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
document.getElementById("input_tid").addEventListener('keyup', function () {
    this.classList.remove("red_border");
    var pattern = this.getAttribute("pattern");
    var value = this.value;

    var validator = new RegExp(pattern);

    if (validator.test(value)) {
        filter_tasks();
    } else {
        this.classList.add("red_border");
    }
});
document.getElementById("input_tname").addEventListener('keyup', filter_tasks);
document.getElementById("select_tcyear").addEventListener('change', filter_tasks);
document.getElementById("select_tcmonth").addEventListener('change', filter_tasks);
document.getElementById("select_tryear").addEventListener('change', filter_tasks);
document.getElementById("select_trmonth").addEventListener('change', filter_tasks);
document.getElementById("select_tdyear").addEventListener('change', filter_tasks);
document.getElementById("select_tdmonth").addEventListener('change', filter_tasks);
document.getElementById("select_tprio").addEventListener('change', filter_tasks);

function createNewDOMTasktr(data) {
    var newTr = document.createElement('tr');
    newTr.classList.add('nowrap', `priority_${data.priority}`);

    var tdId = document.createElement('td');
    tdId.classList.add("pointer", "cell", "c-align");
    tdId.innerText = data.no;
    tdId.id = `${data.id}_id`;
    var tdTitle = document.createElement('td');
    tdTitle.classList.add("pointer", "cell");
    tdTitle.innerText = data.title_cropped;
    tdTitle.id = `${data.id}_title`;
    var tdCreationDate = document.createElement('td');
    tdCreationDate.classList.add("pointer", "cell", "c-align");
    tdCreationDate.innerText = data.creation_date;
    tdCreationDate.id = `${data.id}_creationd`;
    var tdResolutionDate = document.createElement('td');
    tdResolutionDate.classList.add("pointer", "cell", "c-align");
    tdResolutionDate.id = `${data.id}_resolutiond`;
    var tdDeadline = document.createElement('td');
    tdDeadline.classList.add("pointer", "cell", "c-align");
    if (data.due_date !== undefined)
        tdDeadline.innerText = data.due_date;
    tdDeadline.id = `${data.id}_deadline`;
    var tdPriority = document.createElement('td');
    tdPriority.classList.add("pointer", "cell", "c-align");
    tdPriority.innerText = data.priority_str;
    var tdDelete = document.createElement('td');
    tdDelete.classList.add("pointer", "cell", "c-align");
    var tdImg = document.createElement('img');
    tdImg.classList.add("pointer");
    tdImg.alt = "Delete";
    tdImg.width = 24;
    tdImg.height = 24;
    tdImg.src = '/static/img/icons/garbage_red.svg';
    tdDelete.appendChild(tdImg);

    newTr.appendChild(tdId);
    newTr.appendChild(tdTitle);
    newTr.appendChild(tdCreationDate);
    newTr.appendChild(tdResolutionDate);
    newTr.appendChild(tdDeadline);
    newTr.appendChild(tdPriority);
    newTr.appendChild(tdDelete);

    return newTr;
}

function add_task_exp(url) {
    var task_title = document.getElementById('new_task_title').value;
    var task_descr = document.getElementById('new_task_descr').value;
    var task_priority = document.getElementById('new_task_priority').value;
    var task_end_date = document.getElementById('new_task_due_date').value;

    var headers = new Headers({
        'X-CSRFToken': get_cookie('csrftoken'),
        'Content-Type': 'application/json'
    });

    var methodDescription = {
        method: 'POST',
        headers: headers,
        mode: 'cors',
        cache: 'default',
        body: JSON.stringify({
            'title': task_title,
            'descr': task_descr,
            'due': task_end_date,
            'priority': task_priority
        })
    }

    const callback = async function (response) {
        var data = await response.json();
        tasks.unshift(data);
        if (response.status == 200) {
            var firstElt = document.querySelectorAll(`tr.priority_${task_priority}`).item(0);
            var newTr = createNewDOMTasktr(data);
            if (firstElt === null) {
                firstElt = document.getElementById('list-container');
                firstElt.appendChild(newTr);
            } else {
                firstElt.parentNode.insertBefore(newTr, firstElt);
            }
        } else {
        }
    }

    fetch(url, methodDescription).then((response) => {
        callback(response);
    });
}

var tasks = [];

/**
 * Retrieves tasks from the server and saves into `tasks`.
 */
async function fetch_tasks() {
    var listId = document.getElementById('dom_list_id').value;
    var headers = new Headers({
        'X-CSRFToken': get_cookie('csrftoken'),
        'Content-Type': 'application/json'
    });

    var methodDescription = {
        method: 'GET',
        headers: headers,
        mode: 'cors',
        cache: 'default'
    }

    var res = await fetch(`/todo/lists/${listId}/tasks`, methodDescription);
    var data = await res.json();
    data.tasks.forEach(element => {
        tasks.unshift(element);
    })
}
fetch_tasks(); // Fetch tasks when the page is loaded

/**
 * Filters the tasks inside the document with the user-set filters.
 */
function filter_tasks() {
    var task_no = document.getElementById("input_tid").value;
    var title = document.getElementById("input_tname").value;
    var creationMonth = parseInt(document.getElementById("select_tcmonth").value);
    var creationYear = parseInt(document.getElementById("select_tcyear").value);
    var resolutionMonth = parseInt(document.getElementById("select_trmonth").value);
    var resolutionYear = parseInt(document.getElementById("select_tryear").value);
    var dueMonth = parseInt(document.getElementById("select_tdmonth").value);
    var dueYear = parseInt(document.getElementById("select_tdyear").value);
    var priority = parseInt(document.getElementById("select_tprio").value);

     tasks.forEach(element => {
        var currDomElt = document.getElementById(element.id);
        currDomElt.classList.remove("hidden");
        var eltCrDate = new Date(element.creation_date);
        if (typeof(element.resolution_date) !== undefined)
            var eltResDate = new Date(element.resolution_date);
        else
            var eltResDate = undefined;
        if (typeof(element.due_date) !== undefined)
            var eltDueDate = new Date(element.due_date);
        else
            var eltDueDate = undefined;

        var conditions = [
            // Check the task number
            (task_no !== "" && parseInt(task_no) !== element.no),
            // Check whether the title contains the user substring
            (title !== "" && !element.title.includes(title)),
            // Check the creation month
            (creationMonth !== -1 && eltCrDate.getMonth() + 1 !== creationMonth),
            // Check the creation year
            (creationYear !== -1 && eltCrDate.getFullYear() !== creationYear),
            // Check the resolution month
            (resolutionMonth !== -1 && eltResDate !== undefined && eltResDate.getMonth() + 1 !== resolutionMonth),
            // Check the resolution year
            (resolutionYear !== -1 && eltResDate !== undefined && eltResDate.getFullYear() !== resolutionYear),
            // Check the deadline month
            (dueMonth !== -1 && eltDueDate !== undefined && eltDueDate.getMonth() + 1 !== dueMonth),
            // Check the deadline year
            (dueYear !== -1 && eltDueDate !== undefined && eltDueDate.getFullYear() !== dueYear),
            // Check the priority level
            (priority !== -1 && element.priority !== priority)
        ]

        // If any of the previous condition is met, the task is masked
        if (conditions.some( function (item) { return item })) {
            currDomElt.classList.add("hidden");
        }
    });
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

    const callback = function (response) {
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
function mark_task_as_done(url, btn, id) {
    postdata = "";

    if (typeof btn !== "undefined")
        postdata += "followup=" + encodeURIComponent(document.getElementById('followup_' + id).value);

    submit(url, postdata, "list-container");
}

function display_task(task_id, url, public, is_toggle) {
    postdata = "";
    postdata += "public=" + encodeURIComponent(public);
    postdata += "&xhr=" + encodeURIComponent("true");

    if (typeof is_toggle !== 'undefined')
        toggle('task_subline_' + task_id)
}

function edit_task(task_id, url) {
    var postdata = "";

    var new_title = document.getElementById("task_title_" + task_id).value;
    var new_descr = document.getElementById("task_descr_" + task_id).value;
    var new_priority = document.getElementById("task_priority_" + task_id).value;

    postdata += "title=" + encodeURIComponent(new_title);
    postdata += "&descr=" + encodeURIComponent(new_descr);
    postdata += '&prio=' + encodeURIComponent(new_priority);

    submit(url, postdata, 'task_detail_' + task_id);
}

/**
 * Function that displays or masks the followups
 * 
 */
function display_followups(id) {
    if (toggle('followups_' + id))
        document.getElementById('btn-followups_' + id).innerText = "Masquer les commentaires";
    else
        document.getElementById('btn-followups_' + id).innerText = "Afficher les commentaires";
}

/**
 * Function that allows the user to only add a followup
 * 
 * url : the needed url in order to post the data to the server
 * id : the task id
 */
function add_followup(url, task_id) {
    postdata = "followup=" + encodeURIComponent(document.getElementById('followup_' + task_id).value);

    submit(url, postdata, 'followups_' + task_id);
}

function add_list(url, elt) {
    var title = document.getElementById('new_list_title').value;
    var descr = document.getElementById('new_list_description').value;
    var public = document.getElementById('new_list_privacy').value;

    postdata = "";
    postdata += "&title=" + encodeURIComponent(title);
    postdata += "&description=" + encodeURIComponent(descr);
    postdata += "&visibility=" + encodeURIComponent(public);

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
        submit(url, "&xhr=" + encodeURIComponent("True"), elt);
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
