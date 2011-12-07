jQuery(document).ready(function() {

    jQuery(".add-wishlist").each(function (index, element) {
        jQuery(element).click(function() {
            var span = jQuery(element).find("span");
            var gb_id = span.attr('id')
            if (!gb_id) return;
            jQuery.post('/wishlist/', {'googlebooks_id': gb_id}, function(data) {
                span.fadeOut();
                var newSpan = jQuery('<span class="on-wishlist">On Your Wishlist!</span>').hide();
                span.replaceWith(newSpan);
                newSpan.fadeIn('slow');
                newSpan.removeAttr("id");
            });
        });
    });

    jQuery(".remove-wishlist").each(function (index, element) {
        jQuery(element).click(function() {
            var span = jQuery(element).find("span");
            var work_id = span.attr('id')
            jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
                var book = jQuery(element).parent();
                book.fadeOut();
            });
        });
    });

    jQuery(".create-account").each(function (index, element) {
        jQuery(element).click(function() {
            var span = jQuery(element).find("span");
            var work_url = span.attr('title')
            window.location = "/accounts/login/?next=" + work_url;
        });
    });

});

