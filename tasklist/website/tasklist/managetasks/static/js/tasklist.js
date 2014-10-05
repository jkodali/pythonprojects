$(document).ready(function() {

        // JQuery code to be added in here.

	$("#task-list-table tr").click(function(e){
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

	$("#task-list-table input[type='checkbox'").change(function(e) {
		var cell = $(e.target).parent();
		var row = $(cell).parent();

		if (e.target.checked)
			row[0].className = 'selected-row';
		else
			row[0].className = '';
	});

	$("#add").click(function(e) {
		var savetype = 'add';
		$.ajax({
			url: "savetasks/",
			type: "POST",
			dataType: "json",
			data : {
				save_type: savetype,
				task_name: $("#taskname").val(),
				due_date: $("#duedate").val(),
				csrfmiddlewaretoken: csrf_token
			},
			success: function(json) {
				$("#taskname").val('');
				$("#duedate").val('');
				alert('success');
			},
			error: function(xhr, errmsg, err) {
				alert(xhr.status + ": " + xhr.responseText);
			}
		});
		return false;
	});
});
