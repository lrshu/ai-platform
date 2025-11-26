"""
Validation utilities for the employee onboarding system.
"""

from typing import Dict, List, Any, Tuple
import re
from ..models import EducationLevel
from ..utils.exceptions import ValidationError, log_info, log_error

class InputValidator:
    """Utility class for validating input data."""

    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
        """
        Validate a name field.

        Args:
            name: Name to validate
            field_name: Name of the field for error messages

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, f"{field_name} is required"

        name = name.strip()

        if len(name) > 50:
            return False, f"{field_name} is too long (maximum 50 characters)"

        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            return False, f"{field_name} contains invalid characters"

        return True, ""

    @staticmethod
    def validate_school(school: str) -> Tuple[bool, str]:
        """
        Validate school name.

        Args:
            school: School name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not school or not school.strip():
            return False, "School/Institution is required"

        school = school.strip()

        if len(school) > 100:
            return False, "School name is too long (maximum 100 characters)"

        return True, ""

    @staticmethod
    def validate_education_level(education_level: str) -> Tuple[bool, str]:
        """
        Validate education level.

        Args:
            education_level: Education level to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not education_level:
            return False, "Education level is required"

        valid_levels = [level.value for level in EducationLevel]
        if education_level not in valid_levels:
            return False, f"Invalid education level. Valid options: {', '.join(valid_levels)}"

        return True, ""

    @staticmethod
    def validate_position(position: str) -> Tuple[bool, str]:
        """
        Validate job position.

        Args:
            position: Position to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not position:
            return False, "Job position is required"

        # Valid positions (in a real system, this would come from a database)
        valid_positions = [
            'software_engineer',
            'product_manager',
            'hr_specialist',
            'admin_assistant'
        ]

        if position not in valid_positions:
            return False, f"Invalid position. Valid options: {', '.join(valid_positions)}"

        return True, ""

    @staticmethod
    def validate_session_id(session_id: str) -> Tuple[bool, str]:
        """
        Validate session ID format.

        Args:
            session_id: Session ID to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not session_id:
            return False, "Session ID is required"

        # Simple UUID validation (in a real system, you might want more robust validation)
        if len(session_id) < 10:
            return False, "Invalid session ID format"

        return True, ""

    @staticmethod
    def validate_file_upload(file_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate file upload data.

        Args:
            file_data: File data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_data:
            return False, "No file data provided"

        if 'filename' not in file_data:
            return False, "File name is required"

        if 'content_type' not in file_data:
            return False, "File content type is required"

        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if file_data['content_type'] not in allowed_types:
            return False, f"Invalid file type. Allowed types: {', '.join(allowed_types)}"

        # Check file size (if provided)
        if 'size' in file_data and file_data['size'] > 10 * 1024 * 1024:  # 10MB
            return False, "File is too large (maximum 10MB)"

        return True, ""

    @staticmethod
    def validate_employee_data(data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Validate complete employee data.

        Args:
            data: Employee data to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate first name
        if 'first_name' in data:
            is_valid, error_msg = InputValidator.validate_name(data['first_name'], "First name")
            if not is_valid:
                errors.append({'field': 'first_name', 'message': error_msg})

        # Validate last name
        if 'last_name' in data:
            is_valid, error_msg = InputValidator.validate_name(data['last_name'], "Last name")
            if not is_valid:
                errors.append({'field': 'last_name', 'message': error_msg})

        # Validate school
        if 'school' in data:
            is_valid, error_msg = InputValidator.validate_school(data['school'])
            if not is_valid:
                errors.append({'field': 'school', 'message': error_msg})

        # Validate education level
        if 'education_level' in data:
            is_valid, error_msg = InputValidator.validate_education_level(data['education_level'])
            if not is_valid:
                errors.append({'field': 'education_level', 'message': error_msg})

        # Validate position
        if 'position' in data:
            is_valid, error_msg = InputValidator.validate_position(data['position'])
            if not is_valid:
                errors.append({'field': 'position', 'message': error_msg})

        return errors

# Global validator instance
validator = InputValidator()