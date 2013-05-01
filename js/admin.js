$(document).ready(function() {

	// TABS
	$(".admin-tab-link").live("click", function(ev, ui) {
		ev.preventDefault(); 
 		// Remove the 'active' class from the active tab.
		$(this).parents(".admin-tabs").find('li.active').removeClass('active');
		// Add the 'active' class to the clicked tab.
		$(this).parent().addClass('active');

 		// Remove the 'tab_contents_active' class from the visible tab contents.
 		$(this).parents(".admin-tabs").find('div.tab_contents_active')
			.removeClass('tab_contents_active');
  		// Add the 'tab_contents_active' class to the associated tab contents.
		$("#"+$(this).attr('rel')).addClass('tab_contents_active');
	});
	
	// TABLE SORTER
	$(".admin-table").tablesorter({textExtraction: function(node) {
		if ($(node).attr("value")) {return $(node).attr("value")} else {return $(node).html()}}
	});

	// LIST PAGER
	$(".admin-list-pager-link").live("click", function(ev, ui) {
		ev.preventDefault(); 
		ajaxMainLoader({
			"url":$(this).attr("href"),
		 	"target_div":$(this).parents("DIV.tab_contents")
		})
	});

	// LIST FILTER BUTTON
	$(".admin-table-filter-button").live("click", function(ev, ui) {
		ev.preventDefault(); 
		
		// obter filtros
		filter_field = $(this).parents("form").children("#filter_field").find("option:selected").val()
		filter_needle = $(this).parents("form").children("#filter_needle").val()
		
		filter_base_path = $(this).attr("basepath")

		// limpar filtros anteriores do GET
		var query = window.location.search
  		var qmark = ( (query.length == 0 || query.substring(0,1) == "?") ? "?" : "")
  		if (qmark == "?") query = query.substring(1)

  		var vars = new Array()
		var vars2 = []
  		if (query.length > 0) {
			vars = query.split("&");

			for (var i=0;i<vars.length;i++) {
    	  		var pair = vars[i].split("=");
    	  		if (!(pair[0].startsWith("filter_")))
      			vars2.push(vars[i])
    		}
  		}
		vars2.push("filter_field="+filter_field)
 		vars2.push("filter_needle="+filter_needle)
 		
		str_final = qmark+vars2.join("&")

		// obter needle_field e needle_value
		ajaxMainLoader({
			"url":filter_base_path+str_final,
		 	"target_div":$(this).parents("DIV.tab_contents")
		})
	});

	// DELETE SERVLET
	$('.delete').live("click",function(ev, ui) {
		ev.preventDefault(); 
		href_to_delete = $(this).attr("url")
  		var answer = confirm('Tens a certeza?');
  		if (answer == false) {
			return answer
		}
		
		// eu guardo o URL do pedido da última list, na tab-contents.url.
		// posso ir buscar e pedir outra vez, como se fosse um refresh
		// tenho é de o enviar para a servlet delete, que depois faz um 
		// redirect para esse url
		div = $(this).parents("DIV.tab_contents")
		referrer_url = div.attr("url")
		
		url = href_to_delete+"&referrer="+urlencode(referrer_url)
		
		if (url) {
			ajaxMainLoaderWithReferrer({
				"url":url, "target_div":div, "referrer_url":referrer_url
			})
		}
	}); 

	// duplicar linhas na edição de campos
	$('A.duplicate-input-link').live('click', function(ev, ui) {
		ev.preventDefault();
		var target = $(this).attr("what")
		var object = $("."+target)[$("."+target).size()-1]
		$(object).clone().insertAfter(object);
	})
	
	// duplicar linhas na edição de campos
	$('A.remove-input-link').live('click', function(ev, ui) {
		ev.preventDefault();
		var target = $(this).attr("what")
		var object = $("."+target)[$("."+target).size()-1]
		$(object).remove();
	})
	
	// adiciona date picker para data
	$(".datepicker-date" ).AnyTime_picker({ format: "%Y-%m-%d"} );

	// adiciona date picker para datetime
	$(".datepicker-datetime" ).AnyTime_picker({ format: "%Y-%m-%d %H:%i"} );
	
	// a "check all" checkbox that checks or unchecks all checkboxes 
   $(".checkbox-all").live("click", function(ev, ui) {
		if ($(this).attr("checked")) {
      	$(this).parents("TABLE:first").find(
				"input[id$='_checkbox']").attr("checked",true)
		} else  {
    		$(this).parents("TABLE:first").find(
				"input[id$='_checkbox']").attr("checked",false)        
		}
	}); 

	// a "reset-comentadores" checkbox that prefills comnentadores
   $(".reset-comentadores").live("click", function(ev, ui) {
		$("table.tabela-comentadores").each(function() {
			selects = $(this).find(".comentadores")
			selects.eq(0).val(72014) // Jorge Coroado
			selects.eq(2).val(3484938) // Leirós
			selects.eq(1).val(49027) // Pedro Henriques
		})

		$("select[id$='_decisao']").val(1)

	});
	// switch display visibility to sibling DIVs
	$(".toogleDisplay").live("click", function(ev, ui) {
		ev.preventDefault();
		$(this).siblings("DIV").each(function() {
			if ($(this).css("display") != "inline")
				$(this).css("display","inline")
			else 
				$(this).css("display","none")
		})
	})

	// be alert on change, and make the table's only checkbox checked
   $(".aware-change").live("change", function(ev, ui) {
		$(this).closest("TABLE.element").find(
			"input[id$='_checkbox']").attr("checked",true)
	
	}); 
	
	// adicionar pesquisa genérica por jogador
	$(".nome_jogador_autocomplete").autocomplete('/autocomplete/nome_jogador', {
		minChars:2, 
		mustMatch: true, 
		autoFill: true,
		autoSelect: true,
		multiple: false,
		matchSubset:true,
		// como o valor seleccionado é depois colocado na caixa
		formatResult:function (row) {
         return row[1]
		},
		// como o valor é mostrado nas opções
		formatItem:function (row) {
         return row[1]
		}
	})
	// importante para que não faça pesquisa no final
	$(".nome_jogador_autocomplete").unbind("search")
	
});

String.prototype.startsWith = function(str)
{return (this.match("^"+str)==str)}
