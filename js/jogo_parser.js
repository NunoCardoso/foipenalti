
$(document).ready(function() {

	$("#url_parser").live("click", function(e) {
		e.preventDefault()
		var url = $("#url_parser_url").val()
		
		jQuery.ajax({type:'GET', 
			url:"/task/parse_jogo?url="+urlencode(url),
			contentType:"application/x-www-form-urlencoded",
			beforeSubmit: waitMessageBeforeSubmit(), 
			
			success: function(response)  {
				hideWaitingDiv()	
				if (response["status"] == "OK") {	
					console.debug(response)
					fill_out_jogadores(response["message"])
				} else {
					errorMessageWaitingDiv(response["message"])	
				}
			},
			
			error: function(response) {
		           errorMessageWaitingDiv(response)
		     }
    	})
	})
})

function fill_out_jogadores(info) {
	
	// info tem resultados_clube1, resultados_clube2, arbitro(id), tacticas_clube1, tacticas_clube2
	if ("arbitro" in info) {
		$("#jog_arbitro_id").val(info["arbitro"])
	}
	if ("resultados_clube1" in info) {
		$("#jog_golos_clube1").val(info["resultados_clube1"])
	}
	if ("resultados_clube2" in info) {
		$("#jog_golos_clube2").val(info["resultados_clube2"])
	}
	if ("tacticas_clube1" in info) {
		$("#jog_tactica_clube1").val(info["tacticas_clube1"])
	}
	if ("tacticas_clube1" in info) {
		$("#jog_tactica_clube2").val(info["tacticas_clube1"])
	}
	
			
	if ("jogadores_clube1" in info) {
		fill_out_jogadores_batch(0, info["jogadores_clube1"])
	}
	if ("jogadores_clube2" in info) {
		fill_out_jogadores_batch(14, info["jogadores_clube2"])
	}
}

function fill_out_jogadores_batch(my_count, jogadores_batch) {	
	var count = my_count 
	for (i in jogadores_batch) {
		var jgd_id = i
		// activate the change checkbox
		$("#jjj"+count+"_checkbox").attr("checked", true)
		// select the player
		$("#jjj"+count+"_jogador_id").val(jgd_id)
		// go through all features
		var jgd_info = jogadores_batch[i]
		if (jgd_info) {
			if ("cartao amarelo" in jgd_info) {
				$("#jjj"+count+"_amarelo_minuto").val(jgd_info["cartao amarelo"])
			}
			if ("cartao duplo amarelo" in jgd_info) {
				$("#jjj"+count+"_duplo_amarelo_minuto").val(jgd_info["cartao duplo amarelo"])
			}
			if ("cartao vermelho" in jgd_info) {
				$("#jjj"+count+"_vermelho_minuto").val(jgd_info["cartao vermelho"])
			}
			if ("substituicao_entrada" in jgd_info) {
				$("#jjj"+count+"_substituicao_entrada").val(jgd_info["substituicao_entrada"])
			}
			if ("substituicao_saida" in jgd_info) {
				$("#jjj"+count+"_substituicao_saida").val(jgd_info["substituicao_saida"])			
			}
			if ("golos" in jgd_info) {
				for(i in jgd_info["golos"]) {
					var golo = jgd_info["golos"][i]
					var golos_input = $($("#jjj"+count+"_golos_minutos")[$("#jjj"+count+"_golos_minutos").size()-1])
					golos_input.val(golo["minuto"])
					var golos_add_input_link = golos_input.next(".duplicate-input-link")
					golos_add_input_link.trigger("click")
					// clean up the new one
					$($("#jjj"+count+"_golos_minutos")[$("#jjj"+count+"_golos_minutos").size()-1]).val("")
									
					var tipos_input = $($("#jjj"+count+"_golos_tipos")[$("#jjj"+count+"_golos_tipos").size()-1])
					tipos_input.val(golo["tipo"])
					var tipos_add_input_link = tipos_input.next(".duplicate-input-link")
					tipos_add_input_link.trigger("click")
					// clean up the new one
					$($("#jjj"+count+"_golos_tipos")[$("#jjj"+count+"_golos_minutos").size()-1]).val("")
				}
			}
		}
		count++;
	}
}