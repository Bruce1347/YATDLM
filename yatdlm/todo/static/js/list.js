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

// Setup togglers for sub lines inside the tbody
document.getElementById("list-container").querySelectorAll('tr').forEach(
    (element) => {
        var children = element.querySelectorAll('td:not(.delete)');
        children.forEach((child) => {
            child.addEventListener('click', () => {
                toggle(`task_subline_${element.id}`);
            });
        });
    }
);

var tasks = [];
const priorities = Object();
// Fetch tasks when the page is loaded
fetch_tasks(tasks).then(() => {
    // Setup togglers for each task detail
    for (var i = 0; i < tasks.length; ++i) {
        const element = tasks[i];
        // Get the task id from the tr id
        var btn = document.getElementById(`edit-btn_${element.id}`);
        btn.addEventListener('click', () => {
            edit_task_experimental(`task_detail_${element.id}`, element.id);
        });
    }
});

function edit_task_experimental(node_id, id) {
    createTaskEditTd(node_id, id);
}

function createTaskEditTd(node_id, task_id) {
    console.log(node_id);
    /** EDIT FORM */
    var currentTask = tasks.find((elt) => {
        return elt.id === parseInt(task_id);
    });
    var td = document.createElement('td');
    td.id = `task_edit_${task_id}`;
    td.colSpan = 7;
    var editForm = document.createElement('form');
    var fieldSet = document.createElement('fieldset');
    fieldSet.classList.add('noborder');

    /** INPUTS */
    // Title
    var edit_title = document.createElement('input');
    edit_title.name = `task_${task_id}_new_title`;
    edit_title.classList.add('marginb-normal', 'fullwidth');
    edit_title.setAttribute('type', 'text');
    edit_title.value = currentTask.title;
    var edit_title_label = document.createElement('label');
    edit_title_label.setAttribute('for', edit_title.name);
    edit_title_label.textContent = 'Titre :';

    // Description
    var edit_description = document.createElement('textarea');
    edit_description.name = `task_${task_id}_new_description`;
    edit_description.classList.add('marginb-normal', 'fullwidth');
    edit_description.value = currentTask.description;
    var edit_description_label = document.createElement('label');
    edit_description_label.setAttribute('for', edit_title.name);
    edit_description_label.textContent = 'Description :';

    // Priority
    var edit_priority = objectToSelect(priorities, currentTask.priority);
    edit_priority.name = `task_${task_id}_new_priority`;
    edit_priority.classList.add('marginb-normal', 'fullwidth');
    var edit_priority_label = document.createElement('label');
    edit_priority_label.setAttribute('for', edit_priority.name);
    edit_priority_label.textContent = 'Priorité :';

    // Assemble the form
    fieldSet.appendChild(edit_title_label);
    fieldSet.appendChild(edit_title);
    fieldSet.appendChild(edit_description_label);
    fieldSet.appendChild(edit_description);
    fieldSet.appendChild(edit_priority_label);
    fieldSet.appendChild(edit_priority);
    editForm.appendChild(fieldSet);
    td.appendChild(editForm);

    /**
     * Replace the child and save the current child, its internal structure
     * will be used with the newer information  */ 
    var task_td = document.getElementById(node_id);
    task_td.parentNode.replaceChild(td, task_td);
}

function createNewDOMTasktr(data) {
    var newTr = document.createElement('tr');
    newTr.classList.add('nowrap', `priority_${data.priority}`);
    newTr.id = data.no;

    var tdId = document.createElement('td');
    tdId.classList.add("pointer", "cell", "c-align");
    tdId.innerText = data.no;
    tdId.id = `${data.id}_id`;
    tdId.addEventListener('click', () => toggle(`task_subline_${data.no}`));
    var tdTitle = document.createElement('td');
    tdTitle.classList.add("pointer", "cell");
    tdTitle.innerText = data.title_cropped;
    tdTitle.id = `${data.id}_title`;
    tdTitle.addEventListener('click', () => toggle(`task_subline_${data.no}`));
    var tdCreationDate = document.createElement('td');
    tdCreationDate.classList.add("pointer", "cell", "c-align");
    tdCreationDate.innerText = data.creation_date;
    tdCreationDate.id = `${data.id}_creationd`;
    tdCreationDate.addEventListener('click', () => toggle(`task_subline_${data.no}`));
    var tdResolutionDate = document.createElement('td');
    tdResolutionDate.classList.add("pointer", "cell", "c-align");
    tdResolutionDate.id = `${data.id}_resolutiond`;
    tdResolutionDate.addEventListener('click', () => toggle(`task_subline_${data.no}`));
    var tdDeadline = document.createElement('td');
    tdDeadline.classList.add("pointer", "cell", "c-align");
    if (data.due_date !== undefined)
        tdDeadline.innerText = data.due_date;
    tdDeadline.id = `${data.id}_deadline`;
    tdDeadline.addEventListener('click', () => toggle(`task_subline_${data.no}`));
    var tdPriority = document.createElement('td');
    tdPriority.classList.add("pointer", "cell", "c-align");
    tdPriority.innerText = data.priority_str;
    tdPriority.addEventListener('click', () => toggle(`task_subline_${data.no}`));
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

function createNewDOMDetailTr(data) {
    var newSubline = document.createElement('tr');
    var newDetail = document.createElement('td');

    newSubline.id = `task_subline_${data.no}`;
    newSubline.classList.add('b_lightgrey');

    newDetail.id = `task_detail_${data.no}`;
    newDetail.colSpan = 7;

    // Task title
    var divTitle = document.createElement('div');
    var spanTitle = document.createElement('span');
    divTitle.classList.add('margint-normal');
    spanTitle.style = 'font-size: 1.8em';
    spanTitle.innerHTML = `Tâche #${data.no} : ${data.title}`;
    divTitle.appendChild(spanTitle);
    // Task creation date
    var divCrDate = document.createElement('div');
    var spanCrDate = document.createElement('span');
    divCrDate.appendChild(spanCrDate);
    spanCrDate.innerHTML = `Crée le ${data.creation_date} à ${data.creation_hour} par <b>${data.creator}</b>`;
    // Task description
    var spanDescr = document.createElement('span');
    spanDescr.innerHTML = `<p>${data.description}</p>`
    // Followups
    var divFollowups = document.createElement('div');
    divFollowups.classList.add('margint-normal');
    divFollowups.classList.add('followups_container');
    divFollowups.id = `followups_${data.no}`;

    newDetail.appendChild(divTitle);
    newDetail.appendChild(spanCrDate);
    newDetail.appendChild(document.createElement('hr'));
    newDetail.appendChild(spanDescr);
    newDetail.appendChild(document.createElement('hr'));
    newDetail.appendChild(divFollowups);

    newSubline.appendChild(newDetail);
    return newSubline;
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
            var domTasks = document.querySelectorAll(`tr.priority_${task_priority}`);
            var firstElt = domTasks.item(0);
            var newTr = createNewDOMTasktr(data);
            var newDetail = createNewDOMDetailTr(data);
            if (firstElt === null) {
                firstElt = document.getElementById('list-container');
                firstElt.appendChild(newTr);
                firstElt.appendChild(newDetail);
            } else {
                firstElt.parentNode.insertBefore(newTr, firstElt);
                firstElt.parentNode.insertBefore(newDetail, newTr.nextSibling);
            }
        } else {
        }
    }

    fetch(url, methodDescription).then((response) => {
        callback(response);
    });
}

/**
 * Retrieves tasks from the server and saves into `tasks`.
 */
async function fetch_tasks(arr) {
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
        arr.unshift(element);
    });
    // Copy priorities values and keys to the current context
    Object.assign(priorities, data.priorities);
}

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
        var currDomElt = document.getElementById(element.no);
        currDomElt.classList.remove("hidden");
        var eltCrDate = new Date(element.creation_date);
        var eltResDate = undefined;
        if (typeof(element.resolution_date) !== undefined)
            eltResDate = new Date(element.resolution_date);
        else
            eltResDate = undefined;
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

        // If any of the previous condition is met, the task and its subline are
        // masked
        if (conditions.some( function (item) { return item })) {
            document.getElementById(`task_subline_${element.no}`).classList.add("hidden");
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

    var postdata = "";
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
