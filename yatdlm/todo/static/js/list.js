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


/**
 * Function that changes the boolean value `is_done` to its opposite (in order to mark a task as done or not)
 * 
 * url : the specific needed url
 * btn : optional arg, if defined then we add to the postdata the followup added by the user
 */
function mark_task_as_done(url, btn, id)
{
    postdata = "";

    if (typeof btn !== "undefined")
        postdata += "followup="+encodeURIComponent(document.getElementById('followup_'+id).value);

    submit(url, postdata, "list-container");
}

function display_task(task_id, url, public, is_toggle)
{
    postdata = "";
    postdata += "public="+encodeURIComponent(public);
    postdata += "&xhr="+encodeURIComponent("True");

    if (typeof is_toggle !== 'undefined')
        toggle('task_subline_'+task_id)

    submit(url, postdata, 'task_detail_'+task_id);
}

function edit_task(task_id, url)
{
    var postdata = "";

    var new_title = document.getElementById("task_title_"+task_id).value;
    var new_descr = document.getElementById("task_descr_"+task_id).value;
    var new_priority = document.getElementById("task_priority_"+task_id).value;

    postdata += "title="+encodeURIComponent(new_title);
    postdata += "&descr="+encodeURIComponent(new_descr);
    postdata += '&prio='+encodeURIComponent(new_priority);

    submit(url, postdata, 'task_detail_'+task_id);
}

/**
 * Function that displays or masks the followups
 * 
 */
function display_followups(id)
{
    if(toggle('followups_'+id))
        document.getElementById('btn-followups_'+id).innerText = "Masquer les commentaires";
    else
        document.getElementById('btn-followups_'+id).innerText = "Afficher les commentaires";
}

/**
 * Function that allows the user to only add a followup
 * 
 * url : the needed url in order to post the data to the server
 * id : the task id
 */
function add_followup(url, task_id)
{
    postdata = "followup="+encodeURIComponent(document.getElementById('followup_'+task_id).value);

    submit(url, postdata, 'followups_'+task_id);
}

function add_list(url, elt)
{
    var title = document.getElementById('new_list_title').value;
    var descr = document.getElementById('new_list_description').value;
    var public = document.getElementById('new_list_privacy').value;

    postdata = "";
    postdata += "&title="+encodeURIComponent(title);
    postdata += "&description="+encodeURIComponent(descr);
    postdata += "&visibility="+encodeURIComponent(public);

    submit(url, postdata, elt);
}

/**
 * 
 * @param {string} url - The url used for deletion
 * @param {string} name - The name of the list
 * @param {boolean} xhr - If the deleted list is inside a div or not
 * @param {string} elt - The name of the element that will be updated through XHR
 */
function delete_list(url, name, xhr, elt) {

    if (!confirm(`Voulez-vous effacer ${name} ?`)) {
        return;
    }

    if (!xhr) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
    
        // Header creation, since we will only submit text, we use application/x-www-form-urlencoded 
        // instead of multipart/form-data
        xhr.setRequestHeader("X-CSRFToken", get_cookie("csrftoken"));
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                window.location = "/todo";
            }
        }
    
        xhr.send();
    } else {
        submit(url, "&xhr="+encodeURIComponent("True"), elt);
    }
}

/**
 * Toggles the add form and changes the text button accordingly.
 * @param {string} id - The id of the add form
 * @param {string} btnId - The id of the display button
 */
function toggle_add_form(id, btnId) {
    if (toggle(id)) {
        document.getElementById(btnId).innerHTML = "Fermer le formulaire";
    } else {
        document.getElementById(btnId).innerHTML = "Ajouter une tâche";
    }
}
