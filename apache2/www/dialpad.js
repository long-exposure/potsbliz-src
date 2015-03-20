$(function () {
    $.widget("potsbliz.dialpad", {

        options: {
            //background_color: "yellow",
        },

        _create: function () {
        	var self = this;
        	
            this._dialpad = $("<div class='dialpad ui-widget-content ui-corner-all'>");
            this._dialpad.append($("<input type='text' id='dp-display'>"))
            for (i = 0; i <= 9; i++) {
                this._dialpad.append($("<div class='dp-button dp-number-button'>" + i + "</div>"))
            }
            this._dialpad.append($("<div class='dp-button dp-number-button'>*</div>"))
            this._dialpad.append($("<div class='dp-button dp-number-button'>#</div>"))
            this._dialpad.append($("<div id='dp-delete-button' class='dp-button'>X</div>"))
            this._dialpad.append($("<div id='dp-call-button' class='dp-button'>C</div>"))
            this._dialpad.append($("<div id='dp-hangup-button' class='dp-button'>H</div>"))

            $(this.element).append(this._dialpad);
            this._update();
            
            this._offhook = false;
            
            $(".dp-number-button").click(function(){
            	// append number key in display
    			$("#dp-display").val($("#dp-display").val() + $(this).text());

            	if (self._offhook){
            		self._dialed_digits($(this).text());
				}
			});
            
            $("#dp-delete-button").click(function(){
            	// remove last number from display
    			$("#dp-display").val($("#dp-display").val().slice(0, -1));
			});
            
            $("#dp-call-button").click(function(){
            	if (!self._offhook) {
	            	// go offhook
	    			$.ajax({
						url: "/dialpad.py/offhook",
						success: function(response) {
							self._offhook = true;
							digits = $("#dp-display").val()
							if (digits.length > 0) {
	 							self._dialed_digits(digits);
							}						
						},
					});            		
            	}
			});
            
            $("#dp-hangup-button").click(function(){
				self._offhook = false;            
    			$("#dp-display").val('');
    			$.ajax({
					url: "/dialpad.py/onhook",
				});
			});
        },

        _setOption: function (key, value) {
            this.options[key] = value;
            this._update();
        },

        _update: function () {
            this._dialpad.css("background-color", this.options.background_color);
        },

        _dialed_digits: function (digits) {
			$.ajax({
				type: "POST",
				data: 'digits=' + digits,
				dataType: "json",
				url: "/dialpad.py/dialed_digits",
			});
        },
    });
});
