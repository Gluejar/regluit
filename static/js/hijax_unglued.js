// hijack a link with class "hijax" to load only the list element
var $j = jQuery.noConflict();

$j(document).ready(function() {
    $j("a.hijax_unglued").click(function(event) {
        event.preventDefault();
		$j("#content-block-content").html('<img src="/static/images/loading.gif">').load($j(this).attr("href") + " #books-go-here", function(){
            $j('#toggle-list').click(toggleList);
            $j('#toggle-panel').click(togglePanel);
            if($j.cookie('view')=='panel') {togglePanel();}
		});
	});	
});