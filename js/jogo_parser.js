
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

	var table_jogadores_clube1 = $("#table_jogadores_clube1")	
	var table_jogadores_clube2 = $("#table_jogadores_clube2")	
	if ("jogadores_clube1" in info) {
		var count = 0 
		for (i in info["jogadores_clube1"]) {
			var jgd_id = i
			// activate the change checkbox
			$("#jjj"+count+"_checkbox").attr("checked", true)
			// select the player
			$("#jjj"+count+"_jogador_id").val(jgd_id)
			// go through all features
			var jgd_info = info["jogadores_clube1"][i]
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
						console.debug(golo)
						var golos_input = $("#jjj"+count+"_golos_minutos").filter(":last")
						console.debug(golos_input)
						golos_input.val(golo["minuto"])
						console.debug(golos_input)
						var golos_add_input_link = golos_input.siblings(".duplicate-input-link")
						golos_add_input_link.trigger("click")
						console.debug($("#jjj"+count+"_golos_minutos"))
						// clean up the new one
					//	$("#jjj"+count+"_golos_minutos").filter(":last").val("")
						console.debug($("#jjj"+count+"_golos_minutos"))
										
						var tipos_input = $("#jjj"+count+"_golos_tipos").filter(":last")
						tipos_input.val(golo["tipo"])
						var tipos_add_input_link = tipos_input.siblings(".duplicate-input-link")
						tipos_add_input_link.trigger("click")
						// clean up the new one
					//	$("#jjj"+count+"_golos_tipos").filter(":last").val("")
					}
				}
			}
			count++;
		}
	}
	
	if ("jogadores_clube2" in info) {
		var count = 14 
		for (i in info["jogadores_clube2"]) {
			var jgd_id = i
			// activate the change checkbox
			$("#jjj"+count+"_checkbox").attr("checked", true)
			// select the player
			$("#jjj"+count+"_jogador_id").val(jgd_id)
			// go through all features
			var jgd_info = info["jogadores_clube1"][i]
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
						var golos_input = $("#jjj"+count+"_golos_minutos").filter(":last")

						golos_input.val(golo["minuto"])
						var golos_add_input_link = golos_input.siblings(".duplicate-input-link")
						golos_add_input_link.trigger("click")
						// clean up the new one
						$("#jjj"+count+"_golos_minutos").filter(":last").val("")
				
						var tipos_input = $("#jjj"+count+"_golos_tipos").filter(":last")
						tipos_input.val(golo["tipo"])
						var tipos_add_input_link = tipos_input.siblings(".duplicate-input-link")
						tipos_add_input_link.trigger("click")
						// clean up the new one
						$("#jjj"+count+"_golos_tipos").filter(":last").val("")
					}
				}
			}
			count++;
		}
	}
}