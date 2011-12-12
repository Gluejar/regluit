var $j = jQuery.noConflict();
$j(document).ready(function() {
	if (!$j('#watermark').val()) {
		$j('#watermark').css({"background": "white url('/static/images/google_watermark.gif') no-repeat left center"});
	}
});
