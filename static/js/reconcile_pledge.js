var $j = jQuery.noConflict();
// give pledge box focus
$j(function() {
  $j('#id_preapproval_amount').focus();
});

$j().ready(function() {
	// cache these to speed things up
	var inputbox = $j('#id_preapproval_amount');
	var submitbutton = $j('#pledgesubmit');
	var fakesubmitbutton = $j('#fakepledgesubmit');
	var anonbox = $j('#anonbox input');
	var ackSection = $j('#ack_section');
	var supporterName = $j('#pass_supporter_name').html();
	var ackName = $j('#id_ack_name').val();
	var ackDedication = $j('#id_ack_dedication').val();
	if(ackDedication == 'None') {
		ackDedication = '';
	}
	var acks = {
		ack_name: ackName,
		ack_dedication: ackDedication
	};
		
	var ackAnon = $j('#id_anonymous').val();

	// we're not letting people submit arbitrary links
	$j('#id_ack_link').attr('disabled', 'disabled');
	
	// take an input button from the premiums list
	// find the premium amount in its associated span class
	// convert to usable integer form and return
	var canonicalize = function(amt) {
		amt = amt.siblings('span.menu-item-price').html();
		amt = amt.split('$')[1];
		amt = parseInt(amt);
		return amt;
	}
	
	// if amount in pledge box is too small to qualify for premium, highlight pledge
	// box and submit button in alert color and disable the pledge input button
	// with a helpful message
	var mayday = function() {
		inputbox.css({'border-color': '#e35351', 'background-color': '#e35351', 'color': 'white'});
		fakesubmitbutton.val("Pledge at least $"+amount+" to claim that premium");
		fakesubmitbutton.show();
		submitbutton.hide();
		submitbutton.attr('disabled', 'disabled');
	}
	
	// when pledge covers premium again, revert to original styling and reactivate button
	var allclear = function() {
		inputbox.css({'border-color': '#8dc63f', 'background-color': 'white', 'color': '#3d4e53'});
		fakesubmitbutton.hide();
		submitbutton.show();
		submitbutton.removeAttr('disabled');
	}
	
	// make acknowledgements input area active
	var activate = function(mySpan) {
		$j('#'+mySpan).removeClass('ack_inactive').addClass('ack_active');
		$j('#'+mySpan+' input').removeAttr('disabled');
		ack = acks[mySpan];
		$j('#id_'+mySpan).val(ack);
	}
	
	// make mandatory premium input area inactive: greyed-out and not modifiable
	var deactivate = function(mySpan) {
		$j('#'+mySpan).removeClass('ack_active').addClass('ack_inactive');
		$j('#'+mySpan+' input[type=text]').val('').attr('disabled', 'disabled');
	}

	// fill mandatory premium link input with supporter page
	var activateLink = function() {
		$j('#ack_link').removeClass('ack_inactive').addClass('ack_active');
	}
	
	// empty mandatory premium link
	var deactivateLink = function() {
		$j('#ack_link').removeClass('ack_active').addClass('ack_inactive');
	}
	
	var anonymizeName = function() {
		deactivate('ack_name');
		$j('#id_ack_name').val('Anonymous');
	}
	
	// selectively highlight/grey out acknowledgements supporter is eligible for
	var rectifyAcknowledgements = function(current) {
		var anon = anonbox.prop("checked");
		if (!current) {
		    current = 0	;
		}
		if (current < 25) {
			deactivate('ack_name');
			deactivateLink();
			deactivate('ack_dedication');
			ackSection.html('');
		} else if (current >= 25 && current < 50) {
			deactivateLink();
			deactivate('ack_dedication');
			if (anon) {
				anonymizeName();
			} else {
				activate('ack_name');
			}
			ackSection.html(' as a Supporter');
		} else if (current >= 50 && current < 100) {
			deactivate('ack_dedication');
			if (anon) {
				anonymizeName();
				deactivateLink();
			} else {
				activate('ack_name');
				activateLink();
			}
			ackSection.html(' as a Benefactor');
		} else if (current >= 100) {
			activate('ack_dedication');
			if (anon) {
				anonymizeName();
				deactivateLink();
			} else {
				activate('ack_name');
				activateLink();
			}
			ackSection.html(' as a Bibliophile');
		}
	}
	
	// initialize the acknowledgements fields. if we've prefilled the pledge info,
	// use that.
	current = inputbox.val();
	if (ackAnon == 'True') {
		anonbox.prop("checked", true);
	}
	rectifyAcknowledgements(current);

	// when user clicks a premium, ensure it is compatible with the pledge box amount
	// if pledge box was empty, assume they wanted value of premium
	$j('#premiums_list input').on("click", function() {
		amount = canonicalize($j(this));
		current = inputbox.val();
		if (current == "" && !isNaN(amount)) {
		    inputbox.val(amount);
		    rectifyAcknowledgements(amount);
		} else if (current<amount) {
			mayday();
		} else if (submitbutton.attr('disabled')) {
			allclear();
		}
	});
	
	// when user changes the pledge box contents, ensure they are compatible
	// with the selected pledge
	inputbox.keyup(function() {
		current = $j(this).val();
		
		if (current[0] == '$') {
			// remove leading $ to prevent form validation error
			current = current.slice(1);
			$j(this).val(current);
		}
		
		try {
			amount = canonicalize($j('input[type=radio]:checked'));
		} catch(error) {
			amount = 0;
		}
		
		if (current<amount && amount !=0) {
			mayday();
		} else if (submitbutton.attr('disabled')) {
			allclear();
		}
		
		rectifyAcknowledgements(current);
	});
	
	// when supporter clicks the anonymity box, change name & link field to
	// display whatever acks page will display: WYSIWYG
	anonbox.change(function() {
		rectifyAcknowledgements(current);
	});
	
	// if supporters enter a name or dedication, keep track of them
	// so they doesn't get thrown away if they decrease & re-increase pledge, or 
	// anonymize and then de-anonymize
	$j('#ack_name input[type=text]').change(function() {
		acks['ack_name'] = $j(this).val();
	});
	$j('#ack_dedication input[type=text]').change(function() {
		acks['ack_dedication'] = $j(this).val();
	});
	
});