
/* Calculates the number of wags that will be produced from a given amount *
 * of cash. The function is wags = food^(1/2)                              */
function calculate()
{
	var dollars = document.getElementById("calculator_entry").value;
	
	// If the field is blank, make the wags div blank.
	wags_div = document.getElementById("wags")
	if (dollars == "") {
	   wags_div.innerHTML = "";
	   return;
	}
	
	// Otherwise, convert the amount into a float.
	var numeric_dollars = parseFloat(dollars);
	
	// If it's not a number, just return.
	if (isNaN(numeric_dollars)) return;
	
	// Otherwise, calculate the square root and post it
	// to the wags.
	wags = Math.pow(numeric_dollars, .5);
	document.getElementById("wags").innerHTML = wags.toFixed(2);
}
