//This is used to validate an array of radio buttons, keep from having more than one selected per row and column and then create a JSON object from it.

function enforceBallotValidity(obj, scope)
{
	var column, element, selector;
	//element=$(this);
	element=$(obj);
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
    scope = '';	
	selector = scope+" input[type=radio].data-column-"+column;
	$(selector).prop("checked", false);
	element.prop("checked", true);
};
		
function onSubmit()
{
    //var formVals = $("form input:radio").serializeArray();
	var formVals = $(this).find("input:radio").serializeArray();
	var jsonObj = {};
	var length=Math.sqrt($(this).find("input:radio").length);
	var i;
	
	//Initialize the votes to be blank.
	for (i=1; i<=length; i++)
	{
		jsonObj[i]="";
	}

	for (i in formVals)
	{
		jsonObj[formVals[i].value]=formVals[i].name;
	}
	//Inspired by a comment on the jquery documentation at http://api.jquery.com/serializeArray/			
  	var submitVals = JSON.stringify(jsonObj);
				
	$(this).find('input#id_vote').val(submitVals);
	console.log($(this).find('input#id_vote'));
	return true;
}

//Function will fill in the disabled radio buttons to show ballots already entered.
function display(ballot_id, vote_json, is_spoiled)
{
	if (!is_spoiled)
	{
		for (i in vote_json)
		{
			value=vote_json[i];
			$('form#ballot-'+ballot_id+' input#id-'+value+'-'+i).attr('checked', true);

		}
	}
	
}
