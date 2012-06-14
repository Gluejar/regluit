var $j = jQuery.noConflict();

$j(document).ready(function(){
	$j('.about_expander').click(function(){
		// decide which about content to show
		var whichbox = $j(this).attr('id');

		// if we're on a supporter page, personalize our about box
		// by writing the supporter's name in
		if ($j(location).attr('pathname').slice(0,11) == '/supporter/') {
		    var ungluer = $j(location).attr('pathname').slice(11, -1);
		}
		
		if (ungluer != null) {
		    $j('#lightbox').load('/static/html/'+whichbox+'.html');
		    
		    // span.ungluer doesn't exist until the ajax call so we
		    // can't bind to the DOM on document ready; need to use
		    // the ajaxComplete event
		    $j('#lightbox').ajaxComplete(function() {
		    	$j('#lightbox span.ungluer').replaceWith(ungluer);
		    });
		} else {
		    $j('#lightbox').load('/static/html/'+whichbox+'.html');
		}
		
		// fade-out (fade-in) rest of page elements on expand (collapse)
		$j('#js-topsection').css({"opacity": "0.07"});
		$j('.launch_top').css({"opacity": "0.07"});
		$j('#main-container').css({"opacity": "0.07"});
		$j('#js-rightcol').css({"opacity": "0.07"});
		$j('#js-header').css({"opacity": "0.07"});
        $j('#js-header a').css({"cursor": "default"});
		$j('#about_expandable').fadeTo("slow", 1);
	});
	$j('#about_collapser').click(function(){
		$j('#js-topsection').fadeTo("slow", 1);
		$j('.launch_top').fadeTo("slow", 1);
		$j('#main-container').fadeTo("slow", 1);
		$j('#js-rightcol').fadeTo("slow", 1);
		$j('#js-header').fadeTo("slow", 1);
        $j('#js-header a').css({"cursor": "pointer"});
		$j('#about_expandable').css({"display": "none"});
	});
});
