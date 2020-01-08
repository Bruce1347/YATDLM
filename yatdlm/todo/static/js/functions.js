/**
 * This file contains every useful function that doesn't need its own dedicated file
 */


/**
 * This function retrieves a cookie named `cookie` in the document cookies.
 */
function get_cookie(cookie)
{
    // Every cookies
    var cookies = document.cookie.split(";");

    var return_value = null;

    // Then we look at every cookie, if we find the one, we return it
    cookies.forEach(element => {
        var split = element.split("=");
        var name = split[0];
        var value = split[1];

        if (name == cookie)
            return_value = value;
    });

    return return_value;
}

/**
 * This function adds or remove the class "hidden" from an element, then returns a boolean that helps the user 
 * to adapt the instructions following the call of toggle
 */
function toggle(id)
{
    var classList = document.getElementById(id).classList;
    var return_value = classList.contains("hidden");
    
    if (return_value)
        classList.remove("hidden");
    else
        classList.add("hidden");

    return return_value;
}

/**
 * This function takes an object and creates a ``select`` HTML element from
 * the object Keys & Values.
 */
function objectToSelect(obj, selected_id=undefined) {
    const select = document.createElement('select');
    Object.keys(obj).forEach((key) => {
        const option = document.createElement('option');
        option.value = key;
        option.text = obj[key];
        if (selected_id !== undefined && selected_id === parseInt(key)) {
            option.selected = true;
        }
        select.appendChild(option);
    });
    return select;
}

/**
 * Takes an array of ``Object`` that respresents a backend category and
 * transforms it into a select element.
 * @param {Array} categories The categories that must be transformed into a
 * select.
 */
function categoriesToSelect(categories) {
    const select = document.createElement('select');
    let empty_option = document.createElement('option');
    empty_option.value = "-1";
    select.appendChild(empty_option);
    Object.keys(categories).forEach((key) => {
        const option = document.createElement('option');
        option.value = categories[key].id;
        option.text = categories[key].name;
        select.appendChild(option);
    });
    return select;
}

/**
 * This function 
 * @param {String} text The text that may contain displayable URLs
 */
function findUrls(text) {
    // url_regex = '(https?:\/\/[a-zA-Z0-9_-]+\.[a-zA-Z0-9\/]+[a-zA-Z0-9-_&#\/\.\=\?]+)'
    urlRegexp = /(https?:\/\/[a-zA-Z0-9_-]+\.[a-zA-Z0-9\/]+[a-zA-Z0-9-_&#\/\.\=\?]+)/g;

    const urls = new Set(text.match(urlRegexp));

    urls.forEach((url) => {
        /**
         * We have to hack here by replacing URLs in the first time by a
         * temporary value in order to avoid recursion.
         * Since hrefs contains URLs, a simple loop would lead to URLs
         * being replaced endlessly, hence the substitute value. 
        */

       // Replace forward slashes to escaped chars in order to make them 
       // literal in the regexp.
       const urlReplaceRegexp = new RegExp(url.replace(/\//g, '\\/'), "g"); 
       text = text.replace(urlReplaceRegexp, "REPLACEME");
       console.log(text);
       const href = `<a href="${url}">${url}</a>`;
       text = text.replace(new RegExp("REPLACEME", "g"), href);
    });

    return text;
}