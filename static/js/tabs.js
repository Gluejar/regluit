    var $j = jQuery.noConflict();
    $j(document).ready(function(){
        $j('#user-block-hide').hide();
        $j('#user-block1 span').click(
            function() {
                $j(this).toggleClass("active");
                $j("#user-block-hide").slideToggle(300);
            }
        );

		// caching selections to speed up response
        var tabs = $j('ul.tabs');
        var tabsId = $j('#tabs');
        var tabs1 = $j('.tabs1');
        var tabs2 = $j('.tabs2');
        var tabs3 = $j('.tabs3');
        var tabsDash1 = $j('.tabs-1');
        var tabsDash2 = $j('.tabs-2');
        var tabsDash3 = $j('.tabs-3');
        var tabsLink1 = $j('li.tabs1');
        var tabsLink2 = $j('li.tabs2');
        var tabsLink3 = $j('li.tabs3');
        var contentBlockContent = $j('#content-block-content');
        
        // on pageload we are showing only the Active tab, not Unglued or Wishlisted
        if (location.hash == "#1" || location.hash == "#2" || location.hash == "#3") {
        	tab = location.hash;
        } else {
        	tab = $j('#locationhash').html();
        }
        
        $j('#test1').html(location.hash).css('color', 'red');
        $j('#test2').html(tab);
        
        if(tab == "#1") {
	        tabsDash2.hide();
    	    tabsDash3.hide();
            tabsLink1.addClass('active');
    	} else if(tab =="#2") {
	        tabsDash1.hide();
    	    tabsDash3.hide();    	
            tabsLink2.addClass('active');
    	} else {
	        tabsDash1.hide();
    	    tabsDash2.hide();
            tabsLink3.addClass('active');
    	}
        
        tabs1.click(function(){
            tabs.find('.active').removeClass('active');
            tabsLink1.addClass('active');
            contentBlockContent.find('.active').removeClass('active');
            tabsDash1.addClass('active').show(300);
            tabsDash2.hide(200);
            tabsDash3.hide(200);
            tabsId.removeClass('wantto').removeClass('ungluing').addClass('unglued');
            location.hash = "#1";
        });
        tabs2.click(function(){
            tabs.find('.active').removeClass('active');
            tabsLink2.addClass('active');
            contentBlockContent.find('.active').removeClass('active');
            tabsDash2.addClass('active').show(300);
            tabsDash1.hide(200);
            tabsDash3.hide(200);
            tabsId.removeClass('unglued').removeClass('wantto').addClass('ungluing');
            location.hash = "#2";
        });
        tabs3.click(function(){
            tabs.find('.active').removeClass('active');
            tabsLink3.addClass('active');
            contentBlockContent.find('.active').removeClass('active');
            tabsDash3.addClass('active').show(300);
            tabsDash2.hide(200);
            tabsDash1.hide(200);
            tabsId.removeClass('unglued').removeClass('ungluing').addClass('wantto');
            location.hash = "#3";
            });
        $j('.empty-wishlist span.bounce-search').click(function(){
            $j('div.js-search-inner').effect("bounce", 500, function() {
                $j('div.js-search-inner input[type="text"]').focus();
            });
        });
    });