/**
 * This file contains every function related to network requests.
 */

/**
 * This function wraps the call to fetch in order to factorize the code related
 * to network requests.
 * @param {String} url The URL that will be used for the request.
 * @param {String} method The HTTP verb for the request.
 * @param {String} body The body of the request, in our case it needs to be
 * stringfied since we're using JSON for requests and responses.
 */
function fetchWrapper(url, method, body) {
    const methodDescription = {
        method: method,
        headers: new Headers({
            'X-CSRFToken': get_cookie('csrftoken'),
            'Content-Type': 'application/json'
        }),
        mode: 'cors',
        cache: 'default',
        body: body
    }
    return fetch(url, methodDescription);
}

/**
 * Wrapper function for POST requests.
 * @param {String} url The URL where we will POST at.
 * @param {String} body The stringified body that will be sent through POST at
 * `url`. 
 */
function post(url, body) {
    return fetchWrapper(url, 'POST', body);
}

/**
 * Wrapper function for PATCH requests.
 * @param {String} url The URL where we will PATCH a resource.
 * @param {String} body The stringified body that will be send through PATCH at
 * the resource.
 */
function patch(url, body) {
    return fetchWrapper(url, 'PATCH', body);
}

/**
 * Wrapper function for GET requests.
 * @param {String} url The URL where we will GET resources.
 */
function get(url) {
    return fetchWrapper(url, 'GET');
}

/**
 * Wrapper function for DELETE requests.
 * @param {String} url The URL to the resource that will be deleted.
 */
function _delete(url) {
    return fetchWrapper(url, 'DELETE');
}