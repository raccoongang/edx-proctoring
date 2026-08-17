"""
Tests for proctoring template helpers.
"""
from urllib import parse as urlparse

from django.test import SimpleTestCase

from edx_proctoring.templatetags.template_helpers import extend_url_with_query_parameters


class ExtendUrlWithQueryParametersTests(SimpleTestCase):
    """
    Tests for the hardware-checker URL helper.
    """

    def test_extends_url_without_edx_platform_dependency(self):
        """
        Preserve existing query parameters while adding hardware state.
        """
        result = extend_url_with_query_parameters(
            "/exam?attempt=1",
            hardware_checker="camera",
            hardware_checked="microphone",
        )

        parsed_result = urlparse.urlparse(result)
        self.assertEqual(parsed_result.path, "/exam")
        self.assertEqual(
            dict(urlparse.parse_qsl(parsed_result.query)),
            {
                "attempt": "1",
                "hardware_checker": "camera",
                "hardware_checked": "microphone",
            },
        )
