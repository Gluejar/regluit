var $j = jQuery.noConflict();

$j().ready(function(){
	var contentblock = $j('#content-block');
	contentblock.on('mouseenter', 'div.book-list.panelview', function() {
		$j(this).children('.panelfront').removeClass('side1').addClass('side2');
		$j(this).children('.panelback').removeClass('side2').addClass('side1');
	});
				  
	contentblock.on('mouseleave', 'div.book-list.panelview', function() {
		$j(this).children('.panelback').removeClass('side1').addClass('side2');
		$j(this).children('.panelfront').removeClass('side2').addClass('side1');
	});			  
});
