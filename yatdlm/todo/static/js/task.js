/**
 * Determine task_id and list_id from the current URL instead of hardcoding
 * them in the DOM with the server-side rendering engine.
 */
const current_url = window.location.href.split("/");
const task_id = current_url[current_url.length - 1];
const list_id = current_url[current_url.length - 2];

async function fetch_task_followups(list_id, task_id, update = false) {
    let curr_followups = followups.get(task_id);
    if (curr_followups === undefined || update === true) {
        let resp = await getFollowups(list_id, task_id);
        followups.set(task_id, resp.followups);
        curr_followups = resp.followups;
    }
    const followups_container = document.getElementById(`followups_${task_id}`);
    if (followups_container) {
        while (followups_container.firstChild) {
            followups_container.removeChild(followups_container.firstChild);
        }
    }
    for (let i = 0; i < curr_followups.length; ++i) {
        followups_container.appendChild(createDOMFollowup(curr_followups[i]));
    }
}

async function update_displayed_priority(task, updated_task) {
    Object.assign(task, updated_task);
    let displayed_task_priority = document.getElementById(`priority_${task.id}`);
    displayed_task_priority.querySelector("b").innerText = updated_task.priority_str;
    await fetch_task_followups(list_id, task_id, true);
}

function update_displayed_categories(task) {
    let displayed_categories = document.getElementById(`categories_${task.id}`);
    displayed_categories.querySelector("b").innerText = task.categories_str;
}

function update_displayed_description(task) {
    let displayed_description = document.getElementById(`description_${task.id}`);
    displayed_description.querySelector("p").innerText = task.description;
}

async function create_dom_edit_form(task) {
    let div = document.createElement('div');
    div.id = `edit_div_${task.id}`;

    // Title part
    let title_input_label = document.createElement('label');
    title_input_label.textContent = 'Titre :';
    title_input_label.setAttribute('for', `title_input_${task.id}`);
    let title_input = document.createElement('input');
    title_input.id = `title_input_${task.id}`;
    title_input.value = task.title;
    title_input.classList.add('marginb-normal', 'fullwidth');

    // Description part
    let description_textarea_label = document.createElement('label');
    description_textarea_label.textContent = 'Description :';
    description_textarea_label.setAttribute('for', `description_textarea_${task.id}`);
    let description_textarea = document.createElement('textarea');
    description_textarea.id = `description_textarea_${task.id}`;
    description_textarea.value = task.description;
    description_textarea.classList.add('marginb-normal', 'fullwidth');

    // Priority part
    let priority_select_label = document.createElement('label');
    priority_select_label.textContent = 'Priorité :';
    priority_select_label.setAttribute('for', `priority_select_${task.id}`);
    let priority_select = priorities_to_select(task.priorities);
    priority_select.id = `priority_select_${task.id}`;
    priority_select.classList.add('marginb-normal', 'fullwidth');
    priority_select.value = task.priority;

    // Categorie(s) part
    let categories_div_label = document.createElement('label');
    categories_div_label.textContent = 'Catégories :';
    categories_div_label.setAttribute('for', `categories_div_${task.id}`);
    let categories_div = document.createElement('div');
    categories_div.id = `categories_div_${task.id}`;
    categories_div.classList.add('fullwidth', 'marginb-normal');
    // Iterate over the categories and add them to the categories_div
    let list_categories = await get_categories(list_id);
    Object.entries(task.categories).forEach(([key, category]) => {
        let select = categoriesToSelect(list_categories);
        select.classList.add("fullwidth");
        select.value = category.id;
        categories_div.appendChild(select);
    });

    // Assemble the form
    div.appendChild(title_input_label);
    div.appendChild(title_input);
    div.appendChild(description_textarea_label);
    div.appendChild(description_textarea);
    div.appendChild(priority_select_label);
    div.appendChild(priority_select);
    div.appendChild(categories_div_label);
    div.appendChild(categories_div);
    return div;
}

async function edit_task(task) {
    let contents_dom = document.getElementById(`contents_${task.id}`);
    let priority_dom = document.getElementById(`priority_${task.id}`);
    let description_dom = document.getElementById(`description_${task.id}`);
    let categories_dom = document.getElementById(`categories_${task.id}`);

    let save_edit_btn = create_primary_button('SAUVEGARDER', ['marginr-tiny'], async () => {
        // Send the form
        let edit_title = document.getElementById(`title_input_${task.id}`);
        let edit_description = document.getElementById(`description_textarea_${task.id}`);
        let edit_priority = document.getElementById(`priority_select_${task.id}`);
        let categories_container = document.getElementById(`categories_div_${task.id}`);
        let request_body = {
            'title': edit_title.value,
            'description': edit_description.value,
            'priority': edit_priority.value,
        }
        if (categories_container.children.length > 0) {
            let new_categories = new Array();
            for (var i = 0; i < categories_container.children.length; ++i) {
                var value = categories_container.children[i].value;
                if (value !== undefined && value !== "-1") {
                    new_categories.push(value);
                }
            }
            request_body['categories'] = new_categories;
        }
        const updated_task = await update_task(JSON.stringify(request_body), task);
        Object.assign(task, updated_task);
        // Restore the previous DOM state
        document.getElementById(form.id).replaceWith(contents_dom);
        // Update ``contents_dom`` children with up to date informations
        update_displayed_priority(task, updated_task);
        description_dom.innerText = task.description;
        update_displayed_categories(task);
    });

    let add_category_btn = create_primary_button('AJOUTER UNE CATEGORIE', ['marginr-tiny'], async () => {
        let categories = await get_categories(list_id);
        add_new_category_to_task(`categories_div_${task.id}`, categories);
    });

    let cancel_edit_btn = create_primary_button("ANNULER L'EDITION", null, () => {
        document.getElementById(form.id).replaceWith(contents_dom);
    });

    let form = await create_dom_edit_form(task);
    form.style.margin = "auto";
    form.style.setProperty('max-width', '70em');
    form.appendChild(save_edit_btn);
    form.appendChild(add_category_btn);
    form.appendChild(cancel_edit_btn);

    contents_dom.parentNode.replaceChild(form, contents_dom);
}

function set_buttons_listeners(task) {
    const followups_paragraph = document.getElementById(`followups_title_${task.id}`)
    const edit_task_btn = document.getElementById(`edit_btn_${task.id}`);
    const add_followup_btn = document.getElementById(`add_followup-btn_${task.id}`);
    const reject_task_btn = document.getElementById(`reject-btn_${task.id}`);
    const close_task_btn = document.getElementById(`close-btn_${task.id}`);

    followups_paragraph.addEventListener('click', () => {
        toggle(`followups_${task.id}`);
    });
    edit_task_btn.addEventListener('click', () => {
        edit_task(task);
    });
    add_followup_btn.addEventListener('click', () => {
        add_followup(task);
    });
    reject_task_btn.addEventListener('click', async () => {
        let followup = document.getElementById(`followup_${task.id}`).value;
        let updated_task = await reject_task_common(task, followup);
        update_displayed_priority(task, updated_task);
    });
    close_task_btn.addEventListener('click', async () => {
        let updated_task = await close_task(task);
        update_displayed_priority(task, updated_task);
    });
}

let task = new Object();
let followups = new Map();

async function setup() {
    Object.assign(task, await get_task(list_id, task_id));
    await fetch_task_followups(list_id, task_id);
    set_buttons_listeners(task);
}