
/* We need to make sure the user's responses are numbers. This method *
 * confirms that.                                                     */
 function check_response(the_form, days, limit)
 {
    found_error = false;
    for (index = 0; index < days.length; index++) {
        day      = document.getElementById(days[index]);
        response = day.value;
        
        /* There are a few things required of the response. It must be
         * a number, it cannot be blank, and it must be at most 5 digits
         * long with at most 2 decimal places.
         */
        is_number = !isNaN(response);
        exists    = response != '';
        if (is_number && exists) {
            response_value = parseFloat(response);
            non_negative   = response_value >= 0;
            
            // Check that the value is under the limit (if there
            // is one)
            if (limit || limit == 0) under_limit = response_value <= limit;
            else                     under_limit = true;
        }
        
        else {
            non_negative = false;
            under_limit  = true;
        }
         
        // Calculate the number of decimals
        decimal_location = response.indexOf('.');
        if (decimal_location == -1) {
           before_decimal = response;
           after_decimal  = '';
        }
        
        else {
           before_decimal = response.substr(0, decimal_location);
           after_decimal  = response.substr(   decimal_location + 1);
        }
         
        // If there are no more than three digits before the decimal and
        // no more than two digits after it, we're good.
        valid_digits = (before_decimal.length <= 3) &&
                       (after_decimal.length  <= 2);
        
        // Is it good??
        valid_response = non_negative && valid_digits && under_limit;
         
        if (!valid_response) {
            day.style.borderColor = "#F00";
            if (!under_limit) document.getElementById("limit").style.color = "#F00";
            else              document.getElementById("limit").style.color = "#000";
        }
        
        else {
            day.style.borderColor = "#000";
            if (limit) document.getElementById("limit").style.color = "#000";
        }
    }
    
    // If we've made it here, the inputs are good.
    if (valid_response) document.getElementById(the_form).submit();
 }