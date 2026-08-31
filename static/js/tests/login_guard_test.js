// Behavioral test for the #1240 login double-submit guard.
//
// Dependency-free: run with `node static/js/tests/login_guard_test.js`.
// Exits 0 on success, 1 on failure. Also wired into the Django suite
// (frontend/tests.py LoginDoubleSubmitGuardTests) when node is available.
//
// The guard is extracted from static/js/sitewide1.js between the
// `#1240-guard-start` / `#1240-guard-end` markers and evaluated against
// minimal document/window/form fakes that model DOM event dispatch
// (capture phase, then bubble phase, with preventDefault semantics).

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
        preventDefault() { this.defaultPrevented = true; },
    };
}

function makeButton() {
    return { disabled: false };
}

function makeForm(action) {
    const attrs = { action: action };
    const button = makeButton();
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
    const listeners = { capture: [], bubble: [] };
    const windowListeners = {};
    const timeouts = [];
    let reloads = 0;

    const documentFake = {
        addEventListener(type, fn, capture) {
            assert.strictEqual(type, 'submit', 'guard only listens for submit on document');
            listeners[capture ? 'capture' : 'bubble'].push(fn);
        },
    };
    const windowFake = {
        location: {
            href: 'https://unglue.it/',
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
        // Dispatch like a browser would for a document-level submit:
        // capture listeners first, then bubble listeners. `preCancelled`
        // models some other handler (e.g. an inline onsubmit returning
        // false) having cancelled the event before the guard's bubble
        // listener runs.
        dispatchSubmit(form, { preCancelled = false } = {}) {
            const event = makeEvent(form);
            listeners.capture.forEach((fn) => fn(event));
            if (preCancelled) event.preventDefault();
            listeners.bubble.forEach((fn) => fn(event));
            return event;
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
        const e1 = h.dispatchSubmit(form);
        assert.strictEqual(e1.defaultPrevented, false, 'first submit must go through');
        const e2 = h.dispatchSubmit(form);
        assert.strictEqual(e2.defaultPrevented, true, 'second submit must be blocked');
    },

    'lock is global across distinct login form nodes'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
        const e2 = h.dispatchSubmit(makeForm(LOGIN_ACTION)); // fresh node (e.g. reopened lightbox)
        assert.strictEqual(e2.defaultPrevented, true, 'other login form nodes must be blocked too');
    },

    'a submission cancelled by another handler does not acquire the lock'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION), { preCancelled: true });
        const e2 = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(e2.defaultPrevented, false,
            'a later real submission must still be allowed');
    },

    'unrelated forms are never touched'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION)); // lock held
        const other = h.dispatchSubmit(makeForm('/accounts/register/'));
        assert.strictEqual(other.defaultPrevented, false, 'non-login form must not be blocked');
    },

    'action matching is by pathname, not substring'() {
        const h = makeHarness();
        h.dispatchSubmit(makeForm(LOGIN_ACTION)); // lock held
        const smuggled = h.dispatchSubmit(
            makeForm('/feedback/?page=/accounts/superlogin/'));
        assert.strictEqual(smuggled.defaultPrevented, false,
            'querystring mention of the login path must not match');
        const withNext = h.dispatchSubmit(
            makeForm('/accounts/superlogin/?next=/work/1/'));
        assert.strictEqual(withNext.defaultPrevented, true,
            'login action with querystring must match');
    },

    'absolute-URL action on our origin matches'() {
        const h = makeHarness();
        const e1 = h.dispatchSubmit(makeForm('https://unglue.it/accounts/superlogin/'));
        assert.strictEqual(e1.defaultPrevented, false);
        const e2 = h.dispatchSubmit(makeForm(LOGIN_ACTION));
        assert.strictEqual(e2.defaultPrevented, true, 'lock acquired via absolute action');
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
        h.firePageshow(true);
        assert.strictEqual(h.reloads, 1, 'persisted pageshow with lock held must reload');
    },

    'normal pageshow or no lock does not reload'() {
        const h = makeHarness();
        h.firePageshow(true);   // no login in flight
        h.firePageshow(false);  // normal load
        h.dispatchSubmit(makeForm(LOGIN_ACTION));
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
