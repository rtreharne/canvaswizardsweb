from django import template

register = template.Library()

@register.filter
def filter_by_year(rules, year):
    return [rule for rule in rules if rule.year == year]

@register.filter
def in_string(value, arg):
    """Returns True if arg is a substring of value, False otherwise."""
    return value in arg