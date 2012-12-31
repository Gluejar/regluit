var $j = jQuery.noConflict();
$j().ready(function() {
  $j(".loader-gif").click(function(event) {
    $j(this).addClass("show-loading");
  });
});