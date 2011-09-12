$(document).ready(function(){
    $('.book_panel_interior').bind("mouseenter", (function() {
        $(this).children('span').show();
    }));
    $('.book_panel_interior').bind("mouseleave", (function() {
        $(this).children('span').hide();
    }));
});
