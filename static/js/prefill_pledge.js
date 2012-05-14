var $j = jQuery.noConflict();
//give pledge box focus
$j(function() {
  $j('#id_preapproval_amount').focus();
});
// This autofills the pledge box when users select a premium tier.
$j().ready(function() {
	var inputbox = $j('#id_preapproval_amount');
	
	$j('#premiums_list input').click(function() {
		amount = $j(this).siblings('span.menu-item-price').html();
		amount = amount.split('$')[1];
		current = parseInt(inputbox.val());
		if (current<parseInt(amount))
		    {inputbox.val(amount);}
	});
});

