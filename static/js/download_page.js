var $j = jQuery.noConflict();

// must load CSS rather than show/hide jQuery objects; can't trigger an event
// on an element not present on pageload, so binding it via on is useless
if (document.createStyleSheet) {
    // make it work in IE <= 8
    document.createStyleSheet('/static/scss/enhanced_download_ie.css');
}
else {
    $j('<link rel="stylesheet" type="text/css" href="/static/scss/enhanced_download.css" />').appendTo('head'); 
}

// browser has a better sense of DOM changes than jQuery, so user can trigger click element
$j(document).on('click', '.other_instructions', function(e) {
    e.preventDefault();
    var myLink = $j(this);
    classes = myLink.attr('class').split(' ');
    mySelector = classes[0];
    var divSelector = '#' + mySelector + '_div';
    var activeDiv = $j(divSelector);
    activeDiv.show();
    activeDiv.siblings().removeClass('active').hide();
});

$j(document).on('click', '#kindle.authenticated', function() {
    var myDiv = $j(this);
    work_id = myDiv.attr('title');
    myDiv.html('<img src="/static/images/loading.gif">')
    $j.post('/send_to_kindle/' + work_id + '/1/', function(data) {
        myDiv.removeClass('btn_support');
        myDiv.html(data);
        myDiv.removeAttr('id');
        return false;
    });
});