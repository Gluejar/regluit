// make a random ungluing definition active onload
var $j = jQuery.noConflict();
$j(document).ready(function() {
	var length = $j(".block-intro-text").length;
	var ran = Math.floor(Math.random()*length)+1;
	$j(".block-intro-text div:nth-child(" + ran + ")").attr('id', 'active');
});

// change the ungluing def onclick
var $j = jQuery.noConflict();
$j(document).delegate(".block-intro-text", "click", function() {
    var length = $j(".block-intro-text").length;
    // :eq is 1-indexed so there is no minus one after this random number
    var ran = Math.floor(Math.random()*length);
    // make sure our next active div is not the current one!
    $j(this).children("#active").siblings(':eq('+ran+')').attr('id', 'foo');
    $j(this).children("#active").removeAttr('id');
    $j(this).children("#foo").attr('id', 'active');
});