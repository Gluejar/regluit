
	var $j = jQuery.noConflict();
	$j(document).ready(function(){
		// caching the selections to speed up response
		var tabs = $j('#tabs');
        var tabs1 = $j('li.tabs1');
        var tabs2 = $j('li.tabs2');
        var tabs3 = $j('li.tabs3');
        var tabs4 = $j('li.tabs4');
        var tabId1 = $j('#tabs-1');
        var tabId2 = $j('#tabs-2');
        var tabId3 = $j('#tabs-3');
        var tabId4 = $j('#tabs-4');
        var contentBlockContent = $j('#content-block-content');

		tabs1.click(function(){
			tabs.find('div.active').removeClass('active');
			$j(this).addClass('active');
			contentBlockContent.find('div.active').removeClass('active');
			tabId1.addClass('active').show(300);
			tabId2.hide(200);
			tabId3.hide(200);
			tabId4.hide(200);
		});
		tabs2.click(function(){
			tabs.find('div.active').removeClass('active');
			$j(this).addClass('active');
			contentBlockContent.find('div.active').removeClass('active');
			tabId2.addClass('active').show(300);
			tabId1.hide(200);
			tabId3.hide(200);
			tabId4.hide(200);
		});
		tabs3.click(function(){
			tabs.find('div.active').removeClass('active');
			$j(this).addClass('active');
			contentBlockContent.find('div.active').removeClass('active');
			tabId3.addClass('active').show(300);
			tabId2.hide(200);
			tabId1.hide(200);
			tabId4.hide(200);
		});
		tabs4.click(function(){
			tabs.find('div.active').removeClass('active');
			$j(this).addClass('active');
			contentBlockContent.find('div.active').removeClass('active');
			tabId4.addClass('active').show(300);
			tabId2.hide(200);
			tabId1.hide(200);
			tabId3.hide(200);
		});
		$j('.findtheungluers').click(function(){
			tabs.find('div.active').removeClass('active');
			$j('#supporters').addClass('active');
			contentBlockContent.find('div.active').removeClass('active');
			tabId3.addClass('active').show(300);
			tabId2.hide(200);
			tabId1.hide(200);
			tabId4.hide(200);
		});
	});