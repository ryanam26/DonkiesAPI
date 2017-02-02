function doPopup(popupPath,width,height,scroll,name) {
	//scroll yes/no
	opt = 'width=' + width + ',height=' + height + ',left=150,top=150,scrollbars=' + scroll +  ',status=0,resizable=1'
	window.open(popupPath,name,opt);
}


function showblock(id) { 
	
if (document.getElementById(id).style.display == "none")
   {document.getElementById(id).style.display = "block"}
else 
   {document.getElementById(id).style.display = "none"}
}

//  tr display:block не правильно отображает colspan
//  поэтому tr надо обрабатывать по особому
function showtr(id) { 
	
if (document.getElementById(id).style.display == "none")
   {document.getElementById(id).style.display = "table-row"}
else 
   {document.getElementById(id).style.display = "none"}
}


function showlightme(el){ $(el).lightbox_me(); }

function editfield(model,field,id,value,output){
	//output - element id куда выводим результат
	$('#'+output).html('---');
	$.ajax({
            url: "/ajax/admin/editfield/",
            type: "POST",
            data: {'model': model,'field':field,'id':id,'value':value},
            dataType: "json",
          	
          	success: function(data){
		     document.getElementById(output).innerHTML = 'ок';
		     $('#'+output).css('font-weight','bold');
		     $('#'+output).css('color','#107314');
		    },
		    
		    error: function(data){
		     document.getElementById(output).innerHTML = 'ошибка';
		     $('#'+output).css('font-weight','bold');
		     $('#'+output).css('color','#cc0000');
		      
		    }
	});
}



function delitem(model,id,output){
	if(confirm('Удалить товар id:' + id + '?'))
	{
		$.ajax({
	            url: "/ajax/admin/delitem/",
	            type: "GET",
	            data: {'model': model,'id':id},
	            dataType: "json",
	          	
	          	success: function(data){
			     document.getElementById(output).innerHTML = 'удален';
			     $('#'+output).css('font-weight','bold');
			     $('#'+output).css('color','#107314');
			     $('#deleter'+id).css('display','none');//кнопку удаления прячем
			     
			     
			    },
			    
			    error: function(data){
			     document.getElementById(output).innerHTML = 'ошибка';
			     $('#'+output).css('font-weight','bold');
			     $('#'+output).css('color','#cc0000');
			    }
		}); 	
	}
	else return;
	
	
}


function uploadimage(model,id,inputfile,loading,output,erroroutput){
	var data = new FormData();
	jQuery.each($(inputfile)[0].files, function(i, file) {
	    data.append('file-'+i, file);
	});
	
	$(loading).css('display','inline');
	$(erroroutput).html('');
	$.ajax({
	            url: "/ajax/admin/uploadimage/" + model + "/" + id + "/",
	            type: "POST",
	            data: data,
	            dataType: "json",
	            cache: false,
	    		contentType: false,
	    		processData: false,
	            
	          	success: function(resp){
	          		var er = resp['error'];
	          		if (er) $(erroroutput).html(er);
	          			          		
	          		var filepath = resp['filepath'];
	          		var extention = resp['extention'];
	          		
	          		if (filepath){
	          			
	          			html = '<div style="float:left">';
	          			html+= '<a target="_blank" href="' + filepath + '.' + extention + '">';
	          			html+= '<img src="' + filepath + '_s.' + extention + '" alt="" style="padding:2px;width:100px;" />';
	          			html+= '</a>';
	          			html+= '</div>';
	          			 
	          			$(output).append(html);	
	          		}
	          		
	          		$(loading).css('display','none');
				},
			    
			    error: function(){
	          		$(loading).css('display','none');
				}
		}); 	
}



function searchproducts(value){
	if (value.length<3){
		$('div.search_results').css('display','none');
		return;	
	} 
	
	$.ajax({
            url: "/ajax/admin/searchproducts/",
            type: "GET",
            data: {'value': value},
            dataType: "json",
          	
          	success: function(data){
          	 $('div.search_results').css('display','block');
          	 $('div.search_results').html(data['html']); 
		     
		    }, 
	});
}



