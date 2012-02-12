var $j = jQuery.noConflict();

$j('#content-block').ready(setupWishlistControls);

function setupWishlistControls() {

    $j("div.add-wishlist").each(function (index, element) {
        $j(element).click(function() {
            var span = $j(element).find("span");
            var gb_id = span.attr('id')
            if (!gb_id) return;
            
            // give immediate feedback that action is in progress
            newSpan = $j('<span style="font-weight: bold;">Adding...</span>').hide();
            span.replaceWith(newSpan);
            newSpan.show();
            
            // actually perform action
            jQuery.post('/wishlist/', {'googlebooks_id': gb_id}, function(data) {
                newSpan.fadeOut();
                var nextSpan = $j('<span class="on-wishlist">On Wishlist!</span>').hide();
                newSpan.replaceWith(nextSpan);
                nextSpan.fadeIn('fast');
                nextSpan.removeAttr("id");
            });
        });
    });

    $j("div.remove-wishlist").each(function (index, element) {
        $j(element).click(function() {
            var span = $j(element).find("span");
            var work_id = span.attr('id')
            jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
                var book = $j(element).closest('.thewholebook');
                book.fadeOut();
            });
        });
    });

    $j("div.create-account").each(function (index, element) {
        $j(element).click(function() {
            var span = $j(element).find("span");
            var work_url = span.attr('title')
            window.location = "/accounts/login/?next=" + work_url;
        });
    });

	// in panel view on the supporter page we want to remove the entire book listing from view upon wishlist-remove
	// but on the work page, we only want to toggle the add/remove functionality
	// so: slightly different versions ahoy
	// note also that we don't have the Django ORM here so we can't readily get from work.id to googlebooks_id
	// we're going to have to tell /wishlist/ that we're feeding it a different identifier
    $j("div.remove-wishlist-workpage").each(function (index, element) {
        $j(element).click(function() {
            var span = $j(element).find("span");
            var work_id = span.attr('id')
            
            // provide feedback
            var newSpan = $j('<span>Removing...</span>').hide();
            span.replaceWith(newSpan);
            newSpan.show();
            
            // perform action
            jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
                newSpan.parent().fadeOut();
                var newDiv = $j('<div class="add-wishlist-workpage"><span class="'+work_id+'">Add to Wishlist</span></div>').hide();
                newSpan.parent().replaceWith(newDiv);
                newDiv.fadeIn('slow');
            });
        });
    });
}

var $k = jQuery.noConflict();

// can't bind this to document ready because the .add-wishlist-workpage div doesn't exist until remove-wishlist is executed
// need to use delegate and listen for it
// fyi delegate will be deprecated in favor of live() in jquery 1.7 (this was written for 1.6.3)
$k(document).delegate("div.add-wishlist-workpage span", "click", function() {
    var span = $k(this);
    var work_id = span.attr("class");
    if (!work_id || work_id === "on-wishlist") return;

    // give immediate feedback that action is in progress
    newSpan = $j('<span style="font-weight: bold;">Adding...</span>').hide();
    span.replaceWith(newSpan);
    newSpan.show();

    jQuery.post('/wishlist/', {'add_work_id': work_id}, function(data) {
    	newSpan.fadeOut();
        var nextSpan = $k('<span class="on-wishlist">On Wishlist!</span>').hide();
        newSpan.replaceWith(nextSpan);
        nextSpan.fadeIn('slow');
        nextSpan.removeAttr("id");
    });
});


