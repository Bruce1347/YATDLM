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

// Const DOM elements that may be useful later
const category_to_edit = document.getElementById("category_to_edit");
const edit_category_btn = document.getElementById("edit_category-btn");
const delete_category_btn = document.getElementById("delete_category-btn");

function setup() {
    const public = document.getElementById('dom_ispublicjs').value === 'true';
    setup_event_listeners_buttons(public);
    setup_filters_events();
    setup_sublines_togglers();
    setup_categories(public);
    setup_tasks(public);
}

function setup_event_listeners_buttons(public) {
    // If we're in public mode, do nothing
    if (public === true)
        return;
    // Setup event listeners for buttons
    document.getElementById("add-category-form-btn").addEventListener('click', () => {
        toggle_add_category_form();
    });
    document.getElementById("add-category-btn").addEventListener('click', () => {
        add_new_category();
    });
    category_to_edit.addEventListener('change', () => {
        // Disable button if the selected category doesn't exists
        edit_category_btn.disabled = category_to_edit.value === "-1";
        delete_category_btn.disabled = category_to_edit.value === "-1";
        let edit_category_name = document.getElementById("edit_category_name");
        edit_category_name.value = category_to_edit.options[category_to_edit.selectedIndex].text;
    });
    edit_category_btn.addEventListener('click', async function() {
        const response = await edit_category();
        const updated_category = await response.json();
        await fetch_categories();
        update_categories();
        let tasks_to_update = tasks.filter((task) => {
            let idx = task.categories.findIndex((category) => {
                return category.id === updated_category.id;
            });
            return idx !== -1;
        });
        tasks_to_update.forEach((task) => {
            var td = document.getElementById(`categories_${task.no}`);
            td.innerText = updated_category.name;
        });
    });
    delete_category_btn.addEventListener('click', async function() {
        await delete_category();
        await fetch_categories();
        update_categories();
    });
}

function setup_filters_events() {
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
    document.getElementById("select_tcategory").addEventListener('change', filter_tasks);
}

function setup_sublines_togglers() {
    // Setup togglers for sub lines inside the tbody
    document.getElementById("list-container").querySelectorAll('tr:not(.hidden):not(.subtask)').forEach(
        (element) => {
            var children = element.querySelectorAll('td:not(.delete)');
            children.forEach((child) => {
                child.addEventListener('click', () => {
                    //TODO: Also use a Map for tasks and avoid linear search time.
                    fetch_task_followups_then_toggle(tasks.find((elt) => {
                        return elt.no === parseInt(element.id);
                    }));
                });
            });
        }
    );

}

const categories = [];
function setup_categories(public) {
    if (public === false) {
        // Fetch categories
        fetch_categories().then(() => {
            update_categories();
        });
    }
}

async function setup_tasks(public = false) {
    // Fetch tasks when the page is loaded
    await fetch_tasks(tasks);
    const parent_tasks_container = document.getElementById('new_task_parent_task');
    // Setup togglers for each task detail
    for (var i = 0; i < tasks.length; ++i) {
        const element = tasks[i];
        // Get the task id from the tr id
        const editBtn = document.getElementById(`edit-btn_${element.no}`);
        const closeBtn = document.getElementById(`close-btn_${element.no}`);
        const addCommentBtn = document.getElementById(`add_followup-btn_${element.no}`);
        editBtn.addEventListener('click', () => {
            edit_task_experimental(`task_detail_${element.no}`, element.no);
        });
        closeBtn.addEventListener('click', () => {
            closeTask(element);
        });
        addCommentBtn.addEventListener('click', () => {
            addFollowup(element);
        });
        if (element.is_done !== true && element.is_rejected !== true) {
            const reject_task_btn = document.getElementById(`reject_task-btn_${element.no}`);
            reject_task_btn.addEventListener('click', () => {
                let dom_followup = document.getElementById(`followup_${element.no}`);
                let followup = null;
                if (dom_followup && dom_followup.value !== '') {
                    followup = dom_followup.value;
                }
                reject_task(element.list_id, element.id, followup);
            });
        }

        if (public === false) {
            // Add the task to the subtasks select
            var parent_tasks_option = new Option(`#${element.no}: ${element.title}`, `${element.id}`);
            parent_tasks_container.add(parent_tasks_option);
            for (let subtask of element.subtasks) {
                // Attach a callback to its corresponding checkbox
                var checkbox_btn = document.getElementById(`subtask_${subtask.id}_btn`);
                checkbox_btn.addEventListener('click', () => {
                    closeTask(subtask);
                })
            }
        }
    }
}

var tasks = [];
const priorities = Object();

function update_categories() {
    const new_task_category = document.getElementById("new_task_category");
    const filter_categories = document.getElementById("select_tcategory");
    const edit_categories = document.getElementById("category_to_edit");

    // Since we have the same number of categories each time, one loop is
    // enough to clear all the selects elements

    for (let i = new_task_category.options.length - 1; i >= 1; --i) {
        new_task_category.remove(i);
        filter_categories.remove(i);
        edit_categories.remove(i);
    }

    categories.forEach((element, key) => {
        // Since a DOM node can't have multiple parents, we can't factorize
        // this part.
        new_task_category.add(new Option(element.name, element.id));
        filter_categories.add(new Option(element.name, element.id));
        edit_categories.add(new Option(element.name, element.id));
    });
}

// Store the followups in a map with task id as key
const followups = new Map();

async function fetch_task_followups_then_toggle(data) {
    //createDOMFollowup
    var curr_followups = followups.get(data.id);
    if (curr_followups === undefined) {
        let resp = await getFollowups(data.list_id, data.id);
        curr_followups = resp.followups;
        followups.set(data.id, curr_followups);
    }
    if (toggle(`task_subline_${data.no}`)) {
        const followupsContainer = document.getElementById(`followups_${data.no}`);
        // Remove current children to avoid content duplication
        while (followupsContainer.firstChild) {
            followupsContainer.removeChild(followupsContainer.firstChild);
        }
        for (var i = 0; i < curr_followups.length; ++i) {
            followupsContainer.appendChild(createDOMFollowup(curr_followups[i]));
        }
    }
}

/**
 * Handles the addition of one followup to a specific task.
 * @param {Object} task
 */
async function addFollowup(task) {
    const requestBody = JSON.stringify({
        'followup': document.getElementById(`followup_${task.no}`).value,
    });
    const response = await post(`/todo/lists/${task.list_id}/${task.id}/add_followup`, requestBody);
    const data = await response.json();
    await updateFollowups(task);
}

/**
 * Updates the followups of a task and adds a new DOM node for the latest
 * created task.
 * @param {Object} task the task that needs its followups to be updated
 */
async function updateFollowups(task) {
    const followups = await getFollowups(task.list_id, task.id);
    const followupsContainer = document.getElementById(`followups_${task.no}`);
    // Remove all children
    followupsContainer.innerHTML = '';
    for (let followup of followups.followups) {
        console.log(followup);
        let dom_followup = createDOMFollowup(followup);
        followupsContainer.appendChild(dom_followup);
    }
}

/**
 * This function will create an ``Element`` that will represent a single followup.
 * @param {Object} followup The followup that needs to be translated to a DOM Node.
 */
function createDOMFollowup(followup) {
    // Parent div that will contain the followup.
    const parentNode = document.createElement('div');
    parentNode.classList.add("marginb-normal", "single_followup");
    const followupHeader = document.createElement('div');
    const contentHeader = document.createElement('div');

    // Common styles / classes
    contentHeader.style.padding = "0.8em";
    contentHeader.style.hyphens = "auto";
    followupHeader.classList.add("b_grey");

    // Specific styles classes
    // Magic numbers here infortunately, gotta find a way to use literal strings instead.
    parentNode.appendChild(followupHeader);
    if (followup.type === 2) {
        // Modification followup
        followupHeader.classList.add("update_header");
        followupHeader.innerHTML = `<b>${followup.writer}</b> a mis à jour la tâche le ${followup.creation_date}`;
    } else {
        followupHeader.classList.add("followup_header");
        contentHeader.innerHTML = findUrls(followup.content);
        if (followup.type === 1) {
            // Comment
            followupHeader.innerHTML = `<b>${followup.writer}</b> a commenté le ${followup.creation_date}:`;
        } else {
            // State change
            followupHeader.innerHTML = `<b>${followup.writer}</b> a changé la priorité de ${followup.old_priority} à ${followup.new_priority}.`;
        }
        parentNode.appendChild(contentHeader);
    }
    return parentNode;
}


/**
 * DEPRECATED: Handles the closure or the re-opening of a task.
 * @param {Object} task The task that has to be closed or re-opened
 */
async function closeTask(task) {
    let close_followup = document.getElementById(`followup_${task.no}`);
    const requestBody = new Object();
    if (close_followup) {
        requestBody.followup = close_followup.value;
    }
    const response = await patch(`/todo/lists/${task.list_id}/${task.id}/close`, JSON.stringify(requestBody));
    const updatedTask = await response.json();
    const currentTaskIdx = tasks.findIndex((t) => {
        return t.id === updatedTask.id;
    });
    updateDOMTask(updatedTask);
    if (!updatedTask.is_subtask) {
        Object.assign(tasks[currentTaskIdx], updatedTask);
        updateFollowups(task);
    }
}

/**
 * Updates the followups and their DOM representation.
 * @param {number} listId
 * @param {number} taskId
 */
async function getFollowups(listId, taskId) {
    const response = await get(`/todo/lists/${listId}/${taskId}/get_followups`);
    const data = await response.json();
    return data;
}

function edit_task_experimental(node_id, id) {
    createTaskEditTd(node_id, id);
}

function createTaskEditTd(node_id, task_id) {
    /** EDIT FORM */
    var currentTask = tasks.find((elt) => {
        return elt.no === parseInt(task_id);
    });
    var td = document.createElement('td');
    td.id = `task_edit_${task_id}`;
    td.colSpan = 8;
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

    // Category
    let categories_container = document.createElement("div");
    categories_container.classList.add('marginb-normal', 'fullwidth');
    categories_container.id = `task_${task_id}_new_categories`;
    let edit_categories = categoriesToSelect(categories);
    edit_categories.name = `task_${task_id}_new_category`;
    edit_categories.classList.add('fullwidth');
    var edit_categories_label = document.createElement('label');
    edit_categories_label.setAttribute('for', edit_categories.name);
    edit_categories_label.textContent = 'Catégorie :';
    categories_container.appendChild(edit_categories_label);
    categories_container.appendChild(edit_categories);

    // Save and cancel buttons
    const save_task_btn = document.createElement('button');
    save_task_btn.type = 'button';
    save_task_btn.classList.add('pure-button');
    save_task_btn.classList.add('pure-button-primary');
    save_task_btn.classList.add('marginl-tiny');
    const add_category_btn = document.createElement('button');
    add_category_btn.type = 'button';
    add_category_btn.classList.add('pure-button');
    add_category_btn.classList.add('pure-button-primary');
    add_category_btn.classList.add('marginl-tiny', 'marginr-tiny');

    const cancel_edit_btn = document.createElement('button');
    cancel_edit_btn.type = 'button';
    cancel_edit_btn.classList.add('pure-button');
    cancel_edit_btn.classList.add('pure-button-primary');
    cancel_edit_btn.classList.add('marginr-tiny');

    save_task_btn.innerText = "SAUVEGARDER";
    add_category_btn.innerText = "AJOUTER UNE CATEGORIE"
    cancel_edit_btn.innerText = "ANNULER L'EDITION"

    // Assemble the form
    fieldSet.appendChild(edit_title_label);
    fieldSet.appendChild(edit_title);
    fieldSet.appendChild(edit_description_label);
    fieldSet.appendChild(edit_description);
    fieldSet.appendChild(edit_priority_label);
    fieldSet.appendChild(edit_priority);
    fieldSet.appendChild(categories_container);
    fieldSet.appendChild(save_task_btn);
    fieldSet.appendChild(add_category_btn);
    fieldSet.appendChild(cancel_edit_btn);
    editForm.appendChild(fieldSet);
    td.appendChild(editForm);

    /**
     * Replace the child and save the current child, its internal structure
     * will be used with the newer information  */
    const task_td = document.getElementById(node_id);
    // Bind cancel button to a callback which will restore the previous state
    cancel_edit_btn.addEventListener('click', () => {
        document.getElementById(td.id).replaceWith(task_td);
    });
    // Bind save button to a callback which will request the server to update
    // the task
    save_task_btn.addEventListener('click', async () => {
        const requestBody = {
            'title': edit_title.value,
            'description': edit_description.value,
            'priority': edit_priority.value
        };

        if (categories_container.children.length > 0) {
            let new_categories = new Array();
            for (var i = 0; i < categories_container.children.length; ++i) {
                var value = categories_container.children[i].value;
                if (value !== undefined && value !== "-1") {
                    new_categories.push(value);
                }
            }
            requestBody['categories'] = new_categories;
        }

        const updatedTask = await updateTask(JSON.stringify(requestBody), currentTask);
        const currentTaskIdx = tasks.findIndex((elt) => {
            return elt.id === updatedTask.id;
        });
        Object.assign(tasks[currentTaskIdx], updatedTask);
        document.getElementById(td.id).replaceWith(task_td);
        updateDOMTask(updatedTask);
        updateFollowups(updatedTask.list_id, updatedTask.id);
    });
    task_td.parentNode.replaceChild(td, task_td);
    // Bind the add_category button
    add_category_btn.addEventListener('click', () => {
        add_new_task_category(categories_container.id)
    });
}

/**
 * Makes the network request to update a specific task and ask the server to
 * save the changes in database.
 * @param {String} body The body of the request, it is expected to be a
 * stringified Object.
 * @param {Object} task The object that is subject to changes.
 */
async function updateTask(body, task) {
    const response = await patch(`/todo/lists/${task.list_id}/${task.id}/update/`, body);
    const updatedTask = await response.json();
    return updatedTask;
}

/**
 * Updates the DOM nodes that are displaying a specific task informations.
 * @param {Object} task The task subject to modifications
 */
function updateDOMTask(task) {
    if (!task.is_subtask) {
        const tr = document.getElementById(`${task.no}`);
        // Remove all the previous classes from the <tr>
        tr.classList.remove(...tr.classList);
        tr.classList.add("nowrap", `priority_${task.priority}`);
        // Replace all the visible text by their updated versions
        const priorityCell = document.getElementById(`priority_${task.no}`);
        priorityCell.innerText = task.priority_str;
        const titleCell = document.getElementById(`title_${task.no}`);
        titleCell.innerText = task.title_cropped;
        const descriptionCell = document.getElementById(`description_${task.no}`);
        descriptionCell.querySelector("p").innerText = task.description;
        const category_cell = document.getElementById(`categories_${task.no}`);
        const task_categories = new Array();
        for (var i = 0; i < task.categories.length; ++i) {
            var category = categories.find((cat) => {
                return cat.id === task.categories[i].id;
            });
            task_categories.push(category.name);
        }
        category_cell.innerText = task_categories.join(", ");
        // Update the resolution date and due date cells
        const closeBtn = document.getElementById(`close-btn_${task.no}`);
        if (task.is_done) {
            const resolutionDateCell = document.getElementById(`resolutiond_${task.no}`);
            resolutionDateCell.innerText = `Résolu le ${task.resolution_date} à ${task.resolution_hour}`;
            resolutionDateCell.colSpan = 2;
            const dueDateCell = document.getElementById(`dued_${task.no}`);
            dueDateCell.remove();
            closeBtn.innerText = "ROUVRIR LA TÂCHE";
        } else {
            const resolutionDateCell = document.getElementById(`resolutiond_${task.no}`);
            resolutionDateCell.innerText = "";
            resolutionDateCell.colSpan = 1;
            const dueDateCell = document.getElementById(`dued_${task.no}`);
            resolutionDateCell.parentNode.insertBefore(dueDateCell, resolutionDateCell);
            closeBtn.innerText = "FERMER LA TÂCHE";
        }
    } else {
        const tr = document.getElementById(`subtask_${task.id}`);
        // The check box is always the first child, and it's the only child of
        // its parent td, hence the fixed indexes here.
        const subtask_checkbox = tr.children.item(0).children.item(0);
        // The task title is always the second child of the tr element
        const subtask_title = tr.children.item(1);
        if (task.is_done === true) {
            subtask_checkbox.checked = true;
            subtask_title.classList.add('strikethrough');
        } else {
            subtask_checkbox.checked = false;
            subtask_title.classList.remove('strikethrough');
        }
    }
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
    var tdCategories = document.createElement('td');
    tdCategories.classList.add("pointer", "cell", "c-align");
    tdCategories.innerText = data.categories_str;
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
    tdImg.addEventListener('click', () => {
        del_task(`/todo/lists/${data.list_id}/del_task/${data.id}`, data.no);
    });
    tdDelete.appendChild(tdImg);

    newTr.appendChild(tdId);
    newTr.appendChild(tdTitle);
    newTr.appendChild(tdPriority);
    newTr.appendChild(tdCategories);
    newTr.appendChild(tdCreationDate);
    newTr.appendChild(tdResolutionDate);
    newTr.appendChild(tdDeadline);
    newTr.appendChild(tdDelete);

    return newTr;
}

function createNewDOMDetailTr(data) {
    var newSubline = document.createElement('tr');
    var newDetail = document.createElement('td');

    newSubline.id = `task_subline_${data.no}`;
    newSubline.classList.add('b_lightgrey');

    newDetail.id = `task_detail_${data.no}`;
    newDetail.colSpan = 8;

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
    // Task subtasks progression
    var div_progression = document.createElement('div');
    div_progression.id = `task_${data.no}_progression_span`;
    var span_progression = document.createElement('span');
    span_progression.innerHTML = `Progression: <b>${data.subtasks_progress}%</b>`
    div_progression.appendChild(span_progression);
    // Task description
    var spanDescr = document.createElement('span');
    spanDescr.innerHTML = `<p>${findUrls(data.description)}</p>`
    // Followups
    var divFollowups = document.createElement('div');
    divFollowups.classList.add('margint-normal');
    divFollowups.classList.add('followups_container');
    divFollowups.id = `followups_${data.no}`;

    newDetail.appendChild(divTitle);
    newDetail.appendChild(spanCrDate);
    newDetail.appendChild(div_progression);
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
    let task_categories_dom = document.getElementById('new_task_categories_container');
    task_categories_dom = task_categories_dom.getElementsByTagName("select");
    let parent_task = document.getElementById('new_task_parent_task').value;

    var bodyDict = {
        'title': task_title,
        'descr': task_descr,
        'due': task_end_date,
        'priority': task_priority,

    };
    var task_categories = new Array();
    if (task_categories_dom.length > 0) {
        for (var i = 0; i < task_categories_dom.length; ++i) {
            if (task_categories_dom[i].value !== '-1') {
                task_categories.push(task_categories_dom[i].value);
            }
        }
        bodyDict.categories = task_categories;
    }

    // If the user sets a parent task, add it to the body
    if (parent_task !== "-1") {
        bodyDict.parent_task = parent_task;
    }

    const body = JSON.stringify(bodyDict);

    const callback = async function (response) {
        var data = await response.json();
        if (response.status == 200) {
            var domTasks = document.querySelectorAll(`tr.priority_${task_priority}`);
            var firstElt = domTasks.item(0);
            var newTr = createNewDOMTasktr(data);
            var newDetail = createNewDOMDetailTr(data);
            if (data.is_subtask) {
                // TODO: Update the DOM with the new subtask
            } else {
                tasks.unshift(data);
                if (firstElt === null) {
                    firstElt = document.getElementById('list-container');
                    firstElt.appendChild(newTr);
                    firstElt.appendChild(newDetail);
                } else {
                    firstElt.parentNode.insertBefore(newTr, firstElt);
                    firstElt.parentNode.insertBefore(newDetail, newTr.nextSibling);
                }
            }
        } else {
        }
    }

    post(url, body).then((response) => {
        callback(response);
    });
}

/**
 * Retrieves tasks from the server and saves into `tasks`.
 */
async function fetch_tasks(arr) {
    var listId = document.getElementById('dom_list_id').value;

    const response = await get(`/todo/lists/${listId}/tasks?meta_tasks=true`);
    var data = await response.json();
    data.tasks.forEach(element => {
        arr.unshift(element);
    });
    // Copy priorities values and keys to the current context
    Object.assign(priorities, data.priorities);
}

async function fetch_categories() {
    const listId = document.getElementById('dom_list_id').value;

    const response = await get(`/todo/categories/${listId}/list`);
    const data = await response.json();
    Object.assign(categories, data.categories);
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
    var category = parseInt(document.getElementById("select_tcategory").value);

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
            (title !== "" && !element.title.toUpperCase().includes(title.toUpperCase())),
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
            (priority !== -1 && element.priority !== priority),
            // Check the categories
            (category !== -1 && !element.categories.some((elt) => {
                return elt.id === category;
            }))
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
async function del_task(url, task_id) {
    if (!confirm("Voulez-vous supprimer cette tâche ?"))
        return;

    const response = await _delete(url);
    if (response.status == 200) {
        var domTask = document.getElementById(task_id);
        var taskSubline = document.getElementById(`task_subline_${task_id}`);
        taskSubline.remove();
        domTask.remove();
        const taskIndex = tasks.findIndex((elt) => {
            return elt.id === parseInt(task_id);
        });
        tasks.splice(taskIndex, 1);
    } else {
        alert(`Il y a eu une erreur avec l'effacement de la tâche ${task_id}`);
    }
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

/**
 * Toggles the add category form and changes the text button accordingly.
 */
function toggle_add_category_form() {
    if (toggle("add-category-container")) {
        document.getElementById("add-category-form-btn").innerText = "Fermer le formulaire";
    } else {
        document.getElementById("add-category-form-btn").innerText = "Gérer les catégories"
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

/**
 * Creats a new category with the provided name.
 */
async function add_new_category() {
    const body = JSON.stringify({"name": document.getElementById("new_category_name").value});
    const list_id = document.getElementById('dom_list_id').value;
    const response = await post(`/todo/categories/${list_id}/create`, body);
    const new_category = await response.json();
}

/**
 * Edits an existing category with a newer name
 */
function edit_category() {
    const category_id = document.getElementById("category_to_edit").value;
    const body = JSON.stringify({"name": document.getElementById("edit_category_name").value});
    const list_id = document.getElementById("dom_list_id").value;
    const url = `/todo/categories/${category_id}`;
    return patch(url, body);
}

/**
 * Deletes an existing category
 */
function delete_category() {
    const category_id = document.getElementById("category_to_edit").value;
    const url = `/todo/categories/${category_id}`;
    return _delete(url);
}

/**
 * This function adds a new DOM element that contains a select node which
 * contains categories for a new task.
 */
function add_new_task_category(container_id=undefined) {
    if (!container_id) {
        container_id = "new_task_categories_container";
    }
    let categories_container = document.getElementById(container_id);
    // Create the new nodes
    let new_select = categoriesToSelect(categories);
    new_select.classList.add("fullwidth");

    // Append the new select to the current container
    categories_container.appendChild(new_select);
}

/**
 * Deletes the list pointed by ``list_id``.
 *
 * @param {Number} list_id The list that the user wants to delete
 */
async function delete_list(list_id) {
    await _delete(`/todo/lists/delete/${list_id}`);
    window.location.href = '/todo';
}

/**
 * Rejects a task and updates the DOM.
 * @param {Number} list_id The current todo list
 * @param {Number} task_id The task that has to be rejected
 * @param {String} followup An eventual reason for the rejection
 */
async function reject_task(list_id, task_id, followup = null) {
    let url = `/todo/lists/${list_id}/${task_id}/reject`;
    let body = '';
    if (followup !== null) {
        body = JSON.stringify({
            'followup': followup
        });
    }
    let result = await patch(url, body);
    let updated_task = await result.json();
    // Update the DOM
    updateDOMTask(updated_task);
    updateFollowups(updated_task);
    let reject_button = document.getElementById(`reject_task-btn_${updated_task.no}`);
    if (reject_button) {
        reject_button.remove();
    }
}