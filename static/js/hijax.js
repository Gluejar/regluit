// hijack a link with class "hijax" to show its content in a lightbox instead
// allows for ajaxy presentation of things like download links in a way that
// degrades gracefully for non-js users
var $j = jQuery.noConflict();

$j(document).ready(function() {
    $j("a.hijax").click(function(event) {
        event.preventDefault();
		$j("#lightbox").load( $j(this).attr("href") + " #lightbox_content");
		
		if ($j(this).attr("href").substr(-9,8) == "download") {
		    jQuery.getScript('/static/js/readmill.js');
		}
		
		// fade-out rest of page elements on expand
		$j('#js-topsection').css({"opacity": "0.07"});
		$j('.launch_top').css({"opacity": "0.07"});
		$j('.preview').css({"opacity": "0.07"});
		$j('#main-container').css({"opacity": "0.07"});
		$j('#js-rightcol').css({"opacity": "0.07"});
		$j('#js-header').css({"opacity": "0.07"});
        $j('#js-header a').css({"cursor": "default"});
		$j('#js-page-wrap').css({"opacity": "0.07"});
		$j('#footer').css({"opacity": "0.07"});
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
	$j('#about_collapser').click(function(){
		$j('#js-topsection').fadeTo("slow", 1);
		$j('.launch_top').fadeTo("slow", 1);
		$j('.preview').fadeTo("slow", 1);
		$j('#main-container').fadeTo("slow", 1);
		$j('#js-rightcol').fadeTo("slow", 1);
		$j('#js-header').fadeTo("slow", 1);
        $j('#js-header a').css({"cursor": "pointer"});
		$j('#js-page-wrap').fadeTo("slow", 1);
		$j('#footer').fadeTo("slow", 1);
		$j('#about_expandable').css({"display": "none"});
	});
	
});