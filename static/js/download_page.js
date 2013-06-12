var $j = jQuery.noConflict();

// must load CSS rather than show/hide jQuery objects; can't trigger an event
// on an element not present on pageload, so binding it via on is useless
if (document.createStyleSheet) {
    // make it work in IE <= 8
    document.createStyleSheet('/static/css/enhanced_download_ie.css');
}
else {
    $j('<link rel="stylesheet" type="text/css" href="/static/css/enhanced_download.css" />').appendTo('head'); 
}

// browser has a better sense of DOM changes than jQuery, so user can trigger click element
$j(document).on('click', '.other_instructions', function(e) {
    e.preventDefault();
    var myID = $j(this).attr('id');
    var divSelector = '#' + myID + '_div';
    var activeDiv = $j(divSelector);
    activeDiv.show();
    activeDiv.siblings().hide();
});

$j(document).on('click', '#kindle.authenticated', function() {
    classes = $j(this).attr('class').split(' ');
    kindle_ebook_id = classes[0];
    $j.post('/send_to_kindle/' + kindle_ebook_id + '/1/', function(data) {
        $j('#kindle_div').html(data);
        return false;
    });
});