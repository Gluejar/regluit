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
   
   $('#load_shelf_form').submit(function(){
    // do ajax call to pick up the list of shelves
    
        if ($('#id_goodreads_shelf_name_number').length == 0) {
    
            var params = {};
            $.getJSON('/goodreads/shelves', params, function(json) {
                // say waiting
                $('#goodreads_input').attr('value', 'Loading....');
                var sel = $('<select id="id_goodreads_shelf_name_number" name="goodreads_shelf_name_number"></select>').appendTo('#goodreads_shelves');
                if (json.total_book_count === 1) {
	                $('<option value="' + 'all:' + json.total_book_count + '">' + 'all (' + json.total_book_count +' book)' + '</option>').appendTo(sel);
	            } else {
	                $('<option value="' + 'all:' + json.total_book_count + '">' + 'all (' + json.total_book_count +' books)' + '</option>').appendTo(sel);
	            }
                for (var i = 0; i < json.user_shelves.length; i++) {
                	if (json.user_shelves[i].book_count === 1) {
	                    $('<option value="' + json.user_shelves[i].name + ':' + json.user_shelves[i].book_count + '">' + json.user_shelves[i].name +
    	                     ' (' + json.user_shelves[i].book_count + ' book)' + '</option>').appendTo(sel);
    	            } else {
	                    $('<option value="' + json.user_shelves[i].name + ':' + json.user_shelves[i].book_count + '">' + json.user_shelves[i].name +
    	                     ' (' + json.user_shelves[i].book_count + ' books)' + '</option>').appendTo(sel);
    	            }
                }
                $('#load_gr_shelves_list').attr('id','load_shelf_form');
                $('#goodreads_input').attr('value', 'Add this shelf');
            });
    
        } else {

            post_and_alert('/goodreads/load_shelf/')(false,'#load_shelf_form',$('#load_shelf_form').serialize());            
            
        }
       return false;

    // change the button value
    // change form id to 'load_shelf_form'
   });
  
});