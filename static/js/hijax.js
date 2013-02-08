// hijack a link with class "hijax" to show its content in a lightbox instead
// allows for ajaxy presentation of things like download links in a way that
// degrades gracefully for non-js users
var $j = jQuery.noConflict();

$j(document).ready(function() {
    $j("#js-page-wrap, #footer").on("click", "a.hijax", function(event) {
        event.preventDefault();
		$j("#lightbox").load($j(this).attr("href") + " #lightbox_content", function() {
		    // centering divs of dynamic width: shockingly hard. make sure lightbox is centered on load.
            var hijaxWidth = $j('#about_expandable').width() + 28;
            var windowWidth = $j(document).width();
            var marginWidth = (windowWidth - hijaxWidth)/2;
            $j('#about_expandable').css({'margin-left': marginWidth});
            
            // position div vertically relative to top of viewport, to ensure visibility
            // regardless of where on the page the user clicked to activate it
            var marginTop = window.pageYOffset;
            $j('#about_expandable').css({'margin-top': marginTop});
		});
		
		if ($j(this).attr("href").substr(-9,8) == "download") {
		    jQuery.getScript('https://platform.readmill.com/send.js');
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
	
	// fade-in normal page elements on collapse
	$j('#about_collapser').on("click", function(){
		$j('#js-topsection, .launch_top, .preview, #main-container, #js-rightcol, #js-header, #js-page-wrap, #footer, #feedback').fadeTo("slow", 1);
        $j('#js-header a').css({"cursor": "pointer"});
		$j('#about_expandable').css({"display": "none"});
	});
	
});