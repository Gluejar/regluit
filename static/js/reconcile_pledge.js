var $j = jQuery.noConflict();
// give pledge box focus
$j(function() {
  $j('#id_preapproval_amount').focus();
});

// if amount in pledge box is too small to qualify for premium, call attention to it
// and disable the input button with a helpful message
// when they fix it, revert to original styling and reactivate button

$j().ready(function() {
	var inputbox = $j('#id_preapproval_amount');
	var submitbutton = $j('#pledgesubmit');
	
	$j('#premiums_list input').on("click", function() {
		amount = $j(this).siblings('span.menu-item-price').html();
		amount = amount.split('$')[1];
		amount = parseInt(amount);
		current = inputbox.val();
		if (current<amount) {
			inputbox.css({'border-color': '#e35351', 'background-color': '#e35351', 'color': 'white'});
			submitbutton.css({'background-color': '#e35351', 'cursor': 'default', 'font-weight': 'normal', 'font-size': '15px'});
			submitbutton.val("You must pledge at least $"+amount+" for that premium");
			submitbutton.attr('disabled', 'disabled');
		} else if (submitbutton.attr('disabled')) {
			inputbox.css({'border-color': '#8dc63f', 'background-color': 'white', 'color': '#3d4e53'});
			submitbutton.css({'background-color': '#8dc63f', 'cursor': 'pointer', 'font-weight': 'bold', 'font-size': '17px'});
			submitbutton.val("Modify Pledge");
			submitbutton.removeAttr('disabled');
		}
	});
	
	inputbox.keyup(function() {
		current = $j(this).val();
		amount = $j('input[type=radio]:checked').siblings('span.menu-item-price').html();
		amount = amount.split('$')[1];
		amount = parseInt(amount);
		current = inputbox.val();
		if (current<amount) {
			inputbox.css({'border-color': '#e35351', 'background-color': '#e35351', 'color': 'white'});
			submitbutton.css({'background-color': '#e35351', 'cursor': 'default', 'font-weight': 'normal', 'font-size': '15px'});
			submitbutton.val("You must pledge at least $"+amount+" for that premium");
			submitbutton.attr('disabled', 'disabled');
		} else if (submitbutton.attr('disabled')) {
			inputbox.css({'border-color': '#8dc63f', 'background-color': 'white', 'color': '#3d4e53'});
			submitbutton.css({'background-color': '#8dc63f', 'cursor': 'pointer', 'font-weight': 'bold', 'font-size': '17px'});
			submitbutton.val("Modify Pledge");
			submitbutton.removeAttr('disabled');
		}
	});
});