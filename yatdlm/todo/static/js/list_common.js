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
 * Gets the followups of a specific task
 * @param {Number} listId
 * @param {Number} taskId
 */
async function getFollowups(listId, taskId) {
    const response = await get(`/todo/lists/${listId}/${taskId}/get_followups`);
    const data = await response.json();
    return data;
}

/**
 * Updates the followups of a task and adds a new DOM node for the latest
 * created task.
 * @param {Object} task the task that needs its followups to be updated
 */
async function update_followups(task) {
    const followups = await getFollowups(task.list_id, task.id);
    const followupsContainer = document.getElementById(`followups_${task.id}`);
    // Remove all children
    followupsContainer.innerHTML = '';
    for (let followup of followups.followups) {
        let dom_followup = createDOMFollowup(followup);
        followupsContainer.appendChild(dom_followup);
    }
}

/**
 * Handles the addition of one followup to a specific task.
 * @param {Object} task
 */
async function add_followup(task) {
    const requestBody = JSON.stringify({
        'followup': document.getElementById(`followup_${task.id}`).value,
    });
    const response = await post(`/todo/lists/${task.list_id}/${task.id}/add_followup`, requestBody);
    const data = await response.json();
    await update_followups(task);
}

/**
 * Fetches one task and returns its object.
 * @param {Number} list_id
 * @param {Number} task_id
 */
async function get_task(list_id, task_id, public = false) {
    if (public === false) {
        var url = `/todo/lists/${list_id}/${task_id}?json`;
    } else {
        var url = `/todo/lists/public/${list_id}/${task_id}?json`;
    }
    const response = await get(url);
    const data = await response.json();
    return data;
}

/**
 * Handles the closure or the re-opening of a task
 * @param {*} task The task that has to be closed or re-opened.
 */
async function close_task(task) {
    let followup = document.getElementById(`followup_${task.id}`);
    const body = new Object();
    if (followup) {
        body.followup = followup.value;
    }
    const response = await patch(
        `/todo/lists/${task.list_id}/${task.id}/close`,
        JSON.stringify(body)
    );
    const updated_task = await response.json();
    // TODO: write update_dom_task function
    return updated_task;
}

/**
 * Rejects a task and returns the updated task.
 * @param {Object} task The task that has to be rejected
 * @param {String} followup An eventual reason for the rejection
 */
async function reject_task_common(task, followup) {
    let url = `/todo/lists/${task.list_id}/tasks/${task.id}`;
    let body = null;
    if (followup !== null) {
        body = JSON.stringify({
            'followup': followup
        });
    }
    let response = await patch(url, body);
    let updated_task = await response.json();
    return updated_task;
}

/**
 * Gets a JSON list of the categories associated to a specific todo list.
 * @param {Number} list_id The id of the list
 */
async function get_categories(list_id) {
    const response = await get(`/todo/categories/${list_id}/list`);
    const data = await response.json();
    return data.categories;
}

/**
 * A function that will add a new ``Select`` element to the ``container_id`` container.
 * This function shall be used for task edition.
 * @param {String} container_id The div that contains all the categories associated to a Task
 * @param {Array<Object>} categories An array of categories
 */
function add_new_category_to_task(container_id, categories) {
    let categories_container = document.getElementById(container_id);
    let new_select = categoriesToSelect(categories);
    new_select.classList.add("fullwidth");
    categories_container.appendChild(new_select);
}

/**
 * Function that will make a request against the backend in order to update as specific task.
 * @param {String} body The body of the request, this must be a stringified Object.
 * @param {Object} task The Task that will be updated.
 */
async function update_task(body, task_list_id, task_id) {
    let url = `/todo/lists/${task_list_id}/tasks/${task_id}`;
    const response = await put(url, body);
    const updated_task = await response.json();
    return updated_task;
}

/**
 * Attempts a deletion of the list with ``list_id`` being its id.
 *
 * @param {Number} list_id The id of the list that shall be deleted
 */
async function delete_list(list_id) {
    // Ask the user for a manual confirmation
    if (!confirm(`Voulez-vous effacer cette liste ?`)) {
        // Allow a rollback to the current window if they hit the cancel button
        return;
    }

    await _delete(`/todo/lists/delete/${list_id}`);
    window.location.href = '/todo';
}