// to handle generic UI interactions 

// gets loading ajax
var loading = null

$.fn.delay = function(time, callback){
jQuery.fx.step.delay = function(){};
return this.animate({delay:1}, time, callback);
}

$(document).ready(function() {
	
   // adding pause on effects - use like $("#mainImage").pause(5000).fadeOut();
   $.fn.pause = function(duration) {
     $(this).animate({ dummy: 1 }, duration);
     return this;
   };

// desactivar links nos menus
	$('A.inactive').live('click', function(ev, ui) {
		ev.preventDefault()
	})

// chamar modal para corrigir valores	
	$('A.modalCorrect').live('click', function(ev, ui) {
		ev.preventDefault()
		correctModal()
	})	
		
// verificar se tem IE
	if (isIE()) {
	/*	var cookie = $.cookie("IESUCKS")
		if (!cookie) {
			$.cookie("IESUCKS", "Sim", { expires: 7, path: '/'});
			IEwarningModal()
		}
		*/
	}

// duplicar linhas na edição de campos
	$('A.duplicateRow').live('click', function(ev, ui) {
		ev.preventDefault();
		var row = $(this).parents("tr:first")
		row.clone().insertAfter(row).slideDown(500);
	})
	
	// duplicar linhas na edição de campos
	$('A.removeRow').live('click', function(ev, ui) {
		ev.preventDefault();
		var row = $(this).parents("tr:first")
		row.remove();
	})
	
// menus deslizáveis
	$("#main-menu UL LI").hover(function(e) {
		var div = $(this).children("DIV.main-nav-submenu")
		div.hoverFlow(e.type, { 'height': 'show' }, 'fast');
		}, function(e) {
		var div = $(this).children("DIV.main-nav-submenu")
		div.hoverFlow(e.type, {'height': 'hide'}, 'fast');
	});
			
// popup video
	$('A.fp-watch-video').live('click', function(ev, ui) {
		ev.preventDefault();
		video_html = $(this).attr("VIDEO_HTML")
		target_div = $(this).attr("TARGET_DIV")
		$("#"+target_div).html(Url.decode(video_html))
		$("#"+target_div+"-div").show().attr("display","block")
	})
	
// link de esconder video 
	$('A.minimize-video').live('click', function(ev, ui) {
		ev.preventDefault();
		$("#fp-fixed-video-screen-div").hide()
	})
	
// fixar a div do vídeo
	$(window).scroll(function() {
		var counter = $(window).scrollTop()
		var video_div = $("#fp-fixed-video-screen-div")
		if (counter > 280) {
			video_div.css("top", "20px");
		} else {
			video_div.css("top", (280-counter)+ "px");
		}
   })
 	
// fazer com que os botões só apareçam no hover 
	$('.carrossel-div').live("mouseenter", function(ev, ui) {
		$(this).find(".jcarousel-prev").css("display","block")
		$(this).find(".jcarousel-next").css("display","block")
	});
	
	$('.carrossel-div').live("mouseleave", function(ev, ui) {
		$(this).find(".jcarousel-prev").css("display","none")
		$(this).find(".jcarousel-next").css("display","none")
	});
		
	// marquee
	// tem de ser depois dos baloes, pois estes tb tem marqueeables
	$('.marqueeable').each(function() {
		addMarquee(this)
	});
	
// submenu: carregador ajax
	$(".submenu-link").live("click", function(ev, ui) {
		ev.preventDefault(); 
		submenu_ajax_loader({"this":$(this)})
	});

	// select#epoca change: carregador ajax
	$("select#epoca").live("change", function(ev, ui) {
		ev.preventDefault(); 
		epoca_from_select = $(this).find("option:selected").val()
		
		target_link = $("#main-submenu").find("LI.active").find("A.submenu-link")
	//	target_link.trigger("click")
		submenu_ajax_loader({
			"this":target_link,
			"success_callback_function":change_epocas,
			"success_callback_function_params":{
				"epoca":epoca_from_select
			}
		})
	});

// submenu: alternador de switches (div show / hide)
	$(".submenu-switch").live("click", function(ev, ui) {
		ev.preventDefault(); 
		$(".submenu-switch").parent("LI").removeClass("active")
		$(this).parent("LI").addClass("active")

		target_div= $("#"+$(this).attr("TARGET_DIV"))
		service= $(this).attr("TARGET_SERVICE")

		target_div.find("DIV.tab").hide()
		target_div.find("#"+service).show()
	});

// submenu: alternador de tabs (div show / hide)
	$(".main-submenu-tab-link").live("click", function(ev, ui) {
		ev.preventDefault(); 
 		// Remove the 'active' class from the active tab.
  		$('#main-submenu-tab > .tabs > li.active').removeClass('active');
		// Add the 'active' class to the clicked tab.
		$(this).parent().addClass('active');

 		// Remove the 'tab_contents_active' class from the visible tab contents.
  		$('#main-submenu-tab > .main-tab-content > div.tab_contents_active').removeClass('tab_contents_active');
  		// Add the 'tab_contents_active' class to the associated tab contents.
		var target = $(this).attr('rel')
		$("#"+target).addClass('tab_contents_active');
	});


// Não colocar funções depois deste ponto - estas jcarousel dão um pequeno erro e tapam 
// a leitura de código para a frente

	// fazer carrossel parado para classificação
	$('#carrossel-classificacao').jcarousel({
		  scroll: 1, 
        wrap: 'circular',
		  animation:"fast"
	});

	// fazer carrossel parado para jornada
	$('#carrossel-jornada').jcarousel({
		  scroll: 1, 
		  start: 2,
		  animation:"fast"
	});

	// fazer carrossel parado para calendário
	$('#carrossel-calendario').jcarousel({
		  scroll: 1, 
		  start: 2,
		  animation:"fast"
	});

	// carrossel imagens início
	$('#carrossel-pic-title').jcarousel({
        auto: 8,
		  scroll: 1, 
        wrap: 'circular',
		  animation:'slow'
	});
	
	// pesquisa por nome de jogador
	$(".nome_jogador_autocomplete").autocomplete('/autocomplete/nome_jogador', {
		minChars:2, mustMatch: true, autoFill: true,
		autoSelect: true, multiple: false,
		matchSubset:true, // como o valor seleccionado é depois colocado na caixa
		formatResult:function (row) {return row[1]},
		// como o valor é mostrado nas opções
		formatItem:function (row) {return row[1]}
	})
	// importante para que não faça pesquisa no final
	$(".nome_jogador_autocomplete").unbind("search");

	// pesquisa por nome de clube
	$(".nome_clube_autocomplete").autocomplete('/autocomplete/nome_clube', {
		minChars:2, mustMatch: true, autoFill: true,
		autoSelect: true, multiple: false,
		matchSubset:true, // como o valor seleccionado é depois colocado na caixa
		formatResult:function (row) {return row[1]},
		// como o valor é mostrado nas opções
		formatItem:function (row) {return row[1]}
	})
	// importante para que não faça pesquisa no final
	$(".nome_clube_autocomplete").unbind("search");

	// pesquisa por nome de clube
	$(".nome_arbitro_autocomplete").autocomplete('/autocomplete/nome_arbitro', {
		minChars:2, mustMatch: true, autoFill: true,
		autoSelect: true, multiple: false,
		matchSubset:true, // como o valor seleccionado é depois colocado na caixa
		formatResult:function (row) {return row[1]},
		// como o valor é mostrado nas opções
		formatItem:function (row) {return row[1]}
	})
	// importante para que não faça pesquisa no final
	$(".nome_arbitro_autocomplete").unbind("search");

	// front page: link rápido para página de detalhe
	$(".fast-detalhe-text").live("click", function(ev, ui) {
	//	ev.preventDefault();
		val = $(this).siblings("input").val()
		// substituir o campo href pelo campo do URL mais o valor que obtive do campo
		$(this).attr("href", $(this).attr("url")+val)
		$(this).trigger("click")
	})
	// front page: link rápido para página de detalhe
	$(".fast-detalhe-select").live("click", function(ev, ui) {
	//	ev.preventDefault();
		val = $(this).siblings("select").find("option:selected").val()
		// substituir o campo href pelo campo do URL mais o valor que obtive do campo
		$(this).attr("href", $(this).attr("url")+val)
		$(this).trigger("click")
	})
	
	// colocar um table sorter em todas as tabelas que o exigem
	$(".table-sorter").tablesorter({textExtraction: function(node) {
    if ($(node).attr("value")) {return $(node).attr("value")} else {return $(node).html()}
	}})

}); 

// adiciona marquee
function addMarquee(obj) {
   $(obj).addClass('marqueeable-hide')
    var slide_timer,
    slide = function () {
        obj.scrollLeft += 1;
        if (obj.scrollLeft < obj.scrollWidth) {
            slide_timer = setTimeout(slide, 10);
        }
    };
    obj.onmouseover = obj.onmouseout = function (e) {
        e = e.type === 'mouseover';
        clearTimeout(slide_timer);
        $(obj).toggleClass('marqueeable-hide', !e); 
        if (e) slide();
       else obj.scrollLeft = 0;
    };
}

function change_epocas(options) {
	// change DIVs on document
	$("DIV.epoca-container").html(options["epoca"])
	// change title
	 document.title = document.title.replace(/\d{4}\/\d{4}/, options["epoca"])
}

// tira variável tab do URL
function get_tab() { 
	vars = window.location.search.match(/tab=([^&]+)/)
	console.debug(vars)
	if (vars) return vars[1]
	return false
}
	
// ajax loads
function submenu_ajax_loader(options) { 

	options["this"].parent("LI").siblings().removeClass("active")
	options["this"].parent("LI").addClass("active")
	
	target_div= $("#"+options["this"].attr("TARGET_DIV"))
	id= options["this"].attr("TARGET_ID")
	service= options["this"].attr("TARGET_SERVICE")

	querystring = window.location.search

	url = service+"?"
	if (!(id == null || id == "" || id === undefined || id == "undefined"))
		url += "id="+id

	vars = querystring.match(/(?:competicao|jornada|jogo|lance|clube|arbitro|jogador)=(?:[^&]+)/)
	if (vars) {
		for (i=0; i<vars.length; i++) {
			url += "&"+vars[i]
		}
	}
	
	// epoca é obtida preferencialemente a partir do select. 
	// mas se não há no select, há que buscar no URL (get)
	// se não houver lá, azar.
	epoca = null
	epoca_from_select = options["this"].parents("DIV#main-submenu").find("SELECT#epoca option:selected").val()

	if (!(epoca_from_select == null || epoca_from_select == "" || epoca_from_select === undefined 
	 || epoca_from_select == "undefined")) {
		url += "&epoca="+epoca_from_select
	} else {
		vars = querystring.match(/epoca=[^&]+/)
		if (vars) {
			for (i=0; i<vars.length; i++) {
				url += "&"+vars[i]
			}
		}
	}
	
	if (querystring.match("cache=false")) 
		url += "&cache=false"

	if (loading != null) {
		loading.onreadystatechange = function () {};
		loading.abort()
	}
	
	options["url"] = url
	options["target_div"] = target_div
	
	loading = ajaxMainLoader(options)
}

// funcão de mensagem de erro.
function errorMessageWaitingDiv(response) {
	var res
	if (typeof(response) == "string" && 
	   (response.startsWith("<html>") || response.startsWith("<!DOCTYPE HTML")) ) {
		sourcecode.replace(/<body>(.*?)<\/body>/ig, function(m, g1) {res = g1})
	} else if (response != null && typeof(response) == "object") {
		if (response.status == 503 || response.status == 500) {
			res = response.statusText
		} else if (response.status == 404 ) {
			res = "Página não encontrada."
		} 
	} else {
		
		if (res === "error") {
			res = "Serviço gerou um erro interno. Página indisponível."
		} else {
			res = response
		}
	}
	$(".waiting-div-message").html(errormessage(res))
	$(".waiting-div").show("fast").pause(5000).fadeOut()
}

// função de texto de mensagem de erro
function errormessage(message) {
	return "<div class='waiting-error-message fp-medium-radius'>Erro: "+
	(message ? message : "Sem mais informação.") +"</div>"
}

// função de mensagem de espera
function waitmessage(message) {
	return "<div class='waiting-div-message-wait fp-medium-radius'><img src=\"img/loading.gif\" style=\"vertical-align:middle;\"> "+(message ? message : "Aguarde, por favor...") + "</div>"
}

// esconde o div de mensagem
function hideWaitingDiv() {
	$(".waiting-div").slideUp("slow").hide()
//	$(".waiting-div").hide()

}

// mostra o div de mensagem
function waitMessageBeforeSubmit() {
	$(".waiting-div-message").html(waitmessage())
	$(".waiting-div").slideDown("slow").show()
//	$(".waiting-div").show()
}

function ajaxMainLoader(options) {
	
	options["referrer_url"] = options["url"]
	return ajaxMainLoaderWithReferrer(options)
}

// O URL original é /admin/delete?id?xxx&referrer=XXXX
// eu quero um ajax com esse url, para que o servlet delete saiba 
// onde tem de redireccionar, mas eu quero guardar o referrer original 
// no 'url' do div, para poder reproduzir a tabela de lista se quiser
function ajaxMainLoaderWithReferrer(options) {

	return jQuery.ajax({type:'GET', url:options["url"],
	   contentType:"application/x-www-form-urlencoded",
		beforeSubmit: waitMessageBeforeSubmit(), 
		success: function(response)  {
			hideWaitingDiv()
			options["target_div"].html(response)
			options["target_div"].attr("url", options["referrer_url"])
			if (options["success_callback_function"]) {
				if (options["success_callback_function_params"]) {
					options["success_callback_function"](options["success_callback_function_params"])
				} else {
					options["success_callback_function"]()
				}
			}
		}, 
		error: function(response) {
			errorMessageWaitingDiv(response)
		}
	})
}
	
// utilidades URL
var Url = {
 
	// public method for url encoding
	encode : function (string) {
		return escape(this._utf8_encode(string));
	},
 
	// public method for url decoding
	decode : function (string) {
		return this._utf8_decode(unescape(string));
	},
 
	// private method for UTF-8 encoding
	_utf8_encode : function (string) {
		string = string.replace(/\r\n/g,"\n");
		var utftext = "";
 
		for (var n = 0; n < string.length; n++) {
 
			var c = string.charCodeAt(n);
 
			if (c < 128) {
				utftext += String.fromCharCode(c);
			}
			else if((c > 127) && (c < 2048)) {
				utftext += String.fromCharCode((c >> 6) | 192);
				utftext += String.fromCharCode((c & 63) | 128);
			}
			else {
				utftext += String.fromCharCode((c >> 12) | 224);
				utftext += String.fromCharCode(((c >> 6) & 63) | 128);
				utftext += String.fromCharCode((c & 63) | 128);
			}
 
		}
 
		return utftext;
	},
 
	// private method for UTF-8 decoding
	_utf8_decode : function (utftext) {
		var string = "";
		var i = 0;
		var c = c1 = c2 = 0;
 
		while ( i < utftext.length ) {
 
			c = utftext.charCodeAt(i);
 
			if (c < 128) {
				string += String.fromCharCode(c);
				i++;
			}
			else if((c > 191) && (c < 224)) {
				c2 = utftext.charCodeAt(i+1);
				string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
				i += 2;
			}
			else {
				c2 = utftext.charCodeAt(i+1);
				c3 = utftext.charCodeAt(i+2);
				string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
				i += 3;
			}
 
		}
 
		return string;
	}
 
}

// startsWith
String.prototype.startsWith = function(str)
{return (this.match("^"+str)==str)}


function IEwarningModal() {
	$.modal("<div id='warningmodal' class='fp-modal'>"+
      "<div class='fp-modal-escape'>Carregue no Esc para sair desta janela</div>"+
 		"<div style='text-align:center; font-size:20px; padding:10px;'>Internet Explorer? A sério?!</div>"+
 		"<div style='text-align:center;'>"+
		"<img  src='img/no-ie.png'></div>"+
		"<div style='text-align:justify;font-size:16px; padding:10px;'>"+
"<P>O Internet Explorer 8 não consegue apresentar as páginas do 'Foi Penalti!' tão bem quanto os outros navegadores (<A href='http://www.mozilla.com/firefox/'>Firefox</A>, <a href='http://www.google.com/chrome'>Chrome</A>, <a href='http://www.apple.com/safari/'>Safari</A> e <a href='http://www.opera.com'>Opera</A>). A sério, ficam horríveis, dá-me um aperto no coração ver o meu trabalho ser tão mal-tratado pelo Internet Explorer.</P>"+
"<P>Aceite a minha sugestão, e mude de navegador para ver o 'Foi Penalti!'. Noutros navegadores, você pode  ver os vídeos dos jogos, golos e lances, bem como os balões dos comentadores e tabelas de estatísticas com a dimensão certa.</div>"+
"<DIV class='fp-modal-button'><A ID='OKButton' HREF='#'>OK, entendido. Obrigado pelo aviso.</a></DIV>"+
//"<DIV class='fp-modal-button'><A ID='MaisButton' HREF='/agradecimentos'>Não estou convencido. Como ficam as páginas no IE?</a></DIV>"+
	"</div></div>", {
		onShow: function modalShow(dialog) {
		
			dialog.data.find("#OKButton").click(function(ev) {
				ev.preventDefault();
				$.modal.close();
			});
		},
		overlayCss:{backgroundColor: '#888', cursor: 'wait'},
		minWidth:500
	});
}

function correctModal() {
	$.modal("<div id='correctmodal' class='fp-modal'>"+
      "<div class='fp-modal-escape'>Carregue no Esc para sair desta janela</div>"+
 		"<div style='text-align:center; font-size:20px; padding:10px;'>Corrigir os dados</div>"+
 		"<div style='text-align:justify;font-size:16px; padding:10px;'>"+
"<P>É verdade, não sou perfeito. Diga-me qual é o erro que viu, que eu vou rectificar. Obrigado pela colaboração.</P>"+
"<P><input type='text' id='nome' name='nome' size=40 value='O seu nome'></P>"+
"<P><input type='text' id='email' name='email' size=40 value='O seu e-mail'></P>"+
"<P>És humano? escreve 'sim' <input type='text' id='check' name='check' size=20 value=''></P>"+
"<P><TEXTAREA name='correccao' id='correccao' style='width:350px;height:200px;'>Os seguintes dados estão errados:</TEXTAREA></P></div>"+
"<div id='status' style='text-align:center;margin-bottom:5px'></div>"+
"<DIV class='fp-modal-button'><A ID='OKButton' HREF='#'>OK, enviar.</a></DIV></div>", {
		onShow: function modalShow(dialog) {
		
			dialog.data.find("#OKButton").click(function(ev) {
				ev.preventDefault();
				var nome = dialog.data.find("#nome").val()
				var email = dialog.data.find("#email").val()
				var check = dialog.data.find("#check").val()
				var correccao = dialog.data.find("#correccao").val()
				
				if (check == "sim") {

				jQuery.ajax( {type:"POST", url:'/mail/sendmail',
              contentType:"application/x-www-form-urlencoded",  
            	data:"nome="+Url.encode(nome)+"&email="+Url.encode(email)+
					"&body="+Url.encode(correccao),
              beforeSubmit: dialog.data.find("#status").html(waitmesage()), 
              success: function(response) {
                 // status is 0 for good login, -1 otherwise
                  alert("Mail enviado.")
						$.modal.close();
				  },
				  error: function(response) {
                  alert("Mail não enviado, desculpe pelo sucedido. Use foipenalti@foipenalti.com, por favor.")
						$.modal.close();
              } 
				})
				}
			});
		},
		overlayCss:{backgroundColor: '#888', cursor: 'wait'},
		minWidth:400
	});
}

function isIE()
{
  return /msie/i.test(navigator.userAgent) && !/opera/i.test(navigator.userAgent);
}

function urlencode (str) {
str = escape(str);
return str.replace(/[*+\/@]|%20/g,
function (s) {
switch (s) {
case "*": s = "%2A"; break;
case "+": s = "%2B"; break;
case "/": s = "%2F"; break;
case "@": s = "%40"; break;
case "&": s = "%38"; break;
case "%20": s = "+"; break;
}
return s;
}
);
}