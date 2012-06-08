var $j = jQuery.noConflict();
$j(document).ready(function(){
	$j('#about_expander').click(function(){
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
