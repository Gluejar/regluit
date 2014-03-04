var $j = jQuery.noConflict();

$j().ready(function() {
	// only do the lookup once, then cache it
	var contentblock = $j('#content-block');
	
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
        	span.html('Faved!').addClass('on-wishlist');
        });}
        else if (id_type=='gb_id'){
            jQuery.post('/wishlist/', { 'googlebooks_id': id_val}, function(data) {
        	span.html('Faved!').addClass('on-wishlist');
        });}
        else {
            span.html('a type error occurred');
        }
        
        // prevent perversities on download page
        if ($j(this).is("a")) {
        	$j(this).removeClass("add-wishlist").addClass("success");
        }
    });
    
    contentblock.on("click", "div.remove-wishlist", function() {
        var span = $j(this).find("span");
        var book = $j(this).closest('.thewholebook');
        var work_id = span.attr('id').substring(1)
        span.html('Removing...');
        jQuery.post('/wishlist/', {'remove_work_id': work_id}, function(data) {
            book.fadeOut();
        });
    });

    contentblock.on("click", "div.create-account", function () {
        var span = $j(this).find("span");
        var work_url = span.attr('title')
        top.location = "/accounts/login/add/?next=" + work_url + "&add=" + work_url;
    });

	// in panel view on the supporter page we want to remove the entire book listing from view upon wishlist-remove
	// but on the work page, we only want to toggle the add/remove functionality
	// so: slightly different versions ahoy
	// note also that we don't have the Django ORM here so we can't readily get from work.id to googlebooks_id
	// we're going to have to tell /wishlist/ that we're feeding it a different identifier
    contentblock.on("click", "div.remove-wishlist-workpage", function () {
        var span = $j(this).find("span");
        var work_id = span.attr('id').substring(1);
            
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
// allows user to re-add on work page after erroneously removing, without page reload
// can't bind this to document ready because the .add-wishlist-workpage div doesn't exist until remove-wishlist is executed
$k(document).on("click", ".add-wishlist-workpage span", function() {
	var span = $k(this);
	var work_id = span.attr("class");
	if (!work_id) return;
	jQuery.post('/wishlist/', {'add_work_id': work_id}, function(data) {
		span.fadeOut();
		var newSpan = $k('<span class="on-wishlist">Faved!</span>').hide();
		span.replaceWith(newSpan);
		newSpan.fadeIn('slow');
		newSpan.removeAttr("id");
	});
});