class Task {
    /**
     * Constructor of a Task
     * @param {String} json_task the JSON representation of a task, given by
     * API Calls.
     */
    constructor(json_task) {
        // Leverage the power of assign in order to not assign manually properties
        Object.assign(this, JSON.parse(json_task));
    }

    toJSON() {
        let res = {};
        // Deep copy
        Object.assign(res, this);
        let res_categories = Array();
        for (let category of res.categories) {
            res_categories.push(category.id);
        }
        Object.assign(res.categories, res_categories);
        return JSON.stringify(res);
    }
}