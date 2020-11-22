# -*- coding: utf-8 -*-
"""
Celery tasks for communication with examus proctoring server.
"""
import logging

from celery import task
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from opaque_keys.edx.keys import CourseKey

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from edx_proctoring.models import ProctoredExamStudentAttempt

log = logging.getLogger(__name__)


@task(bind=True)
def calculate_grade_after_exam_review_task(self, attempt_code, student_id, course_id):
    student = User.objects.get(id=student_id)
    course_key = CourseKey.from_string(course_id)
    course_grade = CourseGradeFactory().read(user=student, course_key=course_key)
    try:
        student_record = ProctoredExamStudentAttempt.objects.get(attempt_code=attempt_code)
        student_record.passed = course_grade.passed
        student_record.exam_grade = (course_grade.percent * 100)
        student_record.save()
        log.info("Grade was successfully added to the student attempt exam record")
    except ObjectDoesNotExist:
        log.warning("Adding Exam grade to the student attempt was failed")
