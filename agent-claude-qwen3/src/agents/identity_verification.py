"""
Identity verification agent for processing employee ID photos.
"""

from typing import Dict, Any
from ..services.id_verification_service import id_verification_service
from ..agents.supervisor import supervisor_agent
from ..utils.exceptions import log_info, log_error

class IdentityVerificationAgent:
    """Agent responsible for verifying employee identity through ID photos."""

    def __init__(self):
        """Initialize identity verification agent."""
        pass

    def request_id_photo_upload(self, employee_id: str) -> Dict[str, Any]:
        """
        Request employee to upload ID photo.

        Args:
            employee_id: Employee ID

        Returns:
            Instructions for ID photo upload
        """
        try:
            log_info(f"Requesting ID photo upload for employee {employee_id}")

            return {
                'employee_id': employee_id,
                'instruction': 'Please upload a clear photo of your government-issued ID.',
                'requirements': {
                    'format': 'JPEG, PNG, or PDF',
                    'size_limit': 'Maximum 10MB',
                    'quality': 'Clear and well-lit',
                    'content': 'Full ID visible, no glare or shadows'
                },
                'next_step': 'upload_id_photo'
            }

        except Exception as e:
            log_error(e, f"Failed to request ID photo upload for employee {employee_id}")
            return {
                'error': f"Failed to request ID photo upload: {str(e)}"
            }

    def process_id_photo(self, employee_id: str, image_path: str) -> Dict[str, Any]:
        """
        Process uploaded ID photo for verification.

        Args:
            employee_id: Employee ID
            image_path: Path to the uploaded ID photo

        Returns:
            Verification result
        """
        try:
            log_info(f"Processing ID photo for employee {employee_id}")

            # Process ID verification
            result = id_verification_service.process_id_verification(employee_id, image_path)

            # If verification was successful, notify supervisor
            if result.get('status') == 'success':
                # Update supervisor about completed step
                supervisor_agent.update_onboarding_step(employee_id, 'identity_verified')

            return result

        except Exception as e:
            log_error(e, f"Failed to process ID photo for employee {employee_id}")
            return {
                'status': 'error',
                'message': f"Failed to process ID photo: {str(e)}",
                'data': None
            }

    def handle_verification_error(self, employee_id: str, error_message: str) -> Dict[str, Any]:
        """
        Handle ID verification errors and provide guidance.

        Args:
            employee_id: Employee ID
            error_message: Error message from verification

        Returns:
            Guidance for correcting the issue
        """
        try:
            log_info(f"Handling verification error for employee {employee_id}: {error_message}")

            guidance = {
                'employee_id': employee_id,
                'error': error_message,
                'guidance': self._get_correction_guidance(error_message),
                'next_step': 'retry_upload'
            }

            return guidance

        except Exception as e:
            log_error(e, f"Failed to handle verification error for employee {employee_id}")
            return {
                'error': f"Failed to handle verification error: {str(e)}"
            }

    def _get_correction_guidance(self, error_message: str) -> str:
        """
        Provide specific guidance based on error message.

        Args:
            error_message: Error message

        Returns:
            Correction guidance
        """
        error_message = error_message.lower()

        if 'too large' in error_message:
            return "Please reduce the file size of your ID photo. Maximum size is 10MB."
        elif 'not found' in error_message:
            return "Please make sure you have selected a valid ID photo file to upload."
        elif 'blur' in error_message or 'quality' in error_message:
            return "Please take a new photo with better lighting and focus. Make sure the ID is flat and fully visible."
        elif 'invalid image' in error_message:
            return "Please ensure you are uploading a valid image file (JPEG, PNG, or PDF)."
        elif 'missing required field' in error_message:
            return "The ID photo is unclear. Please ensure all text on the ID is readable and the photo is well-lit."
        else:
            return "Please check your ID photo and try uploading again. Make sure it's clear, well-lit, and fully visible."

# Global identity verification agent instance
identity_verification_agent = IdentityVerificationAgent()