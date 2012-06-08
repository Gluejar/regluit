var $j = jQuery.noConflict();
// give pledge box focus
$j(function() {
  $j('#id_preapproval_amount').focus();
});

// if amount in pledge box is too small to qualify for premium, call attention to it
// and disable the input button with a helpful message
// when they fix it, revert to original styling and reactivate button

$j().ready(function() {
	// cache these to speed things up
	var inputbox = $j('#id_preapproval_amount');
	var submitbutton = $j('#pledgesubmit');
	var fakesubmitbutton = $j('#fakepledgesubmit');
	
	var canonicalize = function(amt) {
		// takes an input button from the premiums list
		// finds the premium amount its associated the span class
		// converts to usable integer form and returns
		amt = amt.siblings('span.menu-item-price').html();
		amt = amt.split('$')[1];
		amt = parseInt(amt);
		return amt;
	}
	
	var mayday = function() {
		// highlights pledge box and submit button in alert color
		// disables submit button and overwrites with help text
		inputbox.css({'border-color': '#e35351', 'background-color': '#e35351', 'color': 'white'});
		fakesubmitbutton.val("You must pledge at least $"+amount+" for that premium");
		fakesubmitbutton.show();
		submitbutton.hide();
		submitbutton.attr('disabled', 'disabled');
	}
	
	var allclear = function() {
		// returns pledge box and submit button to conventional colors
		// enables submit button and rewrites with original text
		inputbox.css({'border-color': '#8dc63f', 'background-color': 'white', 'color': '#3d4e53'});
		fakesubmitbutton.hide();
		submitbutton.show();
		submitbutton.removeAttr('disabled');
	}
	
	$j('#premiums_list input').on("click", function() {
		// when user clicks a premium, ensure it is compatible with the pledge box amount
		amount = canonicalize($j(this));
		current = inputbox.val();
		if (current<amount) {
			mayday();
		} else if (submitbutton.attr('disabled')) {
			allclear();
		}
	});
	
	inputbox.keyup(function() {
		// when user changes the pledge box contents, ensure they are compatible
		// with the selected pledge
		current = $j(this).val();
		
		if (current[0] == '$') {
			// remove leading $ to prevent form validation error
			current = current.slice(1);
			$j(this).val(current);
		}
		
		amount = canonicalize($j('input[type=radio]:checked'));
		if (current<amount) {
			mayday();
		} else if (submitbutton.attr('disabled')) {
			allclear();
		}
	});
});