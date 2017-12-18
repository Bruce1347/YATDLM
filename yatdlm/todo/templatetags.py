from django.template.defaulttags import register

# Custom filter in order to use dictionaries inside django templates
@register.filter
def get_value(dict, key):
    return dict.get(key)