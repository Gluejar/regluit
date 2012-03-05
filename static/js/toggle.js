/* 
 * Beware of fadeIn/fadeOut jQuery animations; they add an inline 
 * "display: block" which overrides display: none in the stylesheet. Sneaky! 
 * 
*/

var $j = jQuery.noConflict();

$j(document).ready(function() {
    $j('#toggle-list').click(toggleList);
    $j('#toggle-panel').click(togglePanel);
    if($j.cookie('view')=='panel') {togglePanel();}
});

function toggleList() {
    $j.cookie('view', 'list', {path: '/'});
    $j('div.panelview').addClass("listview").removeClass("panelview");
    $j('#toggle-list').css({opacity: 1});
    $j('#toggle-panel').css({opacity: .2});
}

function togglePanel() {
    $j.cookie('view', 'panel', {path: '/'});
    $j('div.listview').addClass("panelview").removeClass("listview");
    $j('#toggle-panel').css({opacity: 1});
    $j('#toggle-list').css({opacity: .2});
}
