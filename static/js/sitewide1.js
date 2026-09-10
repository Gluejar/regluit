var $j = jQuery.noConflict();

$j(document).ready(function() {
    // hijack a link with class "hijax" to show its content in a lightbox instead
    // allows for ajaxy presentation of things like download links in a way that
    // degrades gracefully for non-js users

   $j("#js-page-wrap, #footer").on("click", "a.hijax", function(event) {
        event.preventDefault();
        var work_page = $j(this).attr("href").split("download")[0];
        var isDownload =$j(this).attr("href").indexOf("download");
        var vars = $j(this).attr("href").split("next=");
        
		$j("#lightbox").load($j(this).attr("href") + " #lightbox_content", function() {
		    // centering divs of dynamic width: shockingly hard. make sure lightbox is centered on load.
            var hijaxWidth = $j('#about_expandable').width() + 28;
            var windowWidth = $j(document).width();
            var marginWidth = (windowWidth - hijaxWidth)/2;
            $j('#about_expandable').css({'margin-left': marginWidth, 'margin-right': marginWidth});
            
            // position div vertically relative to top of viewport, to ensure visibility
            // regardless of where on the page the user clicked to activate it
            var marginTop = window.pageYOffset;
            $j('#about_expandable').css({'margin-top': marginTop});

            if (isDownload !== -1) {
                $j.getScript('/static/js/download_page.js');
                if(typeof(Dropbox) != "undefined"){
                    Dropbox._dropinsjs_loaded=false;
                }
                $j.getScript('https://www.dropbox.com/static/api/2/dropins.js');
                $j.cookie('next', work_page, {path: '/'});
            }
            else {		
                //need to push next cookie for sign-in links
                
                if (vars.length>1){
                    next=vars[1];
                    if(next!='') {
                        next = next.replace(/[\x22\x27\x3c\x3e]/g,'');
                        $j.cookie('next', next, {path: '/'});
                    }
                }
            }
            // fade-out rest of page elements on expand
            $j('#feedback, #js-page-wrap, #footer').css({"opacity": "0.07"});
            $j('#about_expandable').css({'position': 'absolute'});
            $j('#about_expandable').fadeTo("slow", 1);
        
            // if we're on a supporter page, personalize our about box
            // by writing the supporter's name in
            if ($j(location).attr('pathname').slice(0,11) == '/supporter/') {
                var ungluer = $j(location).attr('pathname').slice(11, -1);

                if (ungluer != null) {
                    // span.ungluer doesn't exist until the ajax call so we
                    // can't bind to the DOM on document ready; need to use
                    // the ajaxComplete event
                    $j('#lightbox').ajaxComplete(function() {
                        $j('#lightbox span.ungluer').replaceWith(ungluer);
                    });
                }
            }
		});
	});
	
	// fade-in normal page elements on collapse
	$j('#about_collapser').on("click", function(){
		$j('#js-topsection, .launch_top, .preview, #main-container, #js-rightcol, #js-header, #js-page-wrap, #footer, #feedback').fadeTo("slow", 1);
        $j('#js-header a').css({"cursor": "pointer"});
		$j('#about_expandable').css({"display": "none"});
	});

    // make drop-down menu happen when they click on their name
    $j('#authenticated').click(function(){
        $j('#user_menu').toggle();
        $j(this).toggleClass('highlight');
        $j('#welcome i').toggleClass('fa-chevron-down');
        $j('#welcome i').toggleClass('fa-chevron-up');
    });
    // but suppress it if they're clicking on the badge link to the notifications page
    $j('#i_haz_notifications_badge').click(function() {
        event.stopPropagation();
    });
});

// #1240-guard-start (markers used by the Node behavioral test; keep them)
// Guard the password login form against duplicate submissions (#1240).
//
// Password managers can auto-submit the login form right after autofilling
// it. If the user then clicks "Sign in with Password" themselves, the second
// POST carries the pre-login CSRF token -- Django rotates the CSRF cookie on
// every successful login -- so the user sees a bare 403 page even though the
// first POST already logged them in. First submission wins; any further
// login submission is blocked while it is in flight.
//
// Design notes:
// - Document/window-level delegation is required (not an inline script in
//   login_form.html): the sign-in lightbox is injected via jQuery
//   .load(url + " #lightbox_content"), which strips <script> tags from the
//   loaded fragment.
// - The listener sits on WINDOW in the capture phase -- the earliest point
//   on the propagation path -- so no document/target/ancestor handler can
//   stopPropagation() the event away from the guard.
// - The lock is module-global, not per form node: a page can hold more than
//   one copy of the login form (standalone page + lightbox), and reopening
//   the lightbox creates a fresh node. One login in flight locks them all.
// - FAIL-CLOSED by design: once acquired, the lock is held until navigation
//   or bfcache restore. A hypothetical future handler that cancels (or
//   cancel-and-replaces) a login submission would leave the lock held --
//   a visibly stuck form fixed by reload -- rather than risk releasing it
//   while a POST is in flight, which would recreate the CSRF bug this
//   guards against. (No such handler exists in this codebase today; the
//   synchronous defaultPrevented check below covers anything that cancelled
//   the event before the guard saw it.)
// - A blocked submission is cancelled with preventDefault +
//   stopImmediatePropagation, so downstream submit handlers cannot run side
//   effects for it, and the button that triggered it is disabled so the
//   state is visible.
// - bfcache: a page restored via back/forward still holds the lock and a
//   pre-login CSRF token, so reload it for fresh state.
(function () {
    var LOGIN_PATH = '/accounts/superlogin/';
    var loginSubmitInFlight = false;

    function isLoginForm(node) {
        if (!node || node.nodeName !== 'FORM' || !node.getAttribute) {
            return false;
        }
        var action = node.getAttribute('action') || '';
        try {
            var url = new URL(action, window.location.href);
            return url.origin === window.location.origin &&
                url.pathname === LOGIN_PATH;
        } catch (err) {
            return false;
        }
    }

    // The control that actually triggered the submission when the browser
    // reports it (event.submitter); the form's first submit control as a
    // fallback (implicit Enter-key submission, older engines).
    function buttonFor(event, form) {
        return event.submitter ||
            form.querySelector('input[type=submit], button[type=submit]');
    }

    window.addEventListener('submit', function (event) {
        var form = event.target;
        if (!isLoginForm(form)) {
            return;
        }
        if (event.defaultPrevented) {
            // Cancelled before the guard saw it; no POST will happen.
            return;
        }
        if (loginSubmitInFlight) {
            // A login POST is already pending: cancel this one outright and
            // keep every later handler from acting on it.
            event.preventDefault();
            event.stopImmediatePropagation();
            var blockedButton = buttonFor(event, form);
            if (blockedButton) {
                blockedButton.disabled = true;
            }
            return;
        }
        loginSubmitInFlight = true;
        // Disable the button only after this submission's form data has
        // been captured (a disabled control would be dropped from it);
        // purely visual feedback.
        window.setTimeout(function () {
            var button = buttonFor(event, form);
            if (button) {
                button.disabled = true;
            }
        }, 0);
    }, true);

    window.addEventListener('pageshow', function (event) {
        if (event.persisted && loginSubmitInFlight) {
            window.location.reload();
        }
    });
})();
// #1240-guard-end
