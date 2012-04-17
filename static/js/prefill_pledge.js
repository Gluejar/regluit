// This autofills the pledge box when users select a premium tier.
var $j = jQuery.noConflict();

$j().ready(function() {
	var inputbox = $j('#id_preapproval_amount');
	
	$j('#premiums_list input').click(function() {
		amount = $j(this).siblings('span.menu-item-price').html();
		amount = amount.split('$')[1]
		inputbox.val(amount);
	});
});