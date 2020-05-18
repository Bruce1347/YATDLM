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
    let displayed_task_priority = document.getElementById(`priority_${task.id}`).querySelector("b");
    displayed_task_priority.innerText = updated_task.priority_str;
    await fetch_task_followups(list_id, task_id, true);
}

function set_buttons_listeners(task) {
    const followups_paragraph = document.getElementById(`followups_title_${task.id}`)
    const add_followup_btn = document.getElementById(`add_followup-btn_${task.id}`);
    const reject_task_btn = document.getElementById(`reject-btn_${task.id}`);
    const close_task_btn = document.getElementById(`close-btn_${task.id}`);

    followups_paragraph.addEventListener('click', () => {
        toggle(`followups_${task.id}`);
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