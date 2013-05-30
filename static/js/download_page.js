var $j = jQuery.noConflict();

$j(document).on('prettifyDownload', function(){
    $j('.buttons').show();
    $j('.instructions div:not(#trythis_div)').hide();
    $j('.instructions h4').hide();
    
    $j('.buttons div').on('click', function() {
        $j(this).removeClass('modify');
        $j(this).siblings().addClass('modify');
        var buttonID = $j(this).children('a').attr('id');
        var divSelector = '#' + buttonID + '_div';
        var activeDiv = $j(divSelector);
        activeDiv.show();
        activeDiv.siblings().hide();
    });
});

// needs to work both when people go straight to /download and when they get there via hijax link
// ergo can't fire on document ready; needs custom trigger
$j(document).trigger('prettifyDownload');
