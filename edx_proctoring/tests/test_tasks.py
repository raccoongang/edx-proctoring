"""
Tests for Celery tasks in ``edx_proctoring.tasks``.
"""

from __future__ import absolute_import

from mock import patch

from edx_proctoring.exceptions import StudentExamAttemptDoesNotExistsException
from edx_proctoring.models import ProctoredExamStudentAttempt
from edx_proctoring.statuses import ProctoredExamStudentAttemptStatus
from edx_proctoring.tasks import complete_exam_if_attempt_fails, remove_exam_attempt_task

from .utils import ProctoredExamTestCase


class RemoveExamAttemptTaskTests(ProctoredExamTestCase):
    """
    Tests for asynchronous proctored exam attempt removal.
    """

    def test_remove_exam_attempt_deletes_attempt(self):
        """
        Remove an existing attempt through the queued task path.
        """
        exam_attempt = self._create_started_exam_attempt()

        result = remove_exam_attempt_task.run(
            attempt_id=exam_attempt.id,
            requesting_user_id=self.user.id,
        )

        self.assertIsNone(result)
        self.assertIsNone(
            ProctoredExamStudentAttempt.objects.get_exam_attempt_by_id(exam_attempt.id)
        )

    @patch("edx_proctoring.api.remove_exam_attempt")
    def test_remove_exam_attempt_is_delegated_to_api(self, mocked_remove_exam_attempt):
        """
        Delegate queued attempt removal to the existing API implementation.
        """
        exam_attempt = self._create_started_exam_attempt()

        result = remove_exam_attempt_task.run(
            attempt_id=exam_attempt.id,
            requesting_user_id=self.user.id,
        )

        self.assertIsNone(result)
        mocked_remove_exam_attempt.assert_called_once_with(
            exam_attempt.id,
            requesting_user=self.user,
        )

    @patch("edx_proctoring.api.remove_exam_attempt")
    def test_missing_attempt_is_ignored(self, mocked_remove_exam_attempt):
        """
        Ignore a queued removal whose attempt was already removed.
        """
        mocked_remove_exam_attempt.side_effect = StudentExamAttemptDoesNotExistsException

        result = remove_exam_attempt_task.run(
            attempt_id=9999,
            requesting_user_id=self.user.id,
        )

        self.assertIsNone(result)
        mocked_remove_exam_attempt.assert_called_once_with(
            9999,
            requesting_user=self.user,
        )


class CompleteExamIfAttemptFailsTests(ProctoredExamTestCase):
    """
    Regression tests for completion checks scheduled after timed exams.
    """

    def test_missing_attempt_is_ignored(self):
        """
        Ignore a task whose active attempt was already removed.
        """
        self.assertIsNone(complete_exam_if_attempt_fails.run(attempt_id=9999))

    @patch("edx_proctoring.api.update_attempt_status")
    def test_attempt_removed_during_update_is_ignored(self, mocked_update_attempt_status):
        """
        Ignore deletion that occurs between lookup and status update.
        """
        exam_attempt = self._create_started_exam_attempt(is_proctored=False)
        mocked_update_attempt_status.return_value = None

        result = complete_exam_if_attempt_fails.run(attempt_id=exam_attempt.id)

        self.assertIsNone(result)
        mocked_update_attempt_status.assert_called_once_with(
            exam_attempt.proctored_exam_id,
            exam_attempt.user_id,
            to_status=ProctoredExamStudentAttemptStatus.submitted,
            raise_if_not_found=False,
            skip_if_completed=True,
        )
