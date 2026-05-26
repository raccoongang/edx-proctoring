"""
Celery tasks for edx-proctoring.
"""

import logging
from importlib import import_module
from typing import Optional

from celery.task import task

from edx_proctoring.models import ProctoredExamStudentAttempt
from edx_proctoring.statuses import ProctoredExamStudentAttemptStatus

log = logging.getLogger('edx.celery.task')


@task(bind=True)
def complete_exam_if_attempt_fails(self, attempt_id: int) -> Optional[None]:
    """
    Fix status of attempt in completed state if timed exam has ended in failure.

    Check attempt after timed exam is finished. If its status is in incomplete state
    (e.g. started, ready_to_submit, ready_to_decline) then update it to completed state
    (e.g. submitted, declined).

    :param attempt_id: The ID of the proctored exam attempt to check and potentially update
    :return: None
    """
    # ``api.py`` schedules this task, so defer the reverse import until execution.
    api = import_module('edx_proctoring.api')

    log.info(
        'Checking status of attempt %d after timed exam is finished.',
        attempt_id,
    )
    exam_attempt = ProctoredExamStudentAttempt.objects.get_exam_attempt_by_id(attempt_id)

    if not exam_attempt:
        log.info(
            'Skipping completion check for attempt %d because it no longer exists.',
            attempt_id,
        )
        return

    if exam_attempt.status in ProctoredExamStudentAttemptStatus.failed_exam_end_states:
        try:
            updated_attempt_id = api.update_attempt_status(
                exam_attempt.proctored_exam_id,
                exam_attempt.user_id,
                to_status=ProctoredExamStudentAttemptStatus.convert_to_completed_state(exam_attempt.status),
                raise_if_not_found=False,
                skip_if_completed=True,
            )
        except Exception as exc:
            log.exception('Retrying updating of exam attempt %d to completed state: %s.', attempt_id, exc)
            raise self.retry(exc=exc)

        else:
            if updated_attempt_id is None:
                log.info(
                    'Skipping completion check for attempt %d because it was removed during processing.',
                    attempt_id,
                )
                return

            log.info(
                'Updating of exam attempt %d from status "%s" to "%s" is completed.',
                attempt_id,
                exam_attempt.status,
                ProctoredExamStudentAttemptStatus.convert_to_completed_state(exam_attempt.status),
            )
