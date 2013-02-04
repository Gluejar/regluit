// hijack a link with class "hijax" to show its content in a lightbox instead
// allows for ajaxy presentation of things like download links in a way that
// degrades gracefully for non-js users
var $j = jQuery.noConflict();

$j(document).ready(function() {
    $j("a.hijax_unglued").click(function(event) {
        event.preventDefault();
		$j("#content-block-content").html('<img src="/static/images/loading.gif">').load($j(this).attr("href") + " #books-go-here");
	});	
});