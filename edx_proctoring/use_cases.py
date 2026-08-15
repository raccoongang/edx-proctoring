"""
Application use cases for proctored exam workflows.
"""

from datetime import datetime
from typing import Optional

from kombu.exceptions import ChannelError
from kombu.exceptions import ConnectionError as KombuConnectionError
from kombu.exceptions import TimeoutError as KombuTimeoutError

from django.db import transaction
from django.utils import timezone

from edx_proctoring.exceptions import (
    StudentExamAttemptDoesNotExistsException,
    StudentExamAttemptRemovalQueueUnavailable
)
from edx_proctoring.models import ProctoredExamStudentAttempt
from edx_proctoring.tasks import remove_exam_attempt_task


class RequestExamAttemptRemoval:
    """
    Persist and publish an idempotent exam attempt removal request.
    """

    def execute(self, attempt_id: int, requesting_user_id: int) -> bool:
        """
        Mark an attempt for removal and publish a single Celery task.

        :param attempt_id: The ID of the proctored exam attempt to remove.
        :param requesting_user_id: The ID of the staff user requesting removal.
        :return: ``True`` when a new task was published, otherwise ``False``.
        :raises StudentExamAttemptDoesNotExistsException: If the attempt does not exist.
        :raises StudentExamAttemptRemovalQueueUnavailable: If Celery cannot accept the task.
        """
        removal_requested_at = self._mark_removal_requested(attempt_id)
        if removal_requested_at is None:
            return False

        try:
            remove_exam_attempt_task.apply_async(args=[attempt_id, requesting_user_id])
        except (ChannelError, KombuConnectionError, KombuTimeoutError, OSError) as exc:
            self._clear_removal_request(attempt_id, removal_requested_at)
            raise StudentExamAttemptRemovalQueueUnavailable(
                "Exam attempt removal could not be queued. Please try again."
            ) from exc

        return True

    @staticmethod
    def _mark_removal_requested(attempt_id: int) -> Optional[datetime]:
        """
        Persist a removal timestamp while serializing concurrent requests.

        :param attempt_id: The ID of the attempt to mark.
        :return: The new timestamp, or ``None`` when removal is already pending.
        :raises StudentExamAttemptDoesNotExistsException: If the attempt does not exist.
        """
        with transaction.atomic():
            try:
                attempt = ProctoredExamStudentAttempt.objects.select_for_update().get(id=attempt_id)
            except ProctoredExamStudentAttempt.DoesNotExist:
                raise StudentExamAttemptDoesNotExistsException(
                    "Cannot remove attempt for attempt_id = {attempt_id} because it does not exist!".format(
                        attempt_id=attempt_id,
                    )
                )

            if attempt.removal_requested_at is not None:
                return None

            removal_requested_at = timezone.now()
            attempt.removal_requested_at = removal_requested_at
            attempt.save(update_fields=["removal_requested_at", "modified"])
            return removal_requested_at

    @staticmethod
    def _clear_removal_request(attempt_id: int, removal_requested_at: datetime) -> None:
        """
        Make an attempt retryable when publishing to Celery fails.

        :param attempt_id: The ID of the attempt whose request failed.
        :param removal_requested_at: The timestamp written by this request.
        :return: None.
        """
        ProctoredExamStudentAttempt.objects.filter(
            id=attempt_id,
            removal_requested_at=removal_requested_at,
        ).update(removal_requested_at=None)
