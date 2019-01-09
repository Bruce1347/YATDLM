/**
 * File that contains all the functions for list management
 */


// Things to do when the page is loaded
/**
 * Setup the date picker and ensure that the user cannot input deadlines in the
 * past.
*/
var picker = flatpickr(document.getElementById('new_task_due_date'), {
    minDate: "today"
});

/**
 * Setup the filters events.
 */
function search_task_handler() {
    var current_list_id = document.getElementById("dom_list_id").value;
    search_tasks(`/todo/lists/${current_list_id}/search`);
}
document.getElementById("input_tid").addEventListener('keyup', function() {
    this.classList.remove("red_border");
    var pattern = this.getAttribute("pattern");
    var value = this.value;

    var validator = new RegExp(pattern);

    if (validator.test(value)) {
	search_task_handler();
    } else {
        this.classList.add("red_border");
    }
});
document.getElementById("input_tname").addEventListener('keyup', search_task_handler);
document.getElementById("select_tcyear").addEventListener('change', search_task_handler);
document.getElementById("select_tcmonth").addEventListener('change', search_task_handler);
document.getElementById("select_tryear").addEventListener('change', search_task_handler);
document.getElementById("select_trmonth").addEventListener('change', search_task_handler);
document.getElementById("select_tdyear").addEventListener('change', search_task_handler);
document.getElementById("select_tdmonth").addEventListener('change', search_task_handler);
document.getElementById("select_tprio").addEventListener('change', search_task_handler);

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
    var task_end_date = document.getElementById('new_task_due_date').value;


    postdata  = "action=add";
    postdata += "&title="+encodeURIComponent(task_title);
    postdata += "&descr="+encodeURIComponent(task_descr);
    postdata += "&due="+encodeURIComponent(task_end_date);
    postdata += "&priority="+encodeURIComponent(task_priority);

    submit(url, postdata, "list-container");
}

function search_tasks(url) {
    var public = document.getElementById("dom_ispublicjs").value;
    // Document inputs
    var search_tid = document.getElementById("input_tid");
    var search_tname = document.getElementById("input_tname");
    var search_tcyear = document.getElementById("select_tcyear");
    var search_tcmonth = document.getElementById("select_tcmonth");
    var search_tryear = document.getElementById("select_tryear");
    var search_trmonth = document.getElementById("select_trmonth");
    var search_tdyear = document.getElementById("select_tdyear");
    var search_tdmonth = document.getElementById("select_tdmonth");
    var search_tprio = document.getElementById("select_tprio");

    // Search terms
    var input_tid = undefined;
    var input_tname = undefined;
    var input_tcyear = undefined;
    var input_tcmonth = undefined;
    var input_tryear = undefined;
    var input_trmonth = undefined;
    var input_tdyear = undefined;
    var input_tdmonth = undefined;
    var input_tprio = undefined;

    if (search_tid.value !== undefined && search_tid.value !== "")
        input_tid = encodeURIComponent(search_tid.value);

    if (search_tname.value !== undefined)
        input_tname = encodeURIComponent(search_tname.value);

    // Creation filter
    if (search_tcyear.value != -1)
        input_tcyear = encodeURIComponent(search_tcyear.value);
    if (search_tcmonth.value != -1)
        input_tcmonth = encodeURIComponent(search_tcmonth.value);

    // Resolution filter
    if (search_tryear.value != -1)
        input_tryear = encodeURIComponent(search_tryear.value);
    if (search_trmonth.value != -1)
        input_trmonth = encodeURIComponent(search_trmonth.value);

    // Deadline filter
    if (search_tdyear.value != -1)
        input_tdyear = encodeURIComponent(search_tdyear.value);
    if (search_tdmonth.value != -1)
        input_tdmonth = encodeURIComponent(search_tdmonth.value);

    if (search_tprio.value != -1)
        input_tprio = encodeURIComponent(search_tprio.value);

    // Build the postdata
    postdata = `?method=search&public=${public}`;
    if (input_tid !== undefined)
        postdata = postdata + `&tid=${input_tid}`;
    if (input_tname !== undefined)
        postdata = postdata + `&tname=${input_tname}`;
    if (input_tcmonth !== undefined)
        postdata = postdata + `&tcmonth=${input_tcmonth}`;
    if (input_tcyear !== undefined)
        postdata = postdata + `&tcyear=${input_tcyear}`;
    if (input_trmonth !== undefined)
        postdata = postdata + `&trmonth=${input_trmonth}`;
    if (input_tryear !== undefined)
        postdata = postdata + `&tryear=${input_tryear}`;
    if (input_tdmonth !== undefined)
        postdata = postdata + `&tdmonth=${input_tdmonth}`;
    if (input_tdyear !== undefined)
        postdata = postdata + `&tdyear=${input_tdyear}`;
    if (input_tprio !== undefined)
        postdata = postdata + `&tprio=${input_tprio}`;

    submit(url, postdata, "list-container", "GET");
}

/**
 * Sends a DELETE request to `url` to delete a task and modify accordingly the
 * DOM.
 * @param {string} url The URL that will be used to delete the task
 * @param {int} task_id The ID of the dom element containing the task
 */
function del_task(url, task_id) {
    if (!confirm("Voulez-vous supprimer cette tâche ?"))
        return;

    var headers = new Headers({
            'X-CSRFToken': get_cookie('csrftoken')
        });

    var methodDescription = {
        method: 'DELETE',
        headers: headers,
        mode: 'cors',
        cache: 'default'
    }

    const callback = function(response) {
        if (response.status == 200) {
            var domTask = document.getElementById(task_id);
            var taskSubline = document.getElementById(`task_subline_${task_id}`);
            taskSubline.remove();
            domTask.remove();
        } else {
            alert(`Il y a eu une erreur avec l'effacement de la tâche ${task_id}`);
        }
    }

    fetch(url, methodDescription).then((response) => {
        callback(response);
    });
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
