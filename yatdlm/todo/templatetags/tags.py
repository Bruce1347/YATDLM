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
    url_regex = '(https?:\/\/[a-zA-Z0-9_-]+\.[a-zA-Z0-9\/]+[a-zA-Z0-9-_&#\/\.\=\?]+)'

    # The set is used here to manage a stupid edge case when we have multiple
    # occurrences of a substring.
    # The trick is to have unique substrings in order to avoid recursion when
    # we are using str.replace().
    urls_substrings = set(re.findall(url_regex, desc))

    for url in urls_substrings:
        href = '<a href="{0}">{0}</a>'.format(url)
        # Second part of the stupid edge case : we have an intermediate step
        # which consists of replace() the url by the string 'REPLACEME'.
        # Thanks to this we avoid recursion and we can substitute 'REPLACEME'
        # by hrefs containing `url`
        desc = desc.replace(url, 'REPLACEME')
        desc = desc.replace('REPLACEME', href)

    # We need to mark as safe the returned string in order to avoid string escaping
    return mark_safe(desc)