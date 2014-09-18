$(document).ready(function() {

        // JQuery code to be added in here.

	$("#box-table-a tr").click(function(e){
		var row = $(e.target).parent();
		var tbody = $(row).parent();

		// identify if it is a task row or a header row
		if (tbody.attr('class') == "normal")
		{
			// toggle the checkbox of this row
			var checkBoxElement = $(row).children().children();
			if (checkBoxElement[0].checked == null || checkBoxElement[0].checked == false)
			{
				checkBoxElement[0].checked = true;
				checkBoxElement.trigger('change');
			}
			else
			{
				checkBoxElement[0].checked = false;
				checkBoxElement.trigger('change');
			}
		}
	});

	$("#box-table-a input[type='checkbox'").change(function(e) {
		var cell = $(e.target).parent();
		var row = $(cell).parent();

		if (e.target.checked)
			row[0].className = 'selected-row';
		else
			row[0].className = '';
	});
});
