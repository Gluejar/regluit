/* Beware of fadeIn/fadeOut jQuery animations; they add an inline "display: block"
which overrides display: none in the stylesheet.  Sneaky! */
var $j = jQuery.noConflict();
$j(document).ready(function(){
    $j('#toggle-list').click(function(){
        $j('.panelview').addClass("listview").removeClass("panelview");
        $j(this).css({opacity: 1});
        $j('#toggle-panel').css({opacity: .2});
    });
    $j('#toggle-panel').click(function(){
        $j('.listview').addClass("panelview").removeClass("listview");
        $j(this).css({opacity: 1});
        $j('#toggle-list').css({opacity: .2});
    });
});
