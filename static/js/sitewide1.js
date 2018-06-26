var $j = jQuery.noConflict();

$j(document).ready(function() {
    // hijack a link with class "hijax" to show its content in a lightbox instead
    // allows for ajaxy presentation of things like download links in a way that
    // degrades gracefully for non-js users

   $j("#js-page-wrap, #footer").on("click", "a.hijax", function(event) {
        event.preventDefault();
        var work_page = $j(this).attr("href").split("download")[0];
        var isDownload =$j(this).attr("href").indexOf("download");
        var vars = $j(this).attr("href").split("next=");

	});

	// fade-in normal page elements on collapse
	$j('#about_collapser').on("click", function(){
		$j('#js-topsection, .launch_top, .preview, #main-container, #js-rightcol, #js-header, #js-page-wrap, #footer, #feedback').fadeTo("slow", 1);
        $j('#js-header a').css({"cursor": "pointer"});
		$j('#about_expandable').css({"display": "none"});
	});

    // make drop-down menu happen when they click on their name
    $j('#authenticated').click(function(){
        $j('#user_menu').toggle();
        $j(this).toggleClass('highlight');
        $j('#welcome i').toggleClass('fa-chevron-down');
        $j('#welcome i').toggleClass('fa-chevron-up');
    });
    // but suppress it if they're clicking on the badge link to the notifications page
    $j('#i_haz_notifications_badge').click(function() {
        event.stopPropagation();
    });

    $j('[toggle-header-menu]').click(function () {toggleVisibility('#top-menu')})

    function toggleVisibility(selector) {
        var element = document.querySelector(selector);
        element.style.visibility = element.style.visibility === 'hidden' ? 'visible' : 'hidden';
    }

    // Initialize foundation
    document.querySelectorAll('[data-drilldown]').forEach(element => {
        new Foundation.Drilldown($j(element), {});
    });

    document.querySelectorAll('[data-dropdown-menu]').forEach(element => {
        new Foundation.DropdownMenu($j(element), {});
    });

    document.querySelectorAll('[data-accordion]').forEach(element => {
        console.log(element);
        new Foundation.Accordion($j(element), {'data-multi-expand': true});
    });

});
