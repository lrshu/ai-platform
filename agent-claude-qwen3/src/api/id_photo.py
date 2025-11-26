"""
API endpoints for ID photo management.
"""

import os
from typing import Dict, Any
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..agents.identity_verification import identity_verification_agent
from ..repositories.employee_repository import get_employee_repository
from ..utils.database import get_db
from ..utils.exceptions import ValidationError, log_info, log_error
from ..utils.validators import validator

# Create blueprint for ID photo endpoints
id_photo_bp = Blueprint('id_photo', __name__, url_prefix='/api/v1/onboarding/sessions')

# Configuration
UPLOAD_FOLDER = 'uploads/id_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@id_photo_bp.route('/<session_id>/id-photo', methods=['POST'])
def upload_id_photo(session_id: str):
    """
    Upload an ID photo for verification.

    Form-data with file attachment

    Response:
    {
        "photo_id": "uuid",
        "verification_status": "pending",
        "next_step": "awaiting_verification"
    }
    """
    try:
        # Validate session ID
        is_valid, error_msg = validator.validate_session_id(session_id)
        if not is_valid:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': error_msg,
                    'details': 'Invalid session ID format'
                }
            }), 400

        # Check if session exists
        db = next(get_db())
        repo = get_employee_repository(db)
        employee = repo.get_employee(session_id)

        if not employee:
            db.close()
            return jsonify({
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': 'Session not found',
                    'details': f'No session found with ID: {session_id}'
                }
            }), 404

        # Check if the post request has the file part
        if 'file' not in request.files:
            db.close()
            return jsonify({
                'error': {
                    'code': 'MISSING_FILE',
                    'message': 'No file provided',
                    'details': 'Request must include a file attachment'
                }
            }), 400

        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            db.close()
            return jsonify({
                'error': {
                    'code': 'EMPTY_FILE',
                    'message': 'No file selected',
                    'details': 'Please select a file to upload'
                }
            }), 400

        # Validate file
        if not allowed_file(file.filename):
            db.close()
            return jsonify({
                'error': {
                    'code': 'INVALID_FILE_TYPE',
                    'message': 'Invalid file type',
                    'details': f'Allowed file types: {", ".join(ALLOWED_EXTENSIONS)}'
                }
            }), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        if file_length > MAX_FILE_SIZE:
            db.close()
            return jsonify({
                'error': {
                    'code': 'FILE_TOO_LARGE',
                    'message': 'File too large',
                    'details': f'Maximum file size is {MAX_FILE_SIZE} bytes'
                }
            }), 400

        # Reset file pointer to beginning
        file.seek(0)

        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            filename = f"id_photo_{session_id}.jpg"

        # Add session ID to filename to make it unique
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{session_id}{ext}"

        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Create ID photo record in database
        id_photo = repo.create_id_photo(session_id, file_path)

        db.close()

        # Request verification from identity verification agent
        identity_verification_agent.request_id_photo_upload(session_id)

        return jsonify({
            'photo_id': id_photo.id,
            'verification_status': 'pending',
            'next_step': 'awaiting_verification'
        }), 201

    except Exception as e:
        log_error(e, f"Failed to upload ID photo for session {session_id}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500

@id_photo_bp.route('/<session_id>/id-photo/status', methods=['GET'])
def get_id_verification_status(session_id: str):
    """
    Check the status of ID verification.

    Response:
    {
        "verification_status": "verified|rejected|pending",
        "verification_notes": "string|null",
        "extracted_data": {
            "first_name": "string",
            "last_name": "string",
            "id_number": "string"
        }|null,
        "next_step": "collect_information|retry_upload"
    }
    """
    try:
        # Validate session ID
        is_valid, error_msg = validator.validate_session_id(session_id)
        if not is_valid:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': error_msg,
                    'details': 'Invalid session ID format'
                }
            }), 400

        # Get database session and repository
        db = next(get_db())
        repo = get_employee_repository(db)

        # Get employee
        employee = repo.get_employee(session_id)
        if not employee:
            db.close()
            return jsonify({
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': 'Session not found',
                    'details': f'No session found with ID: {session_id}'
                }
            }), 404

        # Get ID photo
        id_photo = repo.get_id_photo(session_id)
        if not id_photo:
            db.close()
            return jsonify({
                'error': {
                    'code': 'ID_PHOTO_NOT_FOUND',
                    'message': 'ID photo not found',
                    'details': 'No ID photo has been uploaded for this session'
                }
            }), 404

        db.close()

        # Prepare response
        response = {
            'verification_status': id_photo.verification_status,
            'verification_notes': id_photo.verification_notes,
            'next_step': 'awaiting_verification' if id_photo.verification_status == 'pending' else
                        'collect_information' if id_photo.verification_status == 'verified' else
                        'retry_upload'
        }

        # Include extracted data if available and verified
        if id_photo.verification_status == 'verified' and employee.id_number:
            response['extracted_data'] = {
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'id_number': employee.id_number
            }

        return jsonify(response), 200

    except Exception as e:
        log_error(e, f"Failed to get ID verification status for session {session_id}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500