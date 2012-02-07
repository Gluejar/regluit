var $j = jQuery.noConflict();
$j(document).ready(function(){
	var highlighter = $j('#highlighter');
	var mainlogin = $j('#mainlogin');
    highlighter.click(function(){
       mainlogin.css({"background": "#8dc63f"}).animate(
           {backgroundColor: "#EDF3F4"}, 1500
       );
    });
});

/* "sign up below" must be "sign up now" if page != home
	must do something logical elsewhere
*/