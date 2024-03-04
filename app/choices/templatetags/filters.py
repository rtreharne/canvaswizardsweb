from django import template

register = template.Library()

@register.filter
def filter_by_year(rules, year):
    return [rule for rule in rules if rule.year == year]