/**
 * File that contains all the functions for list management
 */

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
    var task_due   = document.getElementById('new_task_due_date').value;
    
    postdata  = "action=add";
    postdata += "&title="+encodeURIComponent(task_title);
    postdata += "&descr="+encodeURIComponent(task_descr);
    postdata += "&due="+encodeURIComponent(task_due);

    submit(url, postdata, "list-container");
}