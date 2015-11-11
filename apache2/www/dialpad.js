/*
  POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
  (C)2015  - Norbert Huffschmid - GNU GPL V3 
*/

$(function () {
    $.widget("potsbliz.dialpad", {

        _create: function () {
        	var self = this;

			// add dialpad to DOM
            this._dialpad = $("<div class='dialpad ui-widget-content ui-corner-all'>");
            this._dialpad.append($("<input type='text' id='dp-display'>"))
            for (i = 0; i <= 9; i++) {
                this._dialpad.append($("<div class='dp-button dp-number-button'>" + i + "</div>"))
            }
            this._dialpad.append($("<div class='dp-button dp-number-button'>*</div>"))
            this._dialpad.append($("<div class='dp-button dp-number-button'>#</div>"))
            this._dialpad.append($("<div id='dp-backspace-button' class='dp-button dp-function-button'></div>"))
            this._dialpad.append($("<div id='dp-call-button' class='dp-button dp-function-button'></div>").hide())
            this._dialpad.append($("<div id='dp-hangup-button' class='dp-button dp-function-button'></div>").hide())
            $(this.element).append(this._dialpad);

			self._state = 'UNDEFINED';
			
            $(".dp-number-button").click(function(){
            	// append number key in display
    			$("#dp-display").val($("#dp-display").val() + $(this).text());
				if ((self._state == 'OFFHOOK') || (self._state == 'COLLECTING') || (self._state == 'TALK')) {
					$.ajax({
						type: "POST",
						data: 'digits=' + $(this).text(),
						dataType: "json",
						url: "/dialpad.py/dialed_digits",
					});
				}
			});
			
			$("#dp-backspace-button").click(function(){
            	// remove last number from display
    			$("#dp-display").val($("#dp-display").val().slice(0, -1));
			});

            $("#dp-call-button").click(function(){
            	// go offhook
    			$.ajax({
					url: "/dialpad.py/offhook",
					async: false,
				});
				
				if ($("#dp-display").val().length > 0) {
					$.ajax({
						type: "POST",
						data: 'digits=' + $("#dp-display").val(),
						dataType: "json",
						url: "/dialpad.py/dialed_digits",
					});
				}       		
			});

            $("#dp-hangup-button").click(function(){
    			// go onhook
    			$.ajax({
					url: "/dialpad.py/onhook",
				});
			});

			$("#dp-display").on('input', function(e) {
 				self._filter_display();
			});
            
			$("#dp-display").on('change', function() {
 				self._filter_display();
			});
            
			// read state periodically
			setInterval(function() {
				$.ajax({
					url: "dialpad.py/get_state",
					dataType: "json",
					success: function(data) {
						if (data.State != self._state) {
							//alert('Old state: ' + self._state + ', New state: ' + data.State);
							if ((data.State == 'IDLE') || (data.State == 'RINGING')) {
								$("#dp-call-button").show();
        						$("#dp-hangup-button").hide();
								$("#dp-backspace-button").show();
								$("#dp-display").val('');
							}
							else {
								$("#dp-call-button").hide();
        						$("#dp-hangup-button").show();        		
								$("#dp-backspace-button").hide();
							}
							self._state = data.State;
				    	}
					},
				});
			}, 3000);
        },

        _filter_display: function () {
            digits = $("#dp-display").val();
            $("#dp-display").val(digits.replace(/[^0-9#*]/g, ""));
        },
    });
});
