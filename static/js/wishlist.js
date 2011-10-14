$(document).ready(function() {

    $(".add-wishlist").each(function (index, element) {
        $(element).click(function() {
            var span = $(element).find("span");
            var gb_id = span.attr('id')
            if (!gb_id) return;
            $.post('/wishlist/', {'googlebooks_id': gb_id}, function(data) {
                span.fadeOut();
                var newSpan = $("<span>On Your Wishlist!</span>").hide();
                span.replaceWith(newSpan);
                newSpan.fadeIn();
                newSpan.removeAttr("id");
            });
        });
    });

    $(".remove-wishlist").each(function (index, element) {
        $(element).click(function() {
            var span = $(element).find("span");
            var work_id = span.attr('id')
            $.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
                var book = $(element).parent();
                book.fadeOut();
            });
        });
    });

});

