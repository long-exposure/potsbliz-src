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
            
            // get current state
			$.ajax({
				url: "dialpad.py/get_state",
				dataType: "json",
				success: function(data) {
			    	self._go_offhook((data.State != 'IDLE') && (data.State != 'RINGING'));
				},
			});
            
            // start polling for state changes
            this._update_state(this);
            
            
            // Event handlers:
            
            $(".dp-number-button").click(function(){
            	// append number key in display
    			$("#dp-display").val($("#dp-display").val() + $(this).text());
            	if (self._offhook){
            		self._dialed_digits($(this).text());
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
				});            		
			});
            
            $("#dp-hangup-button").click(function(){
    			$("#dp-display").val('');
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
        },

        _dialed_digits: function (digits) {
			$.ajax({
				type: "POST",
				data: 'digits=' + digits,
				dataType: "json",
				url: "/dialpad.py/dialed_digits",
			});
        },

        _filter_display: function () {
            digits = $("#dp-display").val();
            $("#dp-display").val(digits.replace(/[^0-9#*]/g, ""));
        },

        _go_offhook: function (flag) {
        	this._offhook = flag;
        	if (flag == true) {
        		$("#dp-call-button").hide();
        		$("#dp-hangup-button").show();        		
        	}
        	else {
        		$("#dp-call-button").show();
        		$("#dp-hangup-button").hide();        		
        	}
        },
        
        _update_state: function (dialpad) {
			$.ajax({
				url: "dialpad.py/get_state",
				dataType: "json",
				success: function(data) {
			    	setTimeout(function() {
    			    	dialpad._go_offhook((data.State != 'IDLE') && (data.State != 'RINGING'));
			    		dialpad._update_state(dialpad);
			    	}, 1000);
				},
			});
		},
    });
});
