var $j = jQuery.noConflict();
$j(document).ready(function(){
    $j('#embed').click(function(){
        $j('div#widgetcode').toggle();
    });
    $j('#lightbox').on('click', '#embed2', function(){
        $j('div#widgetcode2').toggle();
    });
});