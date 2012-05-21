var $j = jQuery.noConflict();
$j(document).ready(function(){
	var collapser = document.getElementById("collapser");
	if(collapser) {
    	$j('#expander a').replaceWith('<a href="#"><span>sign up</span></a>');
    }
    $j('#expander').click(function(){
        $j('#js-topsection').css({"opacity": "0.15"});
		$j('.launch_top').css({"opacity": "0.15"});
        $j('#main-container').css({"opacity": "0.15"});
        $j('#js-rightcol').css({"visibility":"hidden"});
        $j('#expandable').css({"position": "absolute", "z-index": "100", "left":"50%", "margin-left": "-115px"}).fadeTo("slow", 1);
    });
    $j('#collapser').click(function(){
        $j('#js-topsection').fadeTo("slow", 1);
        $j('.launch_top').fadeTo("slow", 1);
        $j('#main-container').fadeTo("slow", 1);
        $j('#js-rightcol').css({"visibility":"visible"});
        $j('#expandable').css({"display": "none"});
    });
});
