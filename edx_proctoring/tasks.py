"""
Celery tasks for edx-proctoring.
"""
import logging

from celery.task import task

from edx_proctoring import api
from edx_proctoring.exceptions import StudentExamAttemptDoesNotExistsException
from edx_proctoring.models import ProctoredExamStudentAttempt
from edx_proctoring.statuses import ProctoredExamStudentAttemptStatus

log = logging.getLogger('edx.celery.task')


@task(bind=True)
def complete_exam_if_attempt_fails(self, attempt_id):
    """
    Fix status of attempt in completed state if timed exam has ended in failure.

    Check attempt after timed exam is finished. If its status is in incomplete state
    (e.g. started. ready_to_submit, ready_to_decline) that update it to completed state
    (e.g. submitted, declined).
    """
    log.info(
        'Checking status of attempt %d after timed exam is finished.',
        attempt_id,
    )
    exam_attempt = ProctoredExamStudentAttempt.objects.get_exam_attempt_by_id(attempt_id)

    if not exam_attempt:
        err_msg = ('Attempted to access to exam attempt {0} but it does not exist.'.format(attempt_id))
        raise StudentExamAttemptDoesNotExistsException(err_msg)

    if exam_attempt.status in ProctoredExamStudentAttemptStatus.failed_exam_end_states:
        try:
            api.update_attempt_status(
                exam_attempt.proctored_exam_id,
                exam_attempt.user_id,
                to_status=ProctoredExamStudentAttemptStatus.convert_to_completed_state(exam_attempt.status),
            )
        except Exception as exc:
            log.exception('Retrying updating of exam attempt %d to completed state: %s.', attempt_id, exc)
            raise self.retry(exc=exc)

        else:
            log.info(
                'Updating of exam attempt %d from status "%s" to "%s" is completed.',
                attempt_id,
                exam_attempt.status,
                ProctoredExamStudentAttemptStatus.convert_to_completed_state(exam_attempt.status),
            )
