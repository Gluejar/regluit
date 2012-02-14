var $j = jQuery.noConflict();

$j().ready(function() {
	// only do the lookup once, then cache it
	var contentblock = $j('#content-block');
	
    contentblock.on("click", "div.add-wishlist", function () {
        var span = $j(this).find("span");
        var gb_id = span.attr('id')
        if (!gb_id) return;
            
        // give immediate feedback that action is in progress
	    span.html('<b>Adding...</b>');
            
        // actually perform action
        jQuery.post('/wishlist/', {'googlebooks_id': gb_id}, function(data) {
        	span.html('On Wishlist!').addClass('on-wishlist');
        });
    });

    contentblock.on("click", "div.remove-wishlist", function() {
        var span = $j(this).find("span");
        var book = $j(this).closest('.thewholebook');
        var work_id = span.attr('id')
        span.html('Removing...');
        jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
            book.fadeOut();
        });
    });

    contentblock.on("click", "div.create-account", function () {
        var span = $j(this).find("span");
        var work_url = span.attr('title')
        window.location = "/accounts/login/?next=" + work_url;
    });

	// in panel view on the supporter page we want to remove the entire book listing from view upon wishlist-remove
	// but on the work page, we only want to toggle the add/remove functionality
	// so: slightly different versions ahoy
	// note also that we don't have the Django ORM here so we can't readily get from work.id to googlebooks_id
	// we're going to have to tell /wishlist/ that we're feeding it a different identifier
    contentblock.on("click", "div.remove-wishlist-workpage", function () {
        var span = $j(this).find("span");
        var work_id = span.attr('id')
            
        // provide feedback
        span.html('Removing...');
            
        // perform action
        jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
        	var parent = span.parent();
            parent.fadeOut();
            var newDiv = $j('<div class="add-wishlist-workpage"><span class="'+work_id+'">Add to Wishlist</span></div>').hide();
            parent.replaceWith(newDiv);
            newDiv.fadeIn('slow');
        });
    });
});

var $k = jQuery.noConflict();

$k().ready(function() {
	$k("div.book-detail-info").on("click", "div.add-wishlist-workpage span", function() {
    	var span = $k(this);
    	var work_id = span.attr("class");
    	if (!work_id || work_id === "on-wishlist") return;

	    // give immediate feedback that action is in progress
	    span.html('<b>Adding...</b>');

	    jQuery.post('/wishlist/', {'add_work_id': work_id}, function(data) {
        	span.html('<span class="on-wishlist">On Wishlist!</span>');
	    });
	});
});
