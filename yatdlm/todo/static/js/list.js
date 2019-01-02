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


document.getElementById("input_tid").addEventListener('keyup', function() {
    this.classList.remove("red_border");
    var pattern = this.getAttribute("pattern");
    var value = this.value;

    var validator = new RegExp(pattern);

    if (validator.test(value)) {
        search_tasks(`/todo/lists/${current_list_id}/search`);
    } else {
        this.classList.add("red_border");
    }
});

function search_task_handler() {
    var current_list_id = document.getElementById("dom_list_id").value;
    search_tasks(`/todo/lists/${current_list_id}/search`);
}

document.getElementById("input_tname").addEventListener('keyup', search_task_handler);
document.getElementById("select_tcyear").addEventListener('change', search_task_handler);
document.getElementById("select_tcmonth").addEventListener('change', search_task_handler);

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

function search_tasks(url) {
    // Document inputs
    var search_tid = document.getElementById("input_tid");
    var search_tname = document.getElementById("input_tname");
    var search_tcyear = document.getElementById("select_tcyear");
    var search_tcmonth = document.getElementById("select_tcmonth");

    // Search terms
    var input_tid = undefined;
    var input_tname = undefined;
    var input_tcyear = undefined;
    var input_tcmonth = undefined;

    if (search_tid.value !== undefined && search_tid.value !== "")
        input_tid = encodeURIComponent(search_tid.value);

    if (search_tname.value !== undefined)
        input_tname = encodeURIComponent(search_tname.value);

    if (search_tcyear.value != -1)
        input_tcyear = encodeURIComponent(search_tcyear.value);

    if (search_tcmonth.value != -1)
        input_tcmonth = encodeURIComponent(search_tcmonth.value);

    // Build the postdata
    postdata = `?method=search`;
    if (input_tid !== undefined)
        postdata = postdata + `&tid=${input_tid}`;
    if (input_tname !== undefined)
        postdata = postdata + `&tname=${input_tname}`;
    if (input_tcmonth !== undefined)
        postdata = postdata + `&tcmonth=${input_tcmonth}`;
    if (input_tcyear !== undefined)
        postdata = postdata + `&tcyear=${input_tcyear}`;

    submit(url, postdata, "list-container", "GET");
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
    postdata += "&xhr="+encodeURIComponent("true");

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

/**
 * Closes all tasks details in the current document.
 */
function close_details() {
    var table = document.getElementById('list-container');
    var cells = table.getElementsByTagName('tr');
    var detail_re = new RegExp('^task_subline_[0-9]+');

    for (var i = 0; i < cells.length; ++i) {
        let element = cells[i];
        var re_results = detail_re.exec(element.id);
        if (re_results !== null) {
            if (!element.classList.contains("hidden"))
                toggle(element.id);
        }
    }
}