"""
Base models and enums for the employee onboarding system.
"""

from enum import Enum
from ..utils.database import Base

# Enums
class EducationLevel(str, Enum):
    HIGH_SCHOOL = "HIGH_SCHOOL"
    ASSOCIATE = "ASSOCIATE"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    DOCTORATE = "DOCTORATE"
    OTHER = "OTHER"

class OnboardingStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    ID_UPLOAD_PENDING = "ID_UPLOAD_PENDING"
    ID_VERIFIED = "ID_VERIFIED"
    INFORMATION_COLLECTION = "INFORMATION_COLLECTION"
    RESPONSIBILITIES_REVIEW = "RESPONSIBILITIES_REVIEW"
    PERMISSIONS_PROVISIONING = "PERMISSIONS_PROVISIONING"
    COMPLETED = "COMPLETED"

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class AccountType(str, Enum):
    EMAIL = "EMAIL"
    GIT = "GIT"

# Import models
from .employee import Employee
from .onboarding_checklist import OnboardingChecklist
from .id_photo import IDPhoto
from .credentials import AccountCredentials

# Make models available at package level
__all__ = [
    'Employee',
    'OnboardingChecklist',
    'IDPhoto',
    'AccountCredentials',
    'EducationLevel',
    'OnboardingStatus',
    'VerificationStatus',
    'AccountType',
    'Base'
]