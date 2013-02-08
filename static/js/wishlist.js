var $j = jQuery.noConflict();

$j().ready(function() {
	// only do the lookup once, then cache it
	var contentblock = $j('#main-container');

    // removing from wishlist on supporter or search page
    contentblock.on("click", "div.remove-wishlist", function() {
        var span = $j(this).find("span");
        var book = $j(this).closest('.thewholebook');
        var work_id = span.attr('id').substring(1)
        span.html('Removing...');
        jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
            book.fadeOut();
        });
    });
    
	// removing from wishlist on work page
    contentblock.on("click", "div.remove-wishlist-workpage", function () {
        var span = $j(this).find("span");
        var work_id = span.attr('id').substring(1);            
        span.html('Removing...');
        jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
        	var parent = span.parent();
            parent.fadeOut();
            var newDiv = $j('<div class="add-wishlist-workpage"><span class="'+work_id+'">Add to Wishlist</span></div>').hide();
            parent.replaceWith(newDiv);
            newDiv.fadeIn('slow');
        });
    });
	
    // re-adding to wishlist after removal on work page
    contentblock.on("click", ".add-wishlist-workpage span", function() {
		var span = $j(this);
		var work_id = span.attr("class");
		if (!work_id) return;
		jQuery.post('/wishlist/', {'add_work_id': work_id}, function(data) {
			span.fadeOut();
			var newSpan = $j('<span class="on-wishlist">On Wishlist!</span>').hide();
			span.replaceWith(newSpan);
			newSpan.fadeIn('slow');
			newSpan.removeAttr("id");
		});
	});
	
	// adding to wishlist when logged in
    contentblock.on("click", ".add-wishlist", function () {
        var span = $j(this).find("span");
        var id_val = span.attr('id').substring(1);
        var id_type = span.attr('class');
        if (!id_val) {span.html('<i>an error occurred.</i>'); return;}

        // give immediate feedback that action is in progress
	    span.html('<b>Adding...</b>');
            
        // actually perform action
        if (id_type=='work_id'){
            jQuery.post('/wishlist/', { 'add_work_id': id_val}, function(data) {
        	span.html('On Wishlist!').addClass('on-wishlist');
        });}
        else if (id_type=='gb_id'){
            jQuery.post('/wishlist/', { 'googlebooks_id': id_val}, function(data) {
        	span.html('On Wishlist!').addClass('on-wishlist');
        });}
        else {
            span.html('a type error occurred');
        }
        
        // prevent perversities on download page
        if ($j(this).is("a")) {
        	$j(this).removeClass("add-wishlist").addClass("success");
        }
    });
    
    // adding to wishlist when not logged in
    contentblock.on("click", "div.create-account", function () {
        var span = $j(this).find("span");
        var work_url = span.attr('title')
        top.location = "/accounts/login/?next=" + work_url;
    });

// needs to work on work page, search page, user page

});