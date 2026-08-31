// Behavioral test for the #1240 login double-submit guard.
//
// Dependency-free: run with `node static/js/tests/login_guard_test.js`.
// Exits 0 on success, 1 on failure. Also wired into the Django suite
// (frontend/tests.py LoginDoubleSubmitGuardTests) when node is available.
//
// The guard is extracted from static/js/sitewide1.js between the
// `#1240-guard-start` / `#1240-guard-end` markers and evaluated against
// minimal document/window/form fakes. The dispatch fake models real DOM
// event propagation for a document-level listener: document capture phase,
// then target listeners, then document bubble phase, honoring
// preventDefault / stopPropagation / stopImmediatePropagation, with the
// browser's default action decided after dispatch completes.

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

function makeEvent(target) {
    return {
        target: target,
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
    const docListeners = { capture: [], bubble: [] };
    const windowListeners = {};
    const timeouts = [];
    let reloads = 0;

    const documentFake = {
        addEventListener(type, fn, capture) {
            assert.strictEqual(type, 'submit', 'guard only listens for submit on document');
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
        addEventListener(type, fn) {
            (windowListeners[type] = windowListeners[type] || []).push(fn);
        },
    };

    vm.runInNewContext(guardSource, {
        document: documentFake,
        window: windowFake,
        URL: URL,
    });

    return {
        // Model a real submit dispatch: document capture listeners, then
        // target listeners, then document bubble listeners. Returns
        // { event, submitted } where `submitted` is the browser's
        // default-action decision made after dispatch.
        dispatchSubmit(form, { targetHandlers = [], docBubbleHandlers = [] } = {}) {
            const event = makeEvent(form);
            const phases = [
                docListeners.capture,
                targetHandlers,
                docListeners.bubble.concat(docBubbleHandlers),
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

    'a LATER handler cancelling the submission releases the lock'() {
        // Round-2 finding 1: sitewide1.js loads first, so other document
        // listeners run after the guard. If one of them preventDefault()s,
        // no POST happens and the lock must not stay stuck.
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION), {
            docBubbleHandlers: [(e) => e.preventDefault()],
        });
        h.flushTimeouts(); // deferred rollback runs
        const retry = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(retry.submitted, true,
            'after a cancelled submission, a real retry must still be allowed');
    },

    'target stopPropagation() cannot bypass lock acquisition'() {
        // Round-2 finding 2: acquisition happens in document capture, which
        // runs before target handlers can stop propagation.
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
        // Round-2 finding 3: preventDefault alone would still let target
        // handlers run side effects (AJAX, form.submit()).
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        let downstreamRan = false;
        const blocked = h.dispatchSubmit(makeForm(LOGIN_ACTION), {
            targetHandlers: [() => { downstreamRan = true; }],
        });
        assert.strictEqual(blocked.submitted, false);
        assert.strictEqual(downstreamRan, false,
            'downstream handlers must not run for a blocked submission');
    },

    'a blocked form gets its button disabled (visible stuck-state)'() {
        // Round-2 finding 4: a fresh lightbox form clicked while locked
        // must not look silently ignorable.
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        h.flushTimeouts();
        const freshForm = makeForm(LOGIN_ACTION);
        h.dispatchSubmit(freshForm);
        assert.strictEqual(freshForm._button.disabled, true,
            'blocked form button must be disabled immediately');
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
        // Round-2 finding 5.
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

    'cancelled submission does not disable the button'() {
        const h = makeHarness();
        const form = makeForm(LOGIN_ACTION);
        h.dispatchSubmit(form, { docBubbleHandlers: [(e) => e.preventDefault()] });
        h.flushTimeouts();
        assert.strictEqual(form._button.disabled, false,
            'no POST happened; the form must stay usable');
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
