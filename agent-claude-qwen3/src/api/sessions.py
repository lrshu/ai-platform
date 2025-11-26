"""
API endpoints for session management.
"""

from typing import Dict, Any
from flask import Blueprint, request, jsonify
from ..services.session_service import session_service
from ..utils.exceptions import ValidationError, log_error
from ..utils.validators import validator

# Create blueprint for session endpoints
sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/v1/onboarding/sessions')

@sessions_bp.route('', methods=['POST'])
def create_session():
    """
    Create a new onboarding session.

    Request Body:
    {
        "employee": {
            "first_name": "string",
            "last_name": "string"
        }
    }

    Response:
    {
        "session_id": "uuid",
        "employee_id": "uuid",
        "checklist": {
            "id": "uuid",
            "identity_verified": false,
            "information_collected": false,
            "responsibilities_shown": false,
            "permissions_granted": false,
            "post_tasks_reminded": false,
            "completed": false
        },
        "next_step": "upload_id_photo"
    }
    """
    try:
        # Get request data
        data = request.get_json()

        if not data or 'employee' not in data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Employee information is required',
                    'details': 'Request body must contain employee object with first_name and last_name'
                }
            }), 400

        employee_data = data['employee']

        # Validate required fields using validator
        first_name = employee_data.get('first_name', '').strip()
        last_name = employee_data.get('last_name', '').strip()

        is_valid, error_msg = validator.validate_name(first_name, "First name")
        if not is_valid:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': error_msg,
                    'details': 'Invalid first name format'
                }
            }), 400

        is_valid, error_msg = validator.validate_name(last_name, "Last name")
        if not is_valid:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': error_msg,
                    'details': 'Invalid last name format'
                }
            }), 400

        # Create session
        session_info = session_service.create_session(first_name, last_name)

        if 'error' in session_info:
            return jsonify({
                'error': {
                    'code': 'SESSION_CREATION_FAILED',
                    'message': session_info['error'],
                    'details': 'Failed to create onboarding session'
                }
            }), 500

        return jsonify(session_info), 201

    except Exception as e:
        log_error(e, "Failed to create session")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500

@sessions_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """
    Get session information.

    Response:
    {
        "employee_id": "uuid",
        "onboarding_status": "string",
        "checklist": {
            "id": "uuid",
            "identity_verified": true|false,
            "information_collected": true|false,
            "responsibilities_shown": true|false,
            "permissions_granted": true|false,
            "post_tasks_reminded": true|false,
            "completed": true|false
        },
        "next_step": "string"
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

        # Get session
        session_info = session_service.get_session(session_id)

        if not session_info:
            return jsonify({
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': 'Session not found',
                    'details': f'No session found with ID: {session_id}'
                }
            }), 404

        if 'error' in session_info:
            return jsonify({
                'error': {
                    'code': 'SESSION_ERROR',
                    'message': session_info['error'],
                    'details': 'Failed to retrieve session information'
                }
            }), 500

        return jsonify(session_info), 200

    except Exception as e:
        log_error(e, f"Failed to get session {session_id}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500

@sessions_bp.route('/<session_id>/status', methods=['GET'])
def get_session_status(session_id: str):
    """
    Get session status (simplified version of get_session).

    Response:
    {
        "status": "string",
        "next_step": "string"
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

        # Get session
        session_info = session_service.get_session(session_id)

        if not session_info:
            return jsonify({
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': 'Session not found',
                    'details': f'No session found with ID: {session_id}'
                }
            }), 404

        if 'error' in session_info:
            return jsonify({
                'error': {
                    'code': 'SESSION_ERROR',
                    'message': session_info['error'],
                    'details': 'Failed to retrieve session status'
                }
            }), 500

        return jsonify({
            'status': session_info.get('onboarding_status', 'unknown'),
            'next_step': session_info.get('next_step', 'unknown')
        }), 200

    except Exception as e:
        log_error(e, f"Failed to get session status {session_id}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500