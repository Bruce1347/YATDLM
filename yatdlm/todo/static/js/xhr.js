/**
 * File that contains AJAX related functions for client/server interaction
 */

/**
 * Functions that creates an XHR object, constructs the postdata based on elements that are inside 
 * the DOM then sends the postdata to the server at `url`.
 * url : the destination
 * postdata : the data that we want to send
 * dom_id : the element that we want to update inside the DOM
 * method : the method that we shall use, by default it is set at "POST".
 */
function submit(url, postdata, dom_id, method)
{
    // Add a spinner to the dom_id in order to notify the user that they have to wait
    document.getElementById(dom_id).innerHTML = '<div class="c-align"><div class="lds-dual-ring"></div></div>';

    // Determine the request type
    var xhrmethod = "POST";
    if (method !== undefined)
        xhrmethod = method;

    // If it's a GET, then use parameters as query params.
    if (xhrmethod === "GET")
        url = `${url}${postdata}`;

    // Create our XHR object
    var xhr = new XMLHttpRequest();

    // Initialize a new request
    xhr.open(xhrmethod, url, true);

    // Header creation, since we will only submit text, we 
    // use application/x-www-form-urlencoded instead of multipart/form-data
    xhr.setRequestHeader("X-CSRFToken", get_cookie("csrftoken"));
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    // Since we are in a asynchronous state, we wait until a state change
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // If we have a 200 response from the server, therefore we can
            // update the DOM
            document.getElementById(dom_id).innerHTML = xhr.responseText;
        }
    }

    xhr.send(postdata);
}