# coding=utf-8
# pylint: disable=invalid-name
"""
All tests for the models.py
"""

from __future__ import absolute_import

import ddt
import six
from six.moves import range

from django.db import IntegrityError, transaction

from edx_proctoring.models import (
    CourseBlockHardwareChecker,
    ProctoredExam,
    ProctoredExamReviewPolicy,
    ProctoredExamReviewPolicyHistory,
    ProctoredExamStudentAllowance,
    ProctoredExamStudentAllowanceHistory,
    ProctoredExamStudentAttempt,
    ProctoredExamStudentAttemptHistory
)
from edx_proctoring.statuses import ProctoredExamStudentAttemptStatus

from .utils import LoggedInTestCase

# pragma pylint: disable=useless-super-delegation


class ProctoredExamModelTests(LoggedInTestCase):
    """
    All tests for the models.py
    """

    def setUp(self):
        """
        Build out test harnessing
        """
        super(ProctoredExamModelTests, self).setUp()

    def test_unicode(self):
        """
        Make sure we support Unicode characters
        """
        proctored_exam = ProctoredExam.objects.create(
            course_id='test_course',
            content_id='test_content',
            exam_name=u'अआईउऊऋऌ अआईउऊऋऌ',
            external_id='123aXqe3',
            time_limit_mins=90
        )
        output = six.text_type(proctored_exam)
        self.assertEqual(output, u"test_course: अआईउऊऋऌ अआईउऊऋऌ (inactive)")

        policy = ProctoredExamReviewPolicy.objects.create(
            set_by_user_id=self.user.id,
            proctored_exam=proctored_exam,
            review_policy='Foo Policy'
        )
        output = six.text_type(policy)
        self.assertEqual(output, u"ProctoredExamReviewPolicy: tester (test_course: अआईउऊऋऌ अआईउऊऋऌ (inactive))")

    def test_save_proctored_exam_student_allowance_history(self):  # pylint: disable=invalid-name
        """
        Test to Save and update the proctored Exam Student Allowance object.
        Upon first save, a new entry is _not_ created in the History table
        However, a new entry in the History table is created every time the Student Allowance entry is updated.
        """
        proctored_exam = ProctoredExam.objects.create(
            course_id='test_course',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )
        ProctoredExamStudentAllowance.objects.create(
            user_id=1,
            proctored_exam=proctored_exam,
            key='allowance_key',
            value='20 minutes'
        )
        # No entry in the History table on creation of the Allowance entry.
        proctored_exam_student_history = ProctoredExamStudentAllowanceHistory.objects.filter(user_id=1)
        self.assertEqual(len(proctored_exam_student_history), 0)

        # Update the allowance object twice
        # pylint: disable=no-member
        ProctoredExamStudentAllowance.objects.filter(
            user_id=1,
            proctored_exam=proctored_exam,
        ).update(
            user=1,
            proctored_exam=proctored_exam,
            key='allowance_key update 1',
            value='10 minutes'
        )

        # pylint: disable=no-member
        ProctoredExamStudentAllowance.objects.filter(
            user_id=1,
            proctored_exam=proctored_exam,
        ).update(
            user=1,
            proctored_exam=proctored_exam,
            key='allowance_key update 2',
            value='5 minutes'
        )

        # 2 new entries are created in the History table.
        proctored_exam_student_history = ProctoredExamStudentAllowanceHistory.objects.filter(user_id=1)
        self.assertEqual(len(proctored_exam_student_history), 2)

        # also check with save() method

        allowance = ProctoredExamStudentAllowance.objects.get(user_id=1, proctored_exam=proctored_exam)
        allowance.value = '15 minutes'
        allowance.save()

        proctored_exam_student_history = ProctoredExamStudentAllowanceHistory.objects.filter(user_id=1)
        self.assertEqual(len(proctored_exam_student_history), 3)

    def test_delete_proctored_exam_student_allowance_history(self):  # pylint: disable=invalid-name
        """
        Test to delete the proctored Exam Student Allowance object.
        Upon first save, a new entry is _not_ created in the History table
        However, a new entry in the History table is created every time the Student Allowance entry is updated.
        """
        proctored_exam = ProctoredExam.objects.create(
            course_id='test_course',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )
        allowance = ProctoredExamStudentAllowance.objects.create(
            user_id=1,
            proctored_exam=proctored_exam,
            key='allowance_key',
            value='20 minutes'
        )

        # No entry in the History table on creation of the Allowance entry.
        proctored_exam_student_history = ProctoredExamStudentAllowanceHistory.objects.filter(user_id=1)
        self.assertEqual(len(proctored_exam_student_history), 0)

        allowance.delete()

        proctored_exam_student_history = ProctoredExamStudentAllowanceHistory.objects.filter(user_id=1)
        self.assertEqual(len(proctored_exam_student_history), 1)


class ProctoredExamStudentAttemptTests(LoggedInTestCase):
    """
    Tests for the ProctoredExamStudentAttempt Model
    """

    def test_exam_unicode(self):
        """
        Serialize the object as a display string
        """
        proctored_exam = ProctoredExam.objects.create(
            course_id='test_course',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )

        string = six.text_type(proctored_exam)
        self.assertEqual(string, "test_course: Test Exam (inactive)")

    def test_delete_proctored_exam_attempt(self):  # pylint: disable=invalid-name
        """
        Deleting the proctored exam attempt creates an entry in the history table.
        """
        proctored_exam = ProctoredExam.objects.create(
            course_id='test_course',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )

        attempt = ProctoredExamStudentAttempt.objects.create(
            proctored_exam_id=proctored_exam.id,
            user_id=1,
            student_name="John. D",
            allowed_time_limit_mins=10,
            attempt_code="123456",
            taking_as_proctored=True,
            is_sample_attempt=True,
            external_id=1
        )

        # No entry in the History table on creation of the Allowance entry.
        attempt_history = ProctoredExamStudentAttemptHistory.objects.filter(user_id=1)
        self.assertEqual(len(attempt_history), 0)

        attempt.delete_exam_attempt()

        attempt_history = ProctoredExamStudentAttemptHistory.objects.filter(user_id=1)
        self.assertEqual(len(attempt_history), 1)

        # make sure we can ready it back with helper class method
        deleted_item = ProctoredExamStudentAttemptHistory.get_exam_attempt_by_code("123456")
        self.assertEqual(deleted_item.student_name, "John. D")

        # re-create and delete again using same attempt_cde
        attempt = ProctoredExamStudentAttempt.objects.create(
            proctored_exam_id=proctored_exam.id,
            user_id=1,
            student_name="John. D Updated",
            allowed_time_limit_mins=10,
            attempt_code="123456",
            taking_as_proctored=True,
            is_sample_attempt=True,
            external_id=1
        )

        attempt.delete_exam_attempt()

        attempt_history = ProctoredExamStudentAttemptHistory.objects.filter(user_id=1)
        self.assertEqual(len(attempt_history), 2)

        deleted_item = ProctoredExamStudentAttemptHistory.get_exam_attempt_by_code("123456")
        self.assertEqual(deleted_item.student_name, "John. D Updated")

    def test_update_proctored_exam_attempt(self):
        """
        Deleting the proctored exam attempt creates an entry in the history table.
        """
        proctored_exam = ProctoredExam.objects.create(
            course_id='test_course',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )
        attempt = ProctoredExamStudentAttempt.objects.create(
            proctored_exam_id=proctored_exam.id,
            user_id=1,
            status=ProctoredExamStudentAttemptStatus.created,
            student_name="John. D",
            allowed_time_limit_mins=10,
            attempt_code="123456",
            taking_as_proctored=True,
            is_sample_attempt=True,
            external_id=1
        )

        # No entry in the History table on creation of the Allowance entry.
        attempt_history = ProctoredExamStudentAttemptHistory.objects.filter(user_id=1)
        self.assertEqual(len(attempt_history), 0)

        # re-saving, but not changing status should not make an archive copy
        attempt.student_name = 'John. D Updated'
        attempt.save()

        attempt_history = ProctoredExamStudentAttemptHistory.objects.filter(user_id=1)
        self.assertEqual(len(attempt_history), 0)

        # change status...
        attempt.status = ProctoredExamStudentAttemptStatus.started
        attempt.save()

        attempt_history = ProctoredExamStudentAttemptHistory.objects.filter(user_id=1)
        self.assertEqual(len(attempt_history), 1)

        # make sure we can ready it back with helper class method
        updated_item = ProctoredExamStudentAttemptHistory.get_exam_attempt_by_code("123456")
        self.assertEqual(updated_item.student_name, "John. D Updated")
        self.assertEqual(updated_item.status, ProctoredExamStudentAttemptStatus.created)

    def test_get_exam_attempts(self):
        """
        Test to get all the exam attempts for a course
        """
        # Create an exam.
        proctored_exam = ProctoredExam.objects.create(
            course_id='a/b/c',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )

        # create number of exam attempts
        for i in range(90):
            ProctoredExamStudentAttempt.create_exam_attempt(
                proctored_exam.id, i, 'test_name{0}'.format(i),
                'test_attempt_code{0}'.format(i), True, False, 'test_external_id{0}'.format(i)
            )

        with self.assertNumQueries(1):
            exam_attempts = ProctoredExamStudentAttempt.objects.get_all_exam_attempts('a/b/c')
            self.assertEqual(len(exam_attempts), 90)

    def test_exam_review_policy(self):
        """
        Assert correct behavior of the Exam Policy model including archiving of updates and deletes
        """

        # Create an exam.
        proctored_exam = ProctoredExam.objects.create(
            course_id='a/b/c',
            content_id='test_content',
            exam_name='Test Exam',
            external_id='123aXqe3',
            time_limit_mins=90
        )

        policy = ProctoredExamReviewPolicy.objects.create(
            set_by_user_id=self.user.id,
            proctored_exam=proctored_exam,
            review_policy='Foo Policy',
        )

        attempt = ProctoredExamStudentAttempt.create_exam_attempt(
            proctored_exam.id,
            self.user.id,
            'test_name{0}'.format(self.user.id),
            'test_attempt_code{0}'.format(self.user.id),
            True,
            False,
            'test_external_id{0}'.format(self.user.id)
        )
        attempt.review_policy_id = policy.id
        attempt.save()

        history = ProctoredExamReviewPolicyHistory.objects.all()
        self.assertEqual(len(history), 0)

        # now update it
        policy.review_policy = 'Updated Foo Policy'
        policy.save()

        # look in history
        history = ProctoredExamReviewPolicyHistory.objects.all()
        self.assertEqual(len(history), 1)
        previous = history[0]
        self.assertEqual(previous.set_by_user_id, self.user.id)
        self.assertEqual(previous.proctored_exam_id, proctored_exam.id)
        self.assertEqual(previous.original_id, policy.id)
        self.assertEqual(previous.review_policy, 'Foo Policy')

        # now delete updated one
        deleted_id = policy.id
        policy.delete()

        # look in history
        history = ProctoredExamReviewPolicyHistory.objects.all()
        self.assertEqual(len(history), 2)
        previous = history[0]
        self.assertEqual(previous.set_by_user_id, self.user.id)
        self.assertEqual(previous.proctored_exam_id, proctored_exam.id)
        self.assertEqual(previous.original_id, deleted_id)
        self.assertEqual(previous.review_policy, 'Foo Policy')

        previous = history[1]
        self.assertEqual(previous.set_by_user_id, self.user.id)
        self.assertEqual(previous.proctored_exam_id, proctored_exam.id)
        self.assertEqual(previous.original_id, deleted_id)
        self.assertEqual(previous.review_policy, 'Updated Foo Policy')

        # assert that we cannot delete history!
        with self.assertRaises(NotImplementedError):
            previous.delete()

        # now delete attempt, to make sure we preserve the policy_id in the archive table
        attempt.delete()

        attempts = ProctoredExamStudentAttemptHistory.objects.all()
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].review_policy_id, deleted_id)


@ddt.ddt
class CourseBlockHardwareCheckerTest(LoggedInTestCase):
    """
    Tests for the CourseBlockHardwareChecker model and its methods.

    This test suite comprehensively verifies the functionality of the
    `CourseBlockHardwareChecker` model, including its unique constraints,
    record creation, and the behavior of the `are_hardwares_enabled` method
    for both updating existing records and creating new ones.
    """

    def setUp(self):
        super().setUp()
        self.user_id = 99
        self.content_id_1 = 'block-v1:Org+Course+TestBlock1'
        self.content_id_2 = 'block-v1:Org+Course+TestBlock2'

        self.record_data_1 = {
            'user_id': self.user_id,
            'content_id': self.content_id_1,
            'is_checking_audio_enabled': False,
            'is_checking_microphone_enabled': True,
            'is_checking_camera_enabled': False,
        }

        self.record_data_2 = {
            'user_id': self.user_id,
            'content_id': self.content_id_2,
            'is_checking_audio_enabled': True,
            'is_checking_microphone_enabled': True,
            'is_checking_camera_enabled': False,
        }

    def test_unique_together_prevention(self):
        """
        Verify that duplicate entries are prevented by unique_together constraint.

        It attempts to create a second record with the same `user_id` and `content_id`
        as an existing record. It asserts that an `IntegrityError`is raised to prevent duplicates.
        The total count of records should be unchanged.
        """
        record_1 = CourseBlockHardwareChecker.objects.create(**self.record_data_1)
        self.assertIsNotNone(record_1.id)
        self.assertEqual(CourseBlockHardwareChecker.objects.count(), 1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CourseBlockHardwareChecker.objects.create(**self.record_data_1)
        self.assertEqual(CourseBlockHardwareChecker.objects.count(), 1)

    def test_different_records_can_be_created(self):
        """
        Verify that records with different of user_id and content_id can be created.

        It checks the creation new record with a unique combination of `user_id` and `content_id`
        (different from previously created record) without errors.
        It asserts that the total count of records increased.
        """
        CourseBlockHardwareChecker.objects.create(**self.record_data_1)
        CourseBlockHardwareChecker.objects.create(**self.record_data_2)
        self.assertEqual(CourseBlockHardwareChecker.objects.count(), 2)

    @ddt.data(
        (
            'microphone_check',
            {'is_checking_microphone_enabled': False}, 'microphone',
            ['is_checking_microphone_enabled'], 'is_checking_microphone_enabled', True, False
        ),
        (
            'headphones_check',
            {'is_checking_audio_enabled': False}, 'headphones',
            ['is_checking_audio_enabled'], 'is_checking_audio_enabled', True, False
        ),
        (
            'camera_check',
            {'is_checking_camera_enabled': False}, 'camera',
            ['is_checking_camera_enabled'], 'is_checking_camera_enabled', True, False
        ),
        (
            'non_existent_checker',
            {'is_checking_audio_enabled': False}, 'non_existent_hardware',
            ['is_checking_audio_enabled'], None, None, True
        ),
        (
            'empty_enabled_hardwares',
            {'is_checking_audio_enabled': False}, 'headphones',
            [], None, None, False),
    )
    @ddt.unpack
    def test_are_hardwares_enabled_updates_existing_record(
            self, test_name,
            initial_field_states, hardware_checked_param,
            enabled_hardwares_param, expected_updated_field,
            expected_updated_value, expected_return_value
    ):
        """
        Verify that `are_hardwares_enabled` updates an existing record and returns correct status.

        This test uses a data provider to test various scenarios for `are_hardwares_enabled`.
        It asserts that:
        1. No new record is created when calling with existing `user_id` and `content_id`.
        2. The specified `hardware_checked` field is correctly updated on the existing record
           if `hardware_checked_param` is valid.
        3. The method returns the expected boolean status based on the `enabled_hardwares` list.
        """
        current_record_initial_data = self.record_data_1.copy()
        current_record_initial_data.update(initial_field_states)
        record_1 = CourseBlockHardwareChecker.objects.create(**current_record_initial_data)
        record_1.refresh_from_db()

        initial_count = CourseBlockHardwareChecker.objects.count()
        self.assertEqual(initial_count, 1)

        initial_audio_enabled = record_1.is_checking_audio_enabled
        initial_microphone_enabled = record_1.is_checking_microphone_enabled
        initial_camera_enabled = record_1.is_checking_camera_enabled

        result = CourseBlockHardwareChecker.are_hardwares_enabled(
            user_id=self.user_id,
            content_id=self.content_id_1,
            enabled_hardwares=enabled_hardwares_param,
            hardware_checked=hardware_checked_param
        )
        record_1.refresh_from_db()

        self.assertEqual(CourseBlockHardwareChecker.objects.count(), initial_count)

        if expected_updated_field:
            self.assertEqual(
                getattr(record_1, expected_updated_field), expected_updated_value,
                "Test '{0}': Expected field '{1}' to be {2}.".format(
                    test_name, expected_updated_field, expected_updated_value
                )
            )
        else:
            self.assertEqual(
                record_1.is_checking_audio_enabled, initial_audio_enabled,
                "Test '{0}': Audio enabled should not change.".format(test_name)
            )
            self.assertEqual(
                record_1.is_checking_microphone_enabled, initial_microphone_enabled,
                "Test '{0}': Microphone enabled should not change.".format(test_name)
            )
            self.assertEqual(
                record_1.is_checking_camera_enabled, initial_camera_enabled,
                "Test '{0}': Camera enabled should not change.".format(test_name)
            )

        self.assertEqual(
            result, expected_return_value,
            "Test '{0}': Expected return value {1}".format(test_name, expected_return_value)
        )
