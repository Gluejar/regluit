var $j = jQuery.noConflict();
$j(document).ready(function(){
    $j('#embed').click(function(){
        $j('div#widgetcode').toggle();
    });
});