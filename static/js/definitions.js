// expand or collapse the learn more section
	var $j = jQuery.noConflict();
	$j(document).ready(function(){
		$j('#user-block-hide').hide();
		$j('#user-block1 a').click(
			function() {
				$j(this).toggleClass("active");
				$j("#user-block-hide").slideToggle(300);
				$j("#readon").toggleClass("down");
			}
		);
	});
	
// make a random ungluing definition active onload
$j(document).ready(function() {
	var length = $j("#block-intro-text div").length;
	var ran = Math.floor(Math.random()*length)+1;
	$j("#block-intro-text div:nth-child(" + ran + ")").attr('id', 'active');
});

// change the ungluing def onclick
$j(document).delegate("#block-intro-text", "click", function() {
    var length = $j("#block-intro-text div").length;
    // minus one because length includes THIS div and we want the set of its siblings only
    var ran = Math.floor(Math.random()*length)-1;
    // make sure our next active div is not the current one!
    $j(this).children("#active").siblings().eq(ran).attr('id', 'foo');
    $j(this).children("#active").removeAttr('id');
    $j(this).children("#foo").attr('id', 'active');
});