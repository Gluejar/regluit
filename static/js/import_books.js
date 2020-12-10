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
                  
  
   $('#librarything_load').submit(function(){
      post_and_alert('/librarything/load/')(false,'#librarything_load',$('#librarything_load').serialize());
      return false;
  });
   

          
            
        }
       return false;

    // change the button value
    // change form id to 'load_shelf_form'
   });
  
});