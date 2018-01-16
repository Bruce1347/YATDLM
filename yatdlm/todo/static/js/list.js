/**
 * File that contains all the functions for list management
 */

// JS calls at page loading

// Setup for datepicker.js
// String that contains the due date as a ISO Date
var sendDate = "";
const picker = datepicker(document.getElementById('new_task_due_date'), {
    formatter: function(element, date) {
        /**
         * Ensuring that the saved date takes into account the timezone 
         * Since getTimezoneOffset returns a time in minutes, we have to convert the returned offset to milliseconds
         */
        var localDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));

        // Ensuring that the display date is to the european format (DD/MM/YYYY)
        element.value = localDate.toLocaleDateString();

        sendDate = localDate.toISOString();
    }
});

/**
 * Function that creates the adequate post data then sends it to the server in order to
 * create a new task.
 * 
 * url : the specfic needed url 
 */
function add_task(url)
{
    var task_title = document.getElementById('new_task_title').value;
    var task_descr = document.getElementById('new_task_descr').value;
    var task_priority = document.getElementById('new_task_priority').value;

    
    postdata  = "action=add";
    postdata += "&title="+encodeURIComponent(task_title);
    postdata += "&descr="+encodeURIComponent(task_descr);
    postdata += "&due="+encodeURIComponent(sendDate);
    postdata += "&priority="+encodeURIComponent(task_priority);

    submit(url, postdata, "list-container");
}

/**
 * Function that creates the adequate post data then sends it to the server in order to delete a specified task
 * 
 * url : the specific needed url
 */
function del_task(url)
{
    if (!confirm("Voulez-vous supprimer cette tâche ?"))
        return;
    
    postdata = "";
    submit(url, postdata, "list-container");
}

function mark_task_as_done(url)
{
    postdata = "";
    submit(url, postdata, "list-container");
}

function display_task(task_id, url)
{
    if (toggle('task_subline_'+task_id))
        submit(url, "", 'task_detail_'+task_id);
}