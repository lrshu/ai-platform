# Data Model: Employee Onboarding System

## Employee

Represents a new hire going through the onboarding process.

### Attributes
- `id`: Unique identifier (UUID)
- `first_name`: First name of the employee
- `last_name`: Last name of the employee
- `id_number`: Government-issued ID number extracted from ID photo
- `school`: Graduated school/institution
- `education_level`: Education qualification (e.g., Bachelor's, Master's, PhD)
- `position`: Selected job position
- `onboarding_status`: Current state in the onboarding process
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last updated

### Relationships
- Has one ID Photo
- Has one Onboarding Checklist
- May have multiple Account Credentials (email, git)

## ID Photo

Digital image uploaded by employee for identity verification.

### Attributes
- `id`: Unique identifier (UUID)
- `employee_id`: Reference to associated Employee
- `file_path`: Path to stored image file
- `verification_status`: Status of verification (pending, verified, rejected)
- `verification_notes`: Notes from verification process
- `uploaded_at`: Timestamp when photo was uploaded

### Relationships
- Belongs to one Employee

## Position

Job role with associated responsibilities and required permissions.

### Attributes
- `id`: Unique identifier (UUID)
- `name`: Position title
- `department`: Department the position belongs to
- `responsibilities`: Description of position responsibilities
- `required_permissions`: List of permissions needed for this position

### Relationships
- Can be associated with multiple Employees

## Onboarding Checklist

Status tracker for employee's progress through onboarding steps.

### Attributes
- `id`: Unique identifier (UUID)
- `employee_id`: Reference to associated Employee
- `identity_verified`: Boolean indicating if ID has been verified
- `information_collected`: Boolean indicating if personal info has been collected
- `responsibilities_shown`: Boolean indicating if position responsibilities have been shown
- `permissions_granted`: Boolean indicating if necessary accounts have been provisioned
- `post_tasks_reminded`: Boolean indicating if post-onboarding tasks have been shared
- `completed`: Boolean indicating if entire onboarding process is complete

### Relationships
- Belongs to one Employee

## Account Credentials

Provisioned access information generated for employee based on their position.

### Attributes
- `id`: Unique identifier (UUID)
- `employee_id`: Reference to associated Employee
- `account_type`: Type of account (email, git)
- `username`: Assigned username
- `provisioned_at`: Timestamp when account was provisioned

### Relationships
- Belongs to one Employee

## Enums

### EducationLevel
- HIGH_SCHOOL
- ASSOCIATE
- BACHELOR
- MASTER
- DOCTORATE
- OTHER

### OnboardingStatus
- NOT_STARTED
- ID_UPLOAD_PENDING
- ID_VERIFIED
- INFORMATION_COLLECTION
- RESPONSIBILITIES_REVIEW
- PERMISSIONS_PROVISIONING
- COMPLETED

### VerificationStatus
- PENDING
- VERIFIED
- REJECTED