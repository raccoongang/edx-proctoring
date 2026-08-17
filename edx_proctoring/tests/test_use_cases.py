"""
Tests for proctoring application use cases.
"""

from kombu.exceptions import ConnectionError as KombuConnectionError
from mock import patch

from edx_proctoring.exceptions import (
    StudentExamAttemptDoesNotExistsException,
    StudentExamAttemptRemovalQueueUnavailable
)
from edx_proctoring.models import ProctoredExamStudentAttempt
from edx_proctoring.use_cases import RequestExamAttemptRemoval

from .utils import ProctoredExamTestCase


class RequestExamAttemptRemovalTests(ProctoredExamTestCase):
    """
    Tests for durable and idempotent exam attempt removal requests.
    """

    @patch("edx_proctoring.use_cases.remove_exam_attempt_task.apply_async")
    def test_execute_marks_attempt_and_publishes_task(self, mocked_apply_async):
        """
        Persist the pending state before publishing the removal task.
        """
        exam_attempt = self._create_started_exam_attempt()

        result = RequestExamAttemptRemoval().execute(exam_attempt.id, self.user.id)

        self.assertTrue(result)
        exam_attempt.refresh_from_db()
        self.assertTrue(exam_attempt.is_removal_pending)
        mocked_apply_async.assert_called_once_with(args=[exam_attempt.id, self.user.id])

    @patch("edx_proctoring.use_cases.remove_exam_attempt_task.apply_async")
    def test_execute_does_not_publish_duplicate_task(self, mocked_apply_async):
        """
        Treat a repeated removal request as a successful no-op.
        """
        exam_attempt = self._create_started_exam_attempt()
        use_case = RequestExamAttemptRemoval()

        self.assertTrue(use_case.execute(exam_attempt.id, self.user.id))
        self.assertFalse(use_case.execute(exam_attempt.id, self.user.id))

        mocked_apply_async.assert_called_once_with(args=[exam_attempt.id, self.user.id])

    @patch("edx_proctoring.use_cases.remove_exam_attempt_task.apply_async")
    def test_execute_clears_pending_state_when_publish_fails(self, mocked_apply_async):
        """
        Allow a new request when Celery cannot accept the removal task.
        """
        exam_attempt = self._create_started_exam_attempt()
        mocked_apply_async.side_effect = KombuConnectionError("broker unavailable")

        with self.assertRaises(StudentExamAttemptRemovalQueueUnavailable):
            RequestExamAttemptRemoval().execute(exam_attempt.id, self.user.id)

        exam_attempt.refresh_from_db()
        self.assertFalse(exam_attempt.is_removal_pending)

    def test_execute_rejects_missing_attempt(self):
        """
        Reject a removal request for an attempt that does not exist.
        """
        with self.assertRaises(StudentExamAttemptDoesNotExistsException):
            RequestExamAttemptRemoval().execute(9999, self.user.id)

        self.assertFalse(ProctoredExamStudentAttempt.objects.filter(id=9999).exists())
