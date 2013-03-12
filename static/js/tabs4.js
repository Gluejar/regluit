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
        tabs.find('.active').removeClass('active');
        $j(this).addClass('active');
        contentBlockContent.find('div.active').removeClass('active');
        tabId1.addClass('active').show(300);
        tabId2.hide(200);
        tabId3.hide(200);
        tabId4.hide(200);
    });
    tabs2.click(function(){
        tabs.find('.active').removeClass('active');
        $j(this).addClass('active');
        contentBlockContent.find('div.active').removeClass('active');
        tabId2.addClass('active').show(300);
        tabId1.hide(200);
        tabId3.hide(200);
        tabId4.hide(200);
    });
    tabs3.click(function(){
        tabs.find('.active').removeClass('active');
        $j(this).addClass('active');
        contentBlockContent.find('div.active').removeClass('active');
        tabId3.addClass('active').show(300);
        tabId2.hide(200);
        tabId1.hide(200);
        tabId4.hide(200);
    });
    tabs4.click(function(){
        tabs.find('.active').removeClass('active');
        $j(this).addClass('active');
        contentBlockContent.find('div.active').removeClass('active');
        tabId4.addClass('active').show(300);
        tabId2.hide(200);
        tabId1.hide(200);
        tabId3.hide(200);
    });
    $j('.findtheungluers').click(function(){
        tabs.find('.active').removeClass('active');
        $j('#supporters').addClass('active');
        contentBlockContent.find('div.active').removeClass('active');
        tabId3.addClass('active').show(300);
        tabId2.hide(200);
        tabId1.hide(200);
        tabId4.hide(200);
    });
    $j('.show_supporter_contact_form').click(function(){
        if ($j(this).parents(".work_supporter_wide").next().html() == ''){
            $j('div.supporter_contact_form').html('').hide();
            $j('input.supporter_contact_form').hide();
            $j(this).parents(".work_supporter_wide").next().html('<br /><textarea name="msg" rows="4" cols="60" \>');
            $j(this).parent().nextUntil('.work_supporter_wide').show();
        } else {
            $j('div.supporter_contact_form').html('');
            $j('input.supporter_contact_form').hide();        
        }
    });
    $j('#contact_form').submit(function(){
        var theTextarea = $j(this).find("textarea")
        var theInput = theTextarea.parent().next();
        var supporter_id = theInput.attr("name").substring(4);
        var msgReq = jQuery.post('/msg/', $j(this).serialize()+'&supporter='+supporter_id)
        .done(function() { 
            theTextarea.parent().prev().find(".info_for_managers").append("<div class='contact_form_result'>Message Sent<br /></div>"); 
            theInput.hide(); 
            theTextarea.hide();
        })
        .fail(function() { 
            theTextarea.parent().prev().find(".info_for_managers").append("<div class='contact_form_result'>Couldn't Send Message<br /></div>"); 
            theInput.hide(); 
            theTextarea.hide();
        });
        
        return false;
    })
    $j('.show_more_edition').click(function(){
        if ($j(this).html() == 'less...') {
        	$j(this).html('more...')
        } else {
        	$j(this).html('less...')
        }
        $j(this).next().toggle();
    });
	var img = $j('#book-detail-img');
	var googimg = $j('#find-google img');
    img.mouseover(function(){
       googimg.css({"background": "#8dc63f"}).animate(
           {backgroundColor: "white"}, 1500
       );
    });
});
