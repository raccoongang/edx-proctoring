"""
Provide template helpers method for proctoring templates.
"""
from django import template
from util.url import extend_url_with_query_parameters as modify_url_with_query_parameters

register = template.Library()


@register.simple_tag
def extend_url_with_query_parameters(url: str, hardware_checker: str, hardware_checked: str):
    return modify_url_with_query_parameters(
        url,
        hardware_checker=hardware_checker,
        hardware_checked=hardware_checked
    )
