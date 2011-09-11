function print_results(results, from_, format, target_div) {
//{'content': [{'click': 1, 'foto': u'img/unknown.gif', 'id': 2103938L, 'nome': u'Ant\xf3nio Ferreira'}], 'header': {'obj': 'arbitro', 'nr': u'15', 'total': 1, 'panel': 'pesquisa'}}
	if (format == "slides") {
		return print_results_slides(results, from_, target_div)
	}
	if (format == "table") {
		return print_results_table(results, from_, target_div)
	}
	$(".marqueeable").each(function() {	addMarquee(this)})  
}

function print_results_table(results, from_, target_div) {
	var html = "<table class='fp-table fp-table-sorter'>"
	if (results["header"]["obj"] == "arbitro") {
		html += "<thead><tr><th>Nome</th></tr></thead><tbody>"
		for (var i in results["content"]) {
			html += print_table_person(results["header"], from_, results["content"][i])
		}
	}
	if (results["header"]["obj"] == "clube") {
		html += "<thead><tr><th>Nome</th></tr></thead><tbody>"
		for (var i in results["content"]) {
			html += print_table_clube(results["header"], from_, results["content"][i])
		}
	}
	if (results["header"]["obj"] == "jogador") {
		html += "<thead><tr><th>Nome</th><th>Numero</th><th>Clube actual</th></tr></thead><tbody>"
		for (var i in results["content"]) {
			html += print_table_jogador(results["header"], from_, results["content"][i])
		}
	}
	if (results["header"]["obj"] == "epoca") {
		html += "<thead><tr><th>Nome</th></tr></thead><tbody>"
		for (var i in results["content"]) {
			html += print_table_epoca(results["header"], from_, results["content"][i])
		}
	}
	if (results["header"]["obj"] == "competicao") {
		html += "<thead><tr><th>Nome</th></tr></thead><tbody>"
		for (var i in results["content"]) {
			html += print_table_competicao(results["header"], from_, results["content"][i])
		}
	}
	if (results["header"]["obj"] == "jogo") {
		html += "<thead><tr><th>Nome</th><th>Data</th><th>Competição</th><th>Jornada</th></tr></thead><tbody>"
		for (var i in results["content"]) {
			html += print_table_jogo(results["header"], from_, results["content"][i])
		}
	}
	if (results["header"]["obj"] == "lance") {
		html += "<thead><tr><th>Nome</th><th>Tipo</th><th>Protagonistas</th><th>Jogo</th><th>Data</th><th>Competição</th><th>Jornada</th></tr></thead><tbody>"
		for (var i in results["content"]) {
			html += print_table_lance(results["header"], from_, results["content"][i])
		}
	}
	html += "</table>"
	target_div.html(html)
	$(".fp-table-sorter").tablesorter({textExtraction: function(node) {
    if ($(node).attr("value")) {return $(node).attr("value")} else {return $(node).html()}
	}})
}

function print_results_slides(results, from_, target_div) {
	var html = ""
	for (var i in results["content"]) {
		if (results["header"]["obj"] == "arbitro") {
			html += print_slide_person(results["header"], from_, results["content"][i])
		}
		if (results["header"]["obj"] == "clube") {
			html += print_slide_clube(results["header"], from_, results["content"][i])
		}
		if (results["header"]["obj"] == "epoca") {
			html += print_slide_epoca(results["header"], from_, results["content"][i])
		}
		if (results["header"]["obj"] == "competicao") {
			html += print_slide_competicao(results["header"], from_, results["content"][i])
		}
		if (results["header"]["obj"] == "jogo") {
			html += print_slide_jogo(results["header"], from_, results["content"][i])
		}
		if (results["header"]["obj"] == "lance") {
			html += print_slide_lance(results["header"], from_, results["content"][i])
		}
		if (results["header"]["obj"] == "jogador") {
			html += print_slide_jogador(results["header"], from_, results["content"][i])
		}
	}
	target_div.html(html)
	$(".marqueeable").each(function() {addMarquee(this)})
}

function print_table_person(header, from_, obj) {
	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	url += '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]
	html = '<TR><TD><A href="'+url+'">'+obj['nome']+'</A></TD></TR>'
	return html
}

function print_table_clube(header, from_, obj) {
	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	url += '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]
	html = '<TR><TD><A href="'+url+'">'+obj['nome']+'</A></TD></TR>'
	return html
}

function print_table_epoca(header, from_, obj) {
	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	url += '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]
	html = '<TR><TD><A href="'+url+'">'+obj['nome']+'</A></TD></TR>'
	return html
}

function print_table_competicao(header, from_, obj) {
	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	url += '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]
	html = '<TR><TD><A href="'+url+'">'+obj['nome']+'</A></TD></TR>'
	return html
}

function print_table_jogador(header, from_, obj) {
	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_

	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]
	html = '<TR><TD><A href="'+url+url2+'">'+obj['nome']+'</A></TD>'

	url3 = '&to=detalhe_clube&click='+obj["click"]+'&id='+obj["clube_id"]
	html += '<TD>'+obj['numero']+'</TD>'
	html += '<TD><A href="'+url+url3+'">'+obj['clube']+'</A></TD></TR>'
	return html
}

function print_table_jogo(header, from_, obj) {
	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_

	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]
	html = '<TR><TD><A href="'+url+url2+'">'+obj['nome']+'</A></TD>'

	html += '<TD>'+obj['data']+'</TD>'

	url3 = '&to=detalhe_competicao&click='+obj["click"]+'&id='+obj["competicao_id"]
	html += '<TD><A href="'+url+url3+'">'+obj['competicao']+'</A></TD>'

	url4 = '&to=detalhe_jornada&click='+obj["click"]+'&id='+obj["jornada_id"]
	html += '<TD><A href="'+url+url4+'">'+obj['jornada']+'</A></TD>'

	html += '</TR>'
	return html
}

function print_table_lance(header, from_, obj) {
	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_

	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]
	html = '<TR><TD><A href="'+url+url2+'">'+obj['nome']+'</A></TD>'

	html += '<TD>'+obj['tipo']+'</A></TD>'
	html += '<TD>'+obj['protagonistas']+'</A></TD>'

	url2_5 = '&to=detalhe_jogo&click='+obj["click"]+'&id='+obj["jogo_id"]
	html += '<TD><A href="'+url+url2_5+'">'+obj['jogo']+'</A></TD>'

	html += '<TD>'+obj['data']+'</TD>'

	url3 = '&to=detalhe_competicao&click='+obj["click"]+'&id='+obj["competicao_id"]
	html += '<TD><A href="'+url+url3+'">'+obj['competicao']+'</A></TD>'

	url4 = '&to=detalhe_jornada&click='+obj["click"]+'&id='+obj["jornada_id"]
	html += '<TD><A href="'+url+url4+'">'+obj['jornada']+'</A></TD>'

	html += '</TR>'
	return html
}

function print_slide_person(header, from_, obj) {

	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	
	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]

	html = '<DIV CLASS="fp-search-result-element-box-small fp-shadow fp-medium-radius">'
	html += '<A CLASS="fp-medium-radius" href="'+url+url2+'">'
	html += '<div CLASS="main-center">'
	html += '<div CLASS="fp-search-result-element-box-img fp-medium-radius">'
	html += '<img src="'+obj['foto']+'"></div>'
	html += '</div><div class="fp-search-result-element-box-description">'
	html += '<div class="fp-search-result-element-box-description-element">'
	html += obj['nome']+'</DIV></div></A></DIV>'
	return html
}

function print_slide_epoca(header, from_, obj) {

	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	
	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]

	html = '<DIV CLASS="fp-search-result-element-box-small fp-shadow fp-medium-radius">'
	html += '<A CLASS="fp-medium-radius" href="'+url+url2+'">'
	html += '<div CLASS="main-center" style="font-size:14px;padding:5px;">'
	html += obj['nome']
	html += '</div></A></DIV>'
	return html
}

function print_slide_competicao(header, from_, obj) {

	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	
	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]

	html = '<DIV CLASS="fp-search-result-element-box-small fp-shadow fp-medium-radius">'
	html += '<A CLASS="fp-medium-radius" href="'+url+url2+'">'
	html += '<div CLASS="main-center">'
	html += '<div CLASS="fp-search-result-element-box-img fp-medium-radius">'
	html += '<img src="'+obj['foto']+'"></div>'
	html += '</div><div class="fp-search-result-element-box-description">'
	html += '<div class="fp-search-result-element-box-description-element">'
	html += obj['nome']+'</DIV></div></A></DIV>'
	return html
}


function print_slide_clube(header, from_, obj) {

	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	
	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]

	html = '<DIV CLASS="fp-search-result-element-box-small fp-shadow fp-medium-radius">'
	html += '<A CLASS="fp-medium-radius" href="'+url+url2+'">'
	html += '<div CLASS="main-center">'
	html += '<div CLASS="fp-search-result-element-box-img fp-medium-radius">'
	html += '<img src="'+obj['foto']+'"></div>'
	html += '</div><div class="fp-search-result-element-box-description">'
	html += '<div class="fp-search-result-element-box-description-element">'
	html += obj['nome']+'</DIV></div></A></DIV>'
	return html
}

function print_slide_jogador(header, from_, obj) {

	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	
	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]

	html = '<DIV CLASS="fp-search-result-element-box-small fp-shadow fp-medium-radius">'
	html += '<A CLASS="fp-medium-radius" href="'+url+url2+'">'
	html += '<div CLASS="main-center">'
	html += '<div CLASS="fp-search-result-element-box-img fp-medium-radius">'
	html += '<img src="'+obj['foto']+'"></div>'
	html += '</div><div class="fp-search-result-element-box-description">'
	html += '<div class="fp-search-result-element-box-description-element">'
	html += obj['nome']+'</DIV></div></A></DIV>'
	return html
}

function print_slide_jogo(header, from_, obj) {

	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	
	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]

	html = '<DIV CLASS="fp-search-result-element-box-small fp-shadow fp-medium-radius">'
	html += '<A CLASS="fp-medium-radius" href="'+url+url2+'">'
	html += '<div CLASS="main-center">'
	html += '<div CLASS="fp-search-result-element-box-img fp-medium-radius">'
	html += '<img src="'+obj['logo1']+'"><img src="'+obj['logo2']+'"></div>'
	html += '</div><div class="fp-search-result-element-box-description">'
	html += '<div class="fp-search-result-element-box-description-element">'+obj['nome']+'</DIV>'
	html += '<div class="fp-search-result-element-box-description-element">'+obj['data']+'</DIV>'
	html += '</div></A></DIV>'
	return html
}

function print_slide_lance(header, from_, obj) {

	url = '/resultado?obj='+header["obj"]+'&panel='+header["panel"]
	url += '&total='+header["total"]+'&nr='+header["nr"]+'&from='+from_
	
	url2 = '&to=detalhe_'+header["obj"]+'&click='+obj["click"]+'&id='+obj["id"]

	html = '<DIV CLASS="fp-search-result-element-box-small fp-shadow fp-medium-radius">'
	html += '<A CLASS="fp-medium-radius" href="'+url+url2+'">'
	html += '<div CLASS="main-center">'
	html += '<div CLASS="fp-search-result-element-box-img fp-medium-radius">'
	html += '<img src="'+obj['logo1']+'"><img src="'+obj['logo2']+'"></div>'
	html += '</div><div class="fp-search-result-element-box-description">'
	html += '<div class="fp-search-result-element-box-description-element"><P class="marqueeable">'+obj['nome']+'</P></DIV>'
	html += '<div class="fp-search-result-element-box-description-element"><P class="marqueeable">'+obj['tipo']+'</P></DIV>'
	html += '<div class="fp-search-result-element-box-description-element"><P class="marqueeable">protagonistas:'+obj['protagonistas']+'</P></DIV>'
	html += '</div></A></DIV>'
	return html
}
