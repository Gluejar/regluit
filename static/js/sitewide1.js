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
        
		$j("#lightbox").load($j(this).attr("href") + " #lightbox_content", function() {
		    // centering divs of dynamic width: shockingly hard. make sure lightbox is centered on load.
            var hijaxWidth = $j('#about_expandable').width() + 28;
            var windowWidth = $j(document).width();
            var marginWidth = (windowWidth - hijaxWidth)/2;
            $j('#about_expandable').css({'margin-left': marginWidth, 'margin-right': marginWidth});
            
            // position div vertically relative to top of viewport, to ensure visibility
            // regardless of where on the page the user clicked to activate it
            var marginTop = window.pageYOffset;
            $j('#about_expandable').css({'margin-top': marginTop});

            if (isDownload !== -1) {
                $j.getScript('/static/js/download_page.js');
                if(typeof(Dropbox) != "undefined"){
                    Dropbox._dropinsjs_loaded=false;
                }
                $j.getScript('https://www.dropbox.com/static/api/2/dropins.js');
                $j.cookie('next', work_page, {path: '/'});
            }
            else {		
                //need to push next cookie for sign-in links
                
                if (vars.length>1){
                    next=vars[1];
                    if(next!='') {
                        next = next.replace(/[\x22\x27\x3c\x3e]/g,'');
                        $j.cookie('next', next, {path: '/'});
                    }
                }
            }
            // fade-out rest of page elements on expand
            $j('#feedback, #js-page-wrap, #footer').css({"opacity": "0.07"});
            $j('#about_expandable').css({'position': 'absolute'});
            $j('#about_expandable').fadeTo("slow", 1);
        
            // if we're on a supporter page, personalize our about box
            // by writing the supporter's name in
            if ($j(location).attr('pathname').slice(0,11) == '/supporter/') {
                var ungluer = $j(location).attr('pathname').slice(11, -1);

                if (ungluer != null) {
                    // span.ungluer doesn't exist until the ajax call so we
                    // can't bind to the DOM on document ready; need to use
                    // the ajaxComplete event
                    $j('#lightbox').ajaxComplete(function() {
                        $j('#lightbox span.ungluer').replaceWith(ungluer);
                    });
                }
            }
		});
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
});
