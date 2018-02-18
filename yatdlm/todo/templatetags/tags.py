from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

import re

# Custom filter in order to use dictionaries inside django templates
@register.filter
def get_value(dict, key):
    return dict.get(key)

# Custom filter that inserts hrefs into the given string then returns it
@register.filter
@stringfilter
def display_urls(desc):
    # Regex that matches URLs
    url_regex = '(https?:\/\/[a-zA-Z0-9_-]+\.[a-zA-Z0-9\/]+[a-zA-Z0-9-_&#\/\.]+)'
    urls_substrings = re.findall(url_regex, desc)

    for url in urls_substrings:
        href = '<a href="{}">{}</a>'.format(url, url)
        desc = desc.replace(url, href)

    # We need to mark as safe the returned string in order to avoid string escaping
    return mark_safe(desc)