/* Beware of fadeIn/fadeOut jQuery animations; they add an inline "display: block"
which overrides display: none in the stylesheet.  Sneaky! */
$(document).ready(function(){
    $('#toggle-list').click(function(){
        $('.panelview').addClass("listview").removeClass("panelview");
    });
    $('#toggle-panel').click(function(){
        $('.listview').addClass("panelview").removeClass("listview");
    });
});