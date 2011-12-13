var $j = jQuery.noConflict();

$j(document).ready(function() {

    $j(".add-wishlist").each(function (index, element) {
        $j(element).click(function() {
            var span = $j(element).find("span");
            var gb_id = span.attr('id')
            if (!gb_id) return;
            jQuery.post('/wishlist/', {'googlebooks_id': gb_id}, function(data) {
                span.fadeOut();
                var newSpan = $j('<span class="on-wishlist">On Your Wishlist!</span>').hide();
                span.replaceWith(newSpan);
                newSpan.fadeIn('slow');
                newSpan.removeAttr("id");
            });
        });
    });

    $j(".remove-wishlist").each(function (index, element) {
        $j(element).click(function() {
            var span = $j(element).find("span");
            var work_id = span.attr('id')
            jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
                var book = $j(element).parent();
                book.fadeOut();
            });
        });
    });

    $j(".create-account").each(function (index, element) {
        $j(element).click(function() {
            var span = $j(element).find("span");
            var work_url = span.attr('title')
            window.location = "/accounts/login/?next=" + work_url;
        });
    });

});

