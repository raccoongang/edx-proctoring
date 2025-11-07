# edX Proctoring Module Documentation

## Functional Description

The `edx_proctoring` module in the edX platform is a comprehensive system for managing proctored exams. It provides the infrastructure for creating, configuring, and administering proctored exams, which are exams with time limits that learners complete while online proctoring software monitors their computers and behavior for activity that might be evidence of cheating.

The module serves several key functions:

1. **Exam Management**: Allows course authors to create and configure proctored exams, including setting time limits, due dates, and review policies
2. **Student Attempt Management**: Handles the workflow of student exam attempts, from initialization through completion and review
3. **Proctoring Service Integration**: Provides a pluggable backend architecture to integrate with different proctoring service providers
4. **Review Process**: Manages the review of completed proctored exams, including handling review results and updating student attempt statuses
5. **Special Allowances**: Supports special accommodations for students, such as additional time or review policy exceptions
6. **Practice Exams**: Enables students to take practice proctored exams to familiarize themselves with the proctoring software and process

The module is designed to be flexible and extensible, supporting different proctoring service providers through a backend plugin architecture. It includes a comprehensive API for managing all aspects of the proctoring process and integrates with other components of the edX platform such as the courseware, grades, and certificates systems.

## Information Models

### Key Models

#### ProctoredExam
The `ProctoredExam` model represents a proctored exam in a course:

- **Course/Content ID**: Identifiers for the course and specific content item
- **Exam Name**: The name of the exam
- **Time Limit**: The time limit for the exam in minutes
- **Due Date**: The deadline for completing the exam
- **Proctoring Flags**: Indicators for whether the exam is proctored, a practice exam, and active
- **External ID**: Identifier used by the proctoring service provider
- **Backend**: The proctoring service provider to use for this exam
- **Hide After Due**: Whether to hide the exam after the due date

This model is the foundation for defining proctored exams in courses.

#### ProctoredExamStudentAttempt
The `ProctoredExamStudentAttempt` model represents a student's attempt at a proctored exam:

- **User**: Reference to the student taking the exam
- **Proctored Exam**: Reference to the ProctoredExam
- **Status**: Current status of the attempt (e.g., created, started, submitted, verified, rejected)
- **Started/Completed At**: Timestamps for when the attempt was started and completed
- **Allowed Time Limit**: The time limit for this specific attempt, which may include accommodations
- **Taking As Proctored**: Whether the student is taking the exam as proctored or timed
- **External ID**: Identifier used by the proctoring service provider
- **Attempt Code**: Unique code for this attempt

This model tracks the entire lifecycle of a student's exam attempt.

#### ProctoredExamStudentAllowance
The `ProctoredExamStudentAllowance` model represents special accommodations for students:

- **User**: Reference to the student receiving the allowance
- **Proctored Exam**: Reference to the ProctoredExam
- **Key**: The type of allowance (e.g., additional_time_granted, review_policy_exception)
- **Value**: The value of the allowance (e.g., number of additional minutes)

This model enables instructors to provide accommodations for students with special needs.

#### ProctoredExamReviewPolicy
The `ProctoredExamReviewPolicy` model defines the review policy for a proctored exam:

- **Proctored Exam**: Reference to the ProctoredExam
- **Set By User**: Reference to the user who set the policy
- **Review Policy**: The policy for reviewing the exam, typically in JSON format

This model allows instructors to define how proctored exams should be reviewed.

#### ProctoredExamSoftwareSecureReview
The `ProctoredExamSoftwareSecureReview` model represents a review of a proctored exam attempt:

- **Attempt Code**: Reference to the attempt being reviewed
- **Review Status**: The status of the review (e.g., clean, violation, suspicious)
- **Raw Data**: The raw data from the review
- **Video URL**: URL to the proctoring video
- **Reviewed By**: Reference to the user who reviewed the attempt

This model stores the results of proctoring service reviews.

### Status Classes

The module defines several status classes to manage the state of exam attempts and reviews:

- **ProctoredExamStudentAttemptStatus**: Defines the possible states of a student's exam attempt
- **ReviewStatus**: Defines the possible states of an exam review
- **SoftwareSecureReviewStatus**: Defines the possible states of a Software Secure review

These classes provide constants and utility methods for working with statuses.

## Database Structure

The edx_proctoring module uses several database tables to store its data:

1. **proctoring_proctoredexam**: Stores proctored exam definitions
   - id: Primary key
   - course_id: Course identifier
   - content_id: Content identifier within the course
   - exam_name: Name of the exam
   - time_limit_mins: Time limit in minutes
   - is_proctored: Whether the exam is proctored
   - is_practice_exam: Whether the exam is a practice exam
   - is_active: Whether the exam is active
   - external_id: Identifier used by the proctoring service
   - backend: Proctoring service provider
   - created/modified: Timestamps

2. **proctoring_proctoredexamstudentattempt**: Stores student exam attempts
   - id: Primary key
   - proctored_exam_id: Foreign key to proctored_exam
   - user_id: Foreign key to auth_user
   - status: Current status of the attempt
   - started_at/completed_at: Timestamps
   - allowed_time_limit_mins: Time limit for this attempt
   - attempt_code: Unique code for this attempt
   - external_id: Identifier used by the proctoring service
   - taking_as_proctored: Whether the student is taking as proctored
   - is_sample_attempt: Whether this is a practice attempt
   - created/modified: Timestamps

3. **proctoring_proctoredexamstudentallowance**: Stores student allowances
   - id: Primary key
   - proctored_exam_id: Foreign key to proctored_exam
   - user_id: Foreign key to auth_user
   - key: Type of allowance
   - value: Value of the allowance
   - created/modified: Timestamps

4. **proctoring_proctoredexamreviewpolicy**: Stores exam review policies
   - id: Primary key
   - proctored_exam_id: Foreign key to proctored_exam
   - set_by_user_id: Foreign key to auth_user
   - review_policy: Policy for reviewing the exam
   - created/modified: Timestamps

5. **proctoring_proctoredexamsoftwaresecurereview**: Stores exam reviews
   - id: Primary key
   - attempt_code: Reference to the attempt
   - review_status: Status of the review
   - raw_data: Raw data from the review
   - video_url: URL to the proctoring video
   - reviewed_by_id: Foreign key to auth_user
   - created/modified: Timestamps

6. **History Tables**: Several history tables track changes to the main models
   - proctoring_proctoredexamstudentattempthistory
   - proctoring_proctoredexamstudentallowancehistory
   - proctoring_proctoredexamreviewpolicyhistory
   - proctoring_proctoredexamsoftwaresecurereviewhistory

The database schema includes appropriate indexes and constraints to ensure data integrity and query performance.

## Interfaces

### API Functions

The module provides a comprehensive API for managing proctored exams:

#### Exam Management
- **create_exam**: Creates a new proctored exam
- **update_exam**: Updates an existing proctored exam
- **get_exam_by_id/get_exam_by_content_id**: Retrieves exam information
- **get_all_exams_for_course**: Gets all exams for a course

#### Review Policy Management
- **create_exam_review_policy**: Creates a review policy for an exam
- **update_review_policy**: Updates an existing review policy
- **remove_review_policy**: Removes a review policy
- **get_review_policy_by_exam_id**: Retrieves a review policy

#### Student Attempt Management
- **create_exam_attempt**: Creates a new exam attempt for a student
- **start_exam_attempt**: Starts an exam attempt
- **stop_exam_attempt**: Stops an exam attempt
- **update_attempt_status**: Updates the status of an attempt
- **get_exam_attempt**: Retrieves information about an attempt
- **get_all_exam_attempts**: Gets all attempts for a course
- **remove_exam_attempt**: Removes an exam attempt

#### Allowance Management
- **add_allowance_for_user**: Adds an allowance for a student
- **get_allowances_for_course**: Gets all allowances for a course
- **remove_allowance_for_user**: Removes an allowance for a student

#### Student View
- **get_student_view**: Gets the appropriate view for a student based on their status

### REST API Endpoints

The module exposes several REST API endpoints:

#### Exam Management
- **ProctoredExamView**: CRUD operations for proctored exams
- **ExamAllowanceView**: CRUD operations for exam allowances

#### Student Attempt Management
- **StudentProctoredExamAttempt**: CRUD operations for a specific attempt
- **StudentProctoredExamAttemptCollection**: List and create attempts
- **StudentProctoredExamAttemptsByCourse**: List attempts for a course
- **ActiveExamsForUserView**: List active exams for a user

#### Review Management
- **ProctoredExamAttemptReviewStatus**: Update review status
- **ProctoredExamReviewCallback**: Handle callbacks from proctoring services
- **AnonymousReviewCallback**: Handle anonymous callbacks from proctoring services

#### Instructor Dashboard
- **InstructorDashboard**: Dashboard for instructors to manage proctored exams

### Backend Interface

The module defines a backend interface for integrating with different proctoring service providers:

- **ProctoredExamBackendProvider**: Base class for backend providers
- **register_backend**: Registers a backend provider
- **get_backend_provider**: Gets a backend provider by name

Implementations include:
- **SoftwareSecureBackendProvider**: Integration with Software Secure
- **MockProctoringBackendProvider**: Mock implementation for testing
- **NullBackendProvider**: No-op implementation for when proctoring is disabled

## Integration Points

The edx_proctoring module integrates with several other components in the edX platform:

### Courseware Integration
- Integrates with the courseware module to display appropriate exam interfaces
- Uses the modulestore to access course structure and content
- Provides XBlock handlers for proctored exam interactions

### Credit Eligibility
- Updates credit eligibility based on proctored exam results
- Integrates with the credit system to enforce proctoring requirements for credit courses

### Grades
- Interacts with the grades system to ensure grades are properly recorded
- Handles special cases like timed out exams or rejected attempts

### Certificates
- Affects certificate generation based on proctoring requirements
- Ensures students who fail proctoring reviews don't receive certificates

### User Authentication
- Integrates with the authentication system for secure access to proctored exams
- Handles user identity verification for proctoring

### Event Tracking
- Emits events for tracking proctored exam activities
- Provides data for analytics and monitoring

### Runtime Services
- Uses a service registry pattern to access LMS services
- Allows the proctoring module to be more loosely coupled with the LMS

## Usage Examples

### Creating a Proctored Exam

```python
from edx_proctoring.api import create_exam

# Create a proctored exam
exam_id = create_exam(
    course_id='course-v1:edX+DemoX+Demo_Course',
    content_id='block-v1:edX+DemoX+Demo_Course+type@sequential+block@exam_section',
    exam_name='Midterm Exam',
    time_limit_mins=60,
    is_proctored=True,
    is_practice_exam=False,
    is_active=True
)
```

### Adding a Time Allowance for a Student

```python
from edx_proctoring.api import add_allowance_for_user

# Add 30 minutes of additional time for a student
add_allowance_for_user(
    exam_id=1,
    user_info='student@example.com',
    key='additional_time_granted',
    value='30'
)
```

### Creating and Starting an Exam Attempt

```python
from edx_proctoring.api import create_exam_attempt, start_exam_attempt

# Create an exam attempt
create_exam_attempt(
    exam_id=1,
    user_id=123,
    taking_as_proctored=True
)

# Start the exam attempt
start_exam_attempt(
    exam_id=1,
    user_id=123
)
```

### Updating an Attempt Status

```python
from edx_proctoring.api import update_attempt_status
from edx_proctoring.statuses import ProctoredExamStudentAttemptStatus

# Mark an attempt as submitted
update_attempt_status(
    exam_id=1,
    user_id=123,
    to_status=ProctoredExamStudentAttemptStatus.submitted
)
```

### Handling a Proctoring Service Callback

```python
# In a view function handling a callback from the proctoring service
from edx_proctoring.models import ProctoredExamSoftwareSecureReview
from edx_proctoring.statuses import SoftwareSecureReviewStatus

# Create a review based on the callback data
review = ProctoredExamSoftwareSecureReview.objects.create(
    attempt_code='attempt_123',
    review_status=SoftwareSecureReviewStatus.clean,
    raw_data=json.dumps(callback_data),
    video_url='https://example.com/video'
)
# The review creation will trigger signals to update the attempt status
```