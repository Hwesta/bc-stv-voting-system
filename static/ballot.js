//This is used to validate an array of radio buttons, keep from having more than one selected per row and column and then create a JSON object from it.

function enforceBallotValidity()
{
	var column, element, selector;
	element=$(this);
	// IE does not support grep/match functions natively.
	column = element.attr("class").split(/ /); 
	column = jQuery.grep(
		column,
		function(x){ return x.match(/data-column/) }
	);
	
	column = jQuery.map(
		column,
		function(x){ return x.replace(/data-column-/,''); }
	)[0];
	
	selector = "input[type=radio].data-column-"+column;
	$(selector).prop("checked", false);
	element.prop("checked", true);
};
		
function onSubmit()
{
	var formVals = $("form input:radio").serializeArray();
	var jsonObj = {};
	var length=Math.sqrt($("form input:radio").length);
	var i;
	
	console.log("length: "+length)

	for (i=1; i<=length; i++)
	{
		jsonObj[i]="";
	}

	for (i in formVals)
	{
		jsonObj[formVals[i].value]=formVals[i].name;
		console.log("value: "+formVals[i].value+" name: "+formVals[i].name);
	}
	//Inspired by a comment on the jquery documentation at http://api.jquery.com/serializeArray/			
  	var submitVals = JSON.stringify(jsonObj);
				
	//console.log(submitVals);
	//return false;
	$('input#id_vote').val(submitVals);
	console.log($('input#id_vote'));
	return true;
}