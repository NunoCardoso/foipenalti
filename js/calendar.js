// these are labels for the days of the week
cal_days_labels = ['Dom', '2ªf', '3ªf', '4ªf', '5ªf', '6ªf', 'Sáb'];

// these are human-readable month name labels, in order
cal_months_labels = ['Janeiro', 'Fevereiro', 'Março', 'Abril',
                     'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
                     'Outubro', 'Novembro', 'Dezembro'];
// these are the days of the week for each month, in order
cal_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

cal_current_date = new Date(); 

function Calendar(month, year, jogos) {
  this.month = (isNaN(month) || month == null) ? cal_current_date.getMonth() : month; 
  this.year  = (isNaN(year) || year == null) ? cal_current_date.getFullYear() : year; 
  this.html = '';
  this.jogos = jogos == null ? {} : jogos;
  this.current_month = cal_current_date.getMonth();
  this.current_year = cal_current_date.getFullYear();
  this.current_day = cal_current_date.getDate();
}

Calendar.prototype.generateHTML = function(){

  // get first day of month
  var firstDay = new Date(this.year, this.month, 1);
  var startingDay = firstDay.getDay();
  // find number of days in month
  var monthLength = cal_days_in_month[this.month];
  // compensate for leap year
  if (this.month == 1) { // February only!
    if((this.year % 4 == 0 && this.year % 100 != 0) || this.year % 400 == 0){
      monthLength = 29;
    }
  }

  // do the header
  var monthName = cal_months_labels[this.month]
  var html = '<table class="fp-calendario-mes-table fp-small-radius fp-shadow">';
  html += '<thead><tr><td colspan="7" class="fp-calendario-mes-table-title">'+ monthName + " de " + this.year;
  html += '</td></tr></thead><tbody><tr class="fp-calendario-mes-table-header">';
  for(var i = 0; i <= 6; i++ ){ html += '<td>' + cal_days_labels[i] + '</td>'; }
  html += '</tr><tr>';

  // fill in the days
  var day = 1;
  // this loop is for is weeks (rows)
  for (var i = 0; i < 9; i++) {
    // this loop is for weekdays (cells)
    for (var j = 0; j <= 6; j++) { 
      html += '<td class="fp-calendario-dia">';
      if (day <= monthLength && (i > 0 || j >= startingDay)) {
			
			// hack for current day
			if (day == this.current_day && this.month == this.current_month && this.year == this.current_year) {
				html += "<DIV CLASS='fp-calendario-current-day'>"
			}
			
		  // hack: check for games. if there is, create a div
		 if (jogos[this.year] && jogos[this.year][this.month] && jogos[this.year][this.month][day] ) {
			html += "<DIV title='fp-calendario-day-"+this.year+this.month+day+"'  class='fp-calendario-event fp-micro-radius fp-little-shadow'>" 
        html += day;
		  html += "</DIV>"
			
		// hack for current day
			if (day == this.current_day && this.month == this.current_month && this.year == this.current_year) {
				html += "</DIV>"
			}
			
		  html_balloon = "<DIV ID='fp-calendario-day-"+this.year+this.month+day+"'>"
			for (var ii in jogos[this.year][this.month][day]["jornadas"]) {
				html_balloon += "<P class='marqueeable'><B>"+jogos[this.year][this.month][day]["jornadas"][ii]+"</B></P>"
			}	
			html_balloon += '<DIV class="fp-hr"></DIV>'
			for (var ii in jogos[this.year][this.month][day]["jogos"]) {
				html_balloon += "<P class='marqueeable'>"+jogos[this.year][this.month][day]["jogos"][ii]+"</P>"
			}	
		  $("#main-hidden-div").append($(html_balloon)) 
		
		 } else {
        html += day;
		 }
        day++;
      }
      html += '</td>';
    }
    // stop making rows if we've run out of days
    if (day > monthLength) {
      break;
    } else {
      html += '</tr><tr>';
    }
  }
  html += '</tr></tbody></table>';

  this.html = html;
}

/*$('#example2').bt('Contents of the tip is provided in the .bt() call', {trigger: 'click', positions: 'top'});
*/

Calendar.prototype.getHTML = function() {
  return this.html;
}