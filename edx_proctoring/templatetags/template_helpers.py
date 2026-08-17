"""
Provide template helpers method for proctoring templates.
"""
from urllib import parse as urlparse

from django import template

register = template.Library()


@register.simple_tag
def extend_url_with_query_parameters(url: str, hardware_checker: str, hardware_checked: str) -> str:
    """
    Add hardware checker parameters to a URL.

    :param url: The URL to extend.
    :param hardware_checker: The hardware checker being displayed.
    :param hardware_checked: The hardware checker that was completed.
    :return: The URL with updated query parameters.
    """
    parsed_url = urlparse.urlparse(url)
    query_parameters = dict(urlparse.parse_qsl(parsed_url.query))
    query_parameters.update(
        hardware_checker=hardware_checker,
        hardware_checked=hardware_checked,
    )
    return urlparse.urlunparse(
        parsed_url._replace(query=urlparse.urlencode(query_parameters))
    )
