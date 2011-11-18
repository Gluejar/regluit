/* Beware of fadeIn/fadeOut jQuery animations; they add an inline "display: block"
which overrides display: none in the stylesheet.  Sneaky! */
$(document).ready(function(){
    $('#toggle-list').click(function(){
        $('.panelview').addClass("listview").removeClass("panelview");
        $(this).css({opacity: 1});
        $('#toggle-panel').css({opacity: .2});
    });
    $('#toggle-panel').click(function(){
        $('.listview').addClass("panelview").removeClass("listview");
        $(this).css({opacity: 1});
        $('#toggle-list').css({opacity: .2});
    });
});
