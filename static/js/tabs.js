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
        var tabs = $j('.tabs');
        var tabsId = $j('#tabs');
        var tabs1 = $j('.tabs1');
        var tabs2 = $j('.tabs2');
        var tabs3 = $j('.tabs3');
        var contentBlockContent = $j('#content-block-content');
        var tabsDash1 = $j('.tabs-1');
        var tabsDash2 = $j('.tabs-2');
        var tabsDash3 = $j('.tabs-3');
        
        tabs1.click(function(){
            tabs.find('.active').removeClass('active');
            $j('li.tabs1').addClass('active');
            contentBlockContent.find('.active').removeClass('active');
            tabsDash1.addClass('active').show(300);
            tabsDash2.hide(200);
            tabsDash3.hide(200);
            tabsId.removeClass('wantto').removeClass('ungluing').addClass('unglued');
        });
        tabs2.click(function(){
            tabs.find('.active').removeClass('active');
            $j('li.tabs2').addClass('active');
            contentBlockContent.find('.active').removeClass('active');
            tabsDash2.addClass('active').show(300);
            tabsDash1.hide(200);
            tabsDash3.hide(200);
            tabsId.removeClass('unglued').removeClass('wantto').addClass('ungluing');
        });
        tabs3.click(function(){
            tabs.find('.active').removeClass('active');
            $j('li.tabs3').addClass('active');
            contentBlockContent.find('.active').removeClass('active');
            tabsDash3.addClass('active').show(300);
            tabsDash2.hide(200);
            tabsDash1.hide(200);
            tabsId.removeClass('unglued').removeClass('ungluing').addClass('wantto');
            });
        $j('.empty-wishlist span.bounce-search').click(function(){
            $j('div.js-search-inner').effect("bounce", 500, function() {
                $j('div.js-search-inner input[type="text"]').focus();
            });
        });
    });