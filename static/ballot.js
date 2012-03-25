//This is used to validate an array of radio buttons, keep from having more than one selected per row and column and then create a JSON object from it.

function enforceBallotValidity(){
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
		
function onSubmit() {
				var formVals = $(this).serializeArray();
  				var jsonObj = {};
				
				//Inspired by a comment on the jquery documentation at http://api.jquery.com/serializeArray/
  				for (i in formVals)
    				jsonObj[formVals[i].name] = formVals[i].value;
				
				console.log(jsonObj);
  				var submitVals = JSON.stringify(jsonObj);
				
				console.log(submitVals);
				return false;
}