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

STATUS_TRANSITION_MAP = {
    ProctoredExamStudentAttemptStatus.started: ProctoredExamStudentAttemptStatus.submitted,
    ProctoredExamStudentAttemptStatus.ready_to_submit: ProctoredExamStudentAttemptStatus.submitted,
    ProctoredExamStudentAttemptStatus.ready_to_decline: ProctoredExamStudentAttemptStatus.declined,
}


@task(bind=True)
def fix_exam_attempt_status_in_completed_state(self, attempt_id):
    """
    Fix status of exam attempt in completed state.

    Check exam attempt after timed exam end. If its status is in incomplete state
    (e.g. started. ready_to_submit, ready_to_decline) that update it to completed state
    (e.g. submitted, declined).
    """
    log.info(
        "The task 'fix_exam_attempt_status_in_completed_state' for exam attempt [%d] started successfully.",
        attempt_id,
    )
    exam_attempt = ProctoredExamStudentAttempt.objects.get_exam_attempt_by_id(attempt_id)

    if not exam_attempt:
        err_msg = ("Attempted to access to exam attempt [{0}] but it does not exist.".format(attempt_id))
        raise StudentExamAttemptDoesNotExistsException(err_msg)

    if exam_attempt.status in STATUS_TRANSITION_MAP.keys():
        try:
            api.update_attempt_status(
                exam_attempt.proctored_exam_id,
                exam_attempt.user_id,
                to_status=STATUS_TRANSITION_MAP.get(exam_attempt.status),
            )
        except Exception as exc:
            log.exception("Retrying updating of exam attempt [%d]: [%s].", attempt_id, exc)
            raise self.retry(exc=exc)

    log.info(
        "The task 'fix_exam_attempt_status_in_completed_state' for exam attempt [%d] finished successfully.",
        attempt_id,
    )
