// Behavioral test for the #1240 login double-submit guard.
//
// Dependency-free: run with `node static/js/tests/login_guard_test.js`.
// Exits 0 on success, 1 on failure. Also wired into the Django suite
// (frontend/tests.py LoginDoubleSubmitGuardTests) when node is available.
//
// The guard is extracted from static/js/sitewide1.js between the
// `#1240-guard-start` / `#1240-guard-end` markers and evaluated against
// minimal window/document/form fakes. The dispatch fake models real DOM
// event propagation for a submit event: window capture, document capture,
// target listeners, document bubble, window bubble -- honoring
// preventDefault / stopPropagation / stopImmediatePropagation. (The
// browser's default-action decision happens after dispatch; the guard is
// deliberately fail-closed, so the tests assert lock retention, not
// rollback.)

'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

// ---- extract the guard ----------------------------------------------------

const sitewidePath = path.join(__dirname, '..', 'sitewide1.js');
const source = fs.readFileSync(sitewidePath, 'utf8');
const start = source.indexOf('// #1240-guard-start');
const end = source.indexOf('// #1240-guard-end');
assert.ok(start !== -1 && end > start, 'guard markers present in sitewide1.js');
const guardSource = source.slice(start, end);

// ---- minimal DOM fakes ----------------------------------------------------

function makeEvent(target, submitter) {
    return {
        target: target,
        submitter: submitter || null,
        defaultPrevented: false,
        _stopProp: false,
        _stopImmediate: false,
        preventDefault() { this.defaultPrevented = true; },
        stopPropagation() { this._stopProp = true; },
        stopImmediatePropagation() { this._stopProp = true; this._stopImmediate = true; },
    };
}

function makeForm(action) {
    const attrs = { action: action };
    const button = { disabled: false };
    return {
        nodeName: 'FORM',
        _button: button,
        getAttribute(name) {
            return Object.prototype.hasOwnProperty.call(attrs, name) ? attrs[name] : null;
        },
        setAttribute(name, value) { attrs[name] = String(value); },
        removeAttribute(name) { delete attrs[name]; },
        querySelector() { return button; },
    };
}

function makeHarness() {
    const winListeners = { capture: [], bubble: [] };
    const docListeners = { capture: [], bubble: [] };
    const windowListeners = {};
    const timeouts = [];
    let reloads = 0;

    const documentFake = {
        addEventListener(type, fn, capture) {
            assert.strictEqual(type, 'submit', 'only submit listeners expected on document');
            docListeners[capture ? 'capture' : 'bubble'].push(fn);
        },
    };
    const windowFake = {
        location: {
            href: 'https://unglue.it/',
            origin: 'https://unglue.it',
            reload() { reloads += 1; },
        },
        setTimeout(fn, ms) { timeouts.push(fn); return timeouts.length; },
        addEventListener(type, fn, capture) {
            if (type === 'submit') {
                winListeners[capture ? 'capture' : 'bubble'].push(fn);
                return;
            }
            (windowListeners[type] = windowListeners[type] || []).push(fn);
        },
    };

    vm.runInNewContext(guardSource, {
        document: documentFake,
        window: windowFake,
        URL: URL,
    });

    return {
        // Model a real submit dispatch: window capture, document capture,
        // target, document bubble, window bubble. Returns { event,
        // submitted } where `submitted` reflects the default-action
        // decision (not cancelled).
        dispatchSubmit(form, {
            submitter = null,
            preGuardHandlers = [],   // window-capture listeners registered BEFORE sitewide1.js
            docCaptureHandlers = [],
            targetHandlers = [],
            docBubbleHandlers = [],
        } = {}) {
            const event = makeEvent(form, submitter);
            const phases = [
                preGuardHandlers.concat(winListeners.capture),
                docListeners.capture.concat(docCaptureHandlers),
                targetHandlers,
                docListeners.bubble.concat(docBubbleHandlers),
                winListeners.bubble,
            ];
            outer:
            for (const phase of phases) {
                for (const fn of phase) {
                    fn(event);
                    if (event._stopImmediate) break outer;
                }
                if (event._stopProp) break;
            }
            return { event, submitted: !event.defaultPrevented };
        },
        firePageshow(persisted) {
            (windowListeners.pageshow || []).forEach((fn) => fn({ persisted: persisted }));
        },
        flushTimeouts() {
            while (timeouts.length) timeouts.shift()();
        },
        get reloads() { return reloads; },
    };
}

const LOGIN_ACTION = '/accounts/superlogin/';

// ---- tests ----------------------------------------------------------------

const tests = {
    'first submission is allowed and acquires the lock'() {
        const h = makeHarness();
        const form = makeForm(LOGIN_ACTION);
        const first = h.dispatchSubmit(form);
        assert.strictEqual(first.submitted, true, 'first submit must go through');
        h.flushTimeouts();
        const second = h.dispatchSubmit(form);
        assert.strictEqual(second.submitted, false, 'second submit must be blocked');
    },

    'lock is global across distinct login form nodes'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        // fresh node, e.g. a reopened lightbox
        const second = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(second.submitted, false, 'other login form nodes must be blocked too');
    },

    'fail-closed: a later handler cancelling the submission leaves the lock held'() {
        // Round-3 finding 1: a timer-time defaultPrevented check cannot
        // distinguish "cancelled" from "cancelled and replaced by
        // form.submit()", so the guard deliberately retains the lock.
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION), {
            docBubbleHandlers: [(e) => e.preventDefault()],
        });
        h.flushTimeouts();
        const retry = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(retry.submitted, false,
            'lock must be retained (fail-closed) after a late cancellation');
    },

    'a submission cancelled BEFORE the guard sees it does not acquire the lock'() {
        // An earlier window-capture listener (registered before sitewide1.js
        // loaded) cancels the event; the guard's synchronous defaultPrevented
        // check must skip acquisition, since no POST will happen.
        const h = makeHarness();
        const cancelled = h.dispatchSubmit(makeForm(LOGIN_ACTION), {
            preGuardHandlers: [(e) => e.preventDefault()],
        });
        assert.strictEqual(cancelled.submitted, false);
        h.flushTimeouts();
        const real = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(real.submitted, true,
            'a later real submission must still be allowed');
    },

    'document-capture stopPropagation cannot bypass lock acquisition'() {
        // Round-3 finding 3 analogue: the guard sits on window capture,
        // ahead of document capture, target, and bubble handlers.
        const h = makeHarness();
        const first = h.dispatchSubmit(makeForm(LOGIN_ACTION), {
            docCaptureHandlers: [(e) => e.stopPropagation()],
        });
        assert.strictEqual(first.submitted, true, 'first POST proceeds');
        h.flushTimeouts();
        const second = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(second.submitted, false, 'lock was still acquired');
    },

    'target stopPropagation() cannot bypass lock acquisition'() {
        const h = makeHarness();
        const first = h.dispatchSubmit(makeForm(LOGIN_ACTION), {
            targetHandlers: [(e) => e.stopPropagation()],
        });
        assert.strictEqual(first.submitted, true, 'first POST proceeds');
        h.flushTimeouts();
        const second = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(second.submitted, false, 'lock was still acquired');
    },

    'a blocked submission stops downstream handlers'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        let downstreamRan = false;
        const blocked = h.dispatchSubmit(makeForm(LOGIN_ACTION), {
            docCaptureHandlers: [() => { downstreamRan = true; }],
            targetHandlers: [() => { downstreamRan = true; }],
        });
        assert.strictEqual(blocked.submitted, false);
        assert.strictEqual(downstreamRan, false,
            'downstream handlers must not run for a blocked submission');
    },

    'a blocked form gets its button disabled (visible stuck-state)'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        const freshForm = makeForm(LOGIN_ACTION);
        h.dispatchSubmit(freshForm);
        assert.strictEqual(freshForm._button.disabled, true,
            'blocked form button must be disabled immediately');
    },

    'the actual submitter control is preferred over the first submit button'() {
        // Round-3 finding 5.
        const h = makeHarness();
        const form = makeForm(LOGIN_ACTION);
        const submitter = { disabled: false };
        h.dispatchSubmit(form, { submitter: submitter });
        h.flushTimeouts();
        assert.strictEqual(submitter.disabled, true, 'event.submitter must be disabled');
        assert.strictEqual(form._button.disabled, false,
            'querySelector fallback must not fire when submitter is known');
    },

    'unrelated forms are never touched'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        const other = h.dispatchSubmit(makeForm('/accounts/register/'));
        assert.strictEqual(other.submitted, true, 'non-login form must not be blocked');
    },

    'action matching is by pathname, not substring'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        const smuggled = h.dispatchSubmit(makeForm('/feedback/?page=/accounts/superlogin/'));
        assert.strictEqual(smuggled.submitted, true,
            'querystring mention of the login path must not match');
        const withNext = h.dispatchSubmit(makeForm('/accounts/superlogin/?next=/work/1/'));
        assert.strictEqual(withNext.submitted, false,
            'login action with querystring must match');
    },

    'absolute-URL action on our origin matches'() {
        const h = makeHarness();
        const first = h.dispatchSubmit(makeForm('https://unglue.it/accounts/superlogin/'));
        assert.strictEqual(first.submitted, true);
        h.flushTimeouts();
        const second = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(second.submitted, false, 'lock acquired via absolute action');
    },

    'cross-origin action with the same path is not ours'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        const foreign = h.dispatchSubmit(makeForm('https://evil.example/accounts/superlogin/'));
        assert.strictEqual(foreign.submitted, true,
            'a cross-origin form must not be treated as our login form');
    },

    'submit button is disabled only after form data capture (async)'() {
        const h = makeHarness();
        const form = makeForm(LOGIN_ACTION);
        h.dispatchSubmit(form);
        assert.strictEqual(form._button.disabled, false,
            'button must not be disabled synchronously (it would drop from form data)');
        h.flushTimeouts();
        assert.strictEqual(form._button.disabled, true, 'button disabled as visual feedback');
    },

    'bfcache restore with a login in flight reloads the page'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        h.firePageshow(true);
        assert.strictEqual(h.reloads, 1, 'persisted pageshow with lock held must reload');
    },

    'normal pageshow or no lock does not reload'() {
        const h = makeHarness();
        h.firePageshow(true);   // no login in flight
        h.firePageshow(false);  // normal load
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        h.firePageshow(false);  // normal load with lock held
        assert.strictEqual(h.reloads, 0);
    },
};

let failures = 0;
for (const [name, fn] of Object.entries(tests)) {
    try {
        fn();
        console.log('ok - ' + name);
    } catch (err) {
        failures += 1;
        console.error('FAIL - ' + name + ': ' + err.message);
    }
}
if (failures) {
    console.error(failures + ' test(s) failed');
    process.exit(1);
}
console.log('all ' + Object.keys(tests).length + ' guard tests passed');
