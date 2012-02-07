var $j =jQuery.noConflict();
$j(document).ready(function(){
	$j('div.book-list').bind("mouseenter", (function()
	{
		$j(this).children('.panelfront').removeClass('side1').addClass('side2');
		$j(this).children('.panelback').removeClass('side2').addClass('side1');
	}));
				  
	$j('div.book-list').bind("mouseleave", (function()
	{
		$j(this).children('.panelback').removeClass('side1').addClass('side2');
		$j(this).children('.panelfront').removeClass('side2').addClass('side1');
	}));
				  
});
