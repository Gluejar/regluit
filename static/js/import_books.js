jQuery(document).ready(function($) {
  
  // post to form_loc and alert with response
  var post_and_alert = function (form_loc){
      
      return function(bubble,location,params) {
          $.post(form_loc, params, function (data) {
                  $(location+' > div').html(data);
              });
          
          return bubble;
          }
  };

                                   
  $('#load_shelf_form').submit(function(){
      post_and_alert('/goodreads/load_shelf/')(false,'#load_shelf_form',$('#load_shelf_form').serialize());
      return false;
  });                     
  
   $('#librarything_load').submit(function(){
      post_and_alert('/librarything/load/')(false,'#librarything_load',$('#librarything_load').serialize());
      return false;
  });  
  
});