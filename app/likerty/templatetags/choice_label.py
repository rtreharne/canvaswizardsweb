from django import template

register = template.Library()

@register.filter
def choice_label(field, key):
    return dict(field.field.choices).get(key)