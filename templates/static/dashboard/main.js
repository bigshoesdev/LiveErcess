$(document).ready(function() {
	$('[data-toggle="tooltip"]').tooltip(); 
          /*$(".que_type").change(function () {
            alert($(this).val())
             var option = $(this).val();
             if(option=='5'){
                var newdiv=$('<div > </div>')
                   var inputfield = $('<input class="form-control form-control-sm" />');
                   var removefield = $('<button type="button" class="btn btn-light">Remove</button>');
                   var addfield = $('<button type="button" class="btn btn-light">Add</button>');
                   removefield.click(function() {
                          $(this).parent().remove();
                   });
                   ;
                          
                                       newdiv.append(inputfield);
                                       newdiv.append(removefield);
                     addfield.click(function() {
                          $("#inputArea").prepend(newdiv);
                   })
			       $("#inputArea").append(newdiv);
                              //$("#inputArea").append('<div >'+inputfield+removefield+' </div>');
                                       $("#inputArea").append(addfield);
	     }

       });*/



        $('#categ').change( function() {
  		var id= $(this).find('option:selected').attr('id');
		$.ajax({                       // initialize an AJAX request
		        url: '/live/dashboard/ajax/topics',                    
			dataType: 'json',		        
			data: {
		          'id': id
        		},
        		success: function (data) {   
                        		
			  $('#top').find('option').remove();
			  if(data == ''){ $('#top').append('<option value='+0+' selected readonly>' + "No Sub Category"+ '</option>')}
                          else {
				$.each(data, function(index, item) {

					$('#top').append('<option value='+item["pk"]+'>' +item['fields']['topic']+ '</option>')
				});}
        		}
      		});

	});

         $('.type1').click(function(){
		$('.type1').not(this).prop('checked', false);
       });
	$('.type2').click(function(){
		$('.type2').not(this).prop('checked', false);
       });
        //startdate
	// $('#datepicker').datepicker({

	// 		format: 'dd/mm/yyyy',
    //             startDate: new Date()
	// }).on('change', function() {
    //     	$(this).valid();  // triggers the validation test

	// 		    //enddate
	

	// 	});
		
	// 	$('#enddatepicker').datepicker({
	// 		//  weekStart: 1,
	// 			 format: 'dd/mm/yyyy',
	// 			  startDate: new Date()
		  
	// 	  }).on('change', function() {
	// 		  $(this).valid();  // triggers the validation test
	// 	  });

	// //starttime
    // 	$('#timepicker').datetimepicker({
	// 	format: 'LT',		
       
    // 	}).on('change', function() {
    //     	$(this).valid();  // triggers the validation test

    // 	});

	// //endtime
	//  $('#timepicker1').datetimepicker({
    //     	format: 'LT'

	//     }).on('change', function() {
    //     	$(this).valid();  // triggers the validation test
    // 	});

	// //custom-method-to compare start and end date
	// $.validator.addMethod("enddate", function(enddatevalue, element) {
	// 	var startdatevalue = $('#datepicker').val();
    //             var arrsdate = startdatevalue.split('/');
    //             var arredate = enddatevalue.split('/');
	// 	return new Date(arrsdate[2], arrsdate[1], arrsdate[0]) <= new Date(arredate[2],arredate[1],arredate[0]);
	//     }, "End date can not be less than Start Date.");

    //    //custom-method-to compare start and end time for same day event
	// $.validator.addMethod("endtime", function(endtimevalue, element) {
	// 	var startdatevalue = $('#datepicker').val();
	// 	var enddatevalue = $('#enddatepicker').val();
           
	//         if(startdatevalue == enddatevalue){
                        
    //                     var temp = '01/01/1990'
	// 		var starttimevalue = $('#timepicker').val();
    //                     var st = new Date(temp + " " +starttimevalue).getTime();
	// 					var et = new Date(temp + " " +endtimevalue).getTime();
						
                        
    //                     return et > st;
	// 	}
	// 	else{
	// 		return true;
	// 	}
                
	// 	}, "End Time can not be less than Start Time for same day event.");
		
	// 	$.validator.addMethod("web", function(webvalue, element) {
	// 		if(webvalue.length > 8){
	// 			return true;
	// 		}
	// 		else{
	// 			return false;
	// 		}
					
	// 		}, "Enter wesite link including https://");

       /* $(".btn-editor").click(function(){
                //alert('working')
	    var div = document.getElementsByClassName('input-error')[0];

              div.innerHTML= '';
             div.style.display = "none";

            var editorinstance = CKEDITOR.instances['id_description'];
            var htmldata = editorinstance.getData();

    
                  // alert(htmldata);
                   var content = $(htmldata).text();
		//alert(content);
                 content  = content.replace(/[\r\n]/g, '');
                content = content.replace(/\s/g, "") 

	//var re = /^(([^<>()[]\.,;:s@"]+(.[^<>()[]\.,;:s@"]+)*)|(".+"))@(([[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}])|(([a-zA-Z-0-9]+.)+[a-zA-Z]{2,}))$/igm;

              var re_email = /(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))/;
               
             // var re_phn = /[0-9]{9,}/;
              var re_phn = /[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}/im;

              var re_url = /((https?|ftp|smtp):\/\/)?(www.)?[a-z0-9]+(\.[a-z]{2,}){1,3}(#?\/?[a-zA-Z0-9#]+)*\/?(\?[a-zA-Z0-9-_]+=[a-zA-Z0-9-%]+&?)?/;

              var re_ifsc = /[A-Za-z]{4}[0-9]{7}/;
		 if (content.length == 0 ){
			var div = document.getElementsByClassName('input-error')[0];
	                        div.innerHTML = 'This field is required.';


                       		div.style.display = "block";
                                
                         

		    return false;
		}
		if (re_phn.test(content))
		{
			var div = document.getElementsByClassName('input-error')[0];

                        div.innerHTML = 'Please remove email id, contact number, website address and bank details.';
			                       		div.style.display = "block";
		    return false;
		}
               
               
		if (re_email.test(content) || re_url.test(content) || re_ifsc.test(content))
		{
			var div = document.getElementsByClassName('input-error')[0];

                        div.innerHTML = 'Please remove email id, contact number, website address and bank details.';
                       		div.style.display = "block";
		    return false;
		}
               
       });*/
	$(".btn2").click(function(){
		//alert('works')
		form = $("#msform");
		form.validate({
			rules:{
				category_id:{
					required: true,
				}
			},
			highlight: function(element) {
                        // add a class "has_error" to the element
                          $(element).next('div').addClass('has_error');
                        },
                        unhighlight: function(element) {
                        // remove the class "has_error" from the element
                          $(element).next('div').removeClass('has_error');
                        },
			messages:{
				category_id:{
					required: "Please choose from dropdown."
				}
			},
			errorPlacement: function(error, element) {

                          error.appendTo( element.next('div'));
                          element.next('div').show();


                        },
	        });
	});

	// $(".btn111").click(function(){
    //     //	 alert('clicked')
		
	// //	alert(new Date(arrsdate[2], arrsdate[1], arrsdate[0]))
    //    		form = $("#msform11");

    //           form.validate({

		
	// 	rules: {
	// 	  event_name: {
	// 		required: true,
    //                     minlength: 5,
	// 	  },
	// 	  website: {
	// 		required: true,
	// 		web:true,
	// 	  },
  	//        	  sdate: {
	// 		required: true,
	// 	  },
	// 	  edate: {
	// 		required: true,
	// 		enddate: true
	// 	  },
	// 	  start_time: {
	// 		required: true,
	// 	  },
	// 	  end_time: {
	// 		required: true,
    //                     endtime: true,
	// 	  },
	// 	  address_line1: {
	// 		required: true,
	// 	  },
			  
		  
	// 	},
	// 	highlight: function(element) {
    //     		// add a class "has_error" to the element 
    //     		$(element).next('div').addClass('has_error');
   	//  	},
    // 	        unhighlight: function(element) {
    //     		// remove the class "has_error" from the element 
    //     		$(element).next('div').removeClass('has_error');
    // 		},
	// 	messages: {
	// 	  event_name: {
	// 		required: "Please provide name of your event",
    //                     minlength: "Event Name should have atleast 5 characters."
	// 	  },
	// 	  website: {
	// 		required: "Provide website link."
	// 	  },
	// 	sdate: {
	// 		required: "Provide the Start Date of Event",
	// 	  },
	// 	edate: {
	// 		required: "Provide the End Date of Event",
    //                     enddate: "End Date cannot be less than Start Date."
	// 	  },
	// 	start_time: {
	// 		required: "Provide Start Time of the event",
	// 	  },
	// 	end_time: {
	// 		required: "Provide End Time of the event.",
    //                     endtime: "End Time can not be less than Start Time for same day event."
	// 	  },
	// 	address_line1: {
	// 		required: "Provide proper address of the event.",
	// 	  }
		  
				
	// 	},
	// 	errorPlacement: function(error, element) {
    
	// 		error.appendTo( element.next('div'));
	// 		element.next('div').show();

			
    // 		},
	//   });

    //   });

	$(".btn5").click(function(){
        	 alert('clicked')
		
	//	alert(new Date(arrsdate[2], arrsdate[1], arrsdate[0]))
       		form = $("#msform");

              form.validate({

		
		rules: {
		  ticket_name: {
			required: true,
                        //minlength: 5,
		  },
  	       	  start_date: {
			required: true,
		  },
		  end_date: {
			required: true,
			enddate: true
		  },
		  start_time: {
			required: true,
		  },
		  end_time: {
			required: true,
                        endtime: true,
		  },
		  
		  				
		},
		highlight: function(element) {
        		// add a class "has_error" to the element 
        		$(element).next('div').addClass('has_error');
   	 	},
    	        unhighlight: function(element) {
        		// remove the class "has_error" from the element 
        		$(element).next('div').removeClass('has_error');
    		},
		messages: {
		  ticket_name: {
			required: "Please provide name of your event",
                        minlength: "Event Name should have atleast 5 characters."
		  },
		  start_date: {
			required: "Provide the Start Date of Event",
		  },
		  end_date: {
			required: "Provide the End Date of Event",
                        edate: "End Date cannot be less than Start Date."
		  },
		  start_time: {
			required: "Provide Start Time of the event",
		  },
		  end_time: {
			required: "Provide End Time of the event.",
                        endtime: "End Time can not be less than Start Time for same day event."
		  },
		  
				
		},
		errorPlacement: function(error, element) {
    
			error.appendTo( element.next('div'));
			element.next('div').show();

			
    		},
	  });

      });

});
