"""
ID verification service for processing employee ID photos.
"""

from typing import Dict, Optional, Tuple
from ..models import VerificationStatus
from ..repositories.employee_repository import get_employee_repository
from ..utils.database import get_db
from ..utils.exceptions import ExternalServiceError, ValidationError, log_info, log_error
from ..services.qwen_client import qwen_client

class IDVerificationService:
    """Service for verifying employee ID photos."""

    def __init__(self):
        """Initialize ID verification service."""
        pass

    def verify_id_photo(self, employee_id: str, image_path: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Verify an ID photo using Qwen vision-language model.

        Args:
            employee_id: Employee ID
            image_path: Path to the ID photo file

        Returns:
            Tuple of (is_valid, error_message, extracted_data)
        """
        try:
            log_info(f"Verifying ID photo for employee {employee_id}")

            # Check image quality and format
            quality_check = self._check_image_quality(image_path)
            if not quality_check[0]:
                return False, quality_check[1], None

            # Use Qwen VL model to extract information
            extracted_data = qwen_client.extract_id_information(image_path)

            # Validate extracted data
            validation_result = self._validate_extracted_data(extracted_data)
            if not validation_result[0]:
                return False, validation_result[1], extracted_data

            log_info(f"ID photo verified successfully for employee {employee_id}")
            return True, None, extracted_data

        except ExternalServiceError as e:
            log_error(e, f"External service error during ID verification for employee {employee_id}")
            return False, f"Failed to process ID photo: {str(e)}", None
        except Exception as e:
            log_error(e, f"Unexpected error during ID verification for employee {employee_id}")
            return False, f"Unexpected error: {str(e)}", None

    def _check_image_quality(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check image quality for ID verification.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (is_valid, error_message)
        """
        # In a real implementation, we would check:
        # - Image resolution
        # - File size
        # - Image format
        # - Blur detection
        # - Lighting conditions

        # For now, we'll just check if the file exists
        try:
            with open(image_path, 'rb') as f:
                # Check file size (should be reasonable for an ID photo)
                f.seek(0, 2)  # Seek to end
                size = f.tell()
                if size > 10 * 1024 * 1024:  # 10MB limit
                    return False, "Image file too large (maximum 10MB)"

                # Check if it's a valid image by trying to read a few bytes
                f.seek(0)
                header = f.read(10)
                if not header:
                    return False, "Invalid image file"

            return True, None
        except FileNotFoundError:
            return False, "Image file not found"
        except Exception as e:
            return False, f"Failed to read image file: {str(e)}"

    def _validate_extracted_data(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate extracted ID data.

        Args:
            data: Extracted data from ID photo

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not data:
            return False, "No data extracted from ID photo"

        # Check for required fields
        required_fields = ['first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"

        # Validate field lengths
        if len(data['first_name']) > 50:
            return False, "First name too long"
        if len(data['last_name']) > 50:
            return False, "Last name too long"

        return True, None

    def process_id_verification(self, employee_id: str, image_path: str) -> Dict:
        """
        Process complete ID verification workflow.

        Args:
            employee_id: Employee ID
            image_path: Path to the ID photo file

        Returns:
            Verification result dictionary
        """
        # Get database session and repository
        db = next(get_db())
        repo = get_employee_repository(db)

        try:
            # Update ID photo status to pending
            repo.update_id_photo_status(employee_id, VerificationStatus.PENDING.value)

            # Verify the ID photo
            is_valid, error_message, extracted_data = self.verify_id_photo(employee_id, image_path)

            if is_valid:
                # Update ID photo status to verified
                repo.update_id_photo_status(
                    employee_id,
                    VerificationStatus.VERIFIED.value,
                    "ID photo verified successfully"
                )

                # Update employee with extracted data
                if extracted_data:
                    update_fields = {}
                    if 'first_name' in extracted_data:
                        update_fields['first_name'] = extracted_data['first_name']
                    if 'last_name' in extracted_data:
                        update_fields['last_name'] = extracted_data['last_name']
                    if 'id_number' in extracted_data:
                        update_fields['id_number'] = extracted_data['id_number']

                    if update_fields:
                        repo.update_employee(employee_id, **update_fields)

                # Update onboarding checklist
                repo.update_onboarding_checklist(employee_id, identity_verified=True)

                return {
                    'status': 'success',
                    'message': 'ID photo verified successfully',
                    'data': extracted_data
                }
            else:
                # Update ID photo status to rejected
                repo.update_id_photo_status(
                    employee_id,
                    VerificationStatus.REJECTED.value,
                    error_message
                )

                return {
                    'status': 'error',
                    'message': error_message,
                    'data': None
                }

        except Exception as e:
            # Update ID photo status to rejected with error
            repo.update_id_photo_status(
                employee_id,
                VerificationStatus.REJECTED.value,
                f"Processing error: {str(e)}"
            )

            log_error(e, f"Failed to process ID verification for employee {employee_id}")
            return {
                'status': 'error',
                'message': f"Failed to process ID verification: {str(e)}",
                'data': None
            }
        finally:
            db.close()

# Global ID verification service instance
id_verification_service = IDVerificationService()