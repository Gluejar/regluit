var $j = jQuery.noConflict();
	$j(function(){
		$j('#js-slideshow').slides({
			preload: true,
			preloadImage: '/static/images/landingpage/loading.gif',
			hoverPause: true,
			generateNextPrev: true,
			next: 'next',
			prev: 'prev',
			pagination: true,
			generatePagination: false,
			slideSpeed: 600,
			autoHeight: true
		});
	});
