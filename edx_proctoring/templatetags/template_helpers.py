"""
Provide template helpers method for proctoring templates.
"""
from django import template
from exam_dashboard.utils import extend_url_with_query_parameters as modify_url_with_query_parameters

register = template.Library()


@register.simple_tag
def extend_url_with_query_parameters(url, hardware_checker, hardware_checked):
    return modify_url_with_query_parameters(
        url,
        hardware_checker=hardware_checker,
        hardware_checked=hardware_checked
    )
