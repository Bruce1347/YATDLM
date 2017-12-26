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