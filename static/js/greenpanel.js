	        $(document).ready(function(){
				  $('.book-list').bind("mouseenter", (function()
				  {
				  		$(this).removeClass('side1').addClass('side2');
						$(this).children('.panelback').removeClass('side2').addClass('side1');
				  }));
				  
				  $('.book-list').bind("mouseleave", (function()
				  {
						$(this).children('.panelback').removeClass('side1').addClass('side2');
				  		$(this).removeClass('side2').addClass('side1');
				  }));
				  
			});
