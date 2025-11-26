"""
API endpoints for employee information collection.
"""

from typing import Dict, Any
from flask import Blueprint, request, jsonify
from ..agents.information_collection import information_collection_agent
from ..repositories.employee_repository import get_employee_repository
from ..utils.database import get_db
from ..utils.exceptions import ValidationError, log_info, log_error
from ..utils.validators import validator

# Create blueprint for information endpoints
information_bp = Blueprint('information', __name__, url_prefix='/api/v1/onboarding/sessions')

@information_bp.route('/<session_id>/information', methods=['GET'])
def get_information_form(session_id: str):
    """
    Get the information collection form.

    Response:
    {
        "employee_id": "uuid",
        "employee_name": "string",
        "fields": [
            {
                "name": "string",
                "label": "string",
                "type": "text|select",
                "required": true|false,
                "placeholder": "string (optional)",
                "options": [  // For select type
                    {
                        "value": "string",
                        "label": "string"
                    }
                ]
            }
        ],
        "next_step": "collect_information"
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

        # Request form from information collection agent
        form = information_collection_agent.request_employee_information(session_id)

        if 'error' in form:
            return jsonify({
                'error': {
                    'code': 'FORM_ERROR',
                    'message': form['error'],
                    'details': 'Failed to generate information collection form'
                }
            }), 500

        return jsonify(form), 200

    except Exception as e:
        log_error(e, f"Failed to get information form for session {session_id}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500

@information_bp.route('/<session_id>/information', methods=['POST'])
def submit_information(session_id: str):
    """
    Submit employee personal information.

    Request Body:
    {
        "school": "string",
        "education_level": "HIGH_SCHOOL|ASSOCIATE|BACHELOR|MASTER|DOCTORATE|OTHER",
        "position": "string"
    }

    Response:
    {
        "information_id": "uuid",
        "validation_result": {
            "valid": true,
            "errors": []|[{ "field": "string", "message": "string" }]
        },
        "next_step": "show_responsibilities|correct_information"
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

        # Get request data
        data = request.get_json()

        if not data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body is required',
                    'details': 'Request must contain employee information'
                }
            }), 400

        # Validate information
        validation_result = information_collection_agent.validate_employee_information(session_id, data)

        if not validation_result['valid']:
            # Handle validation errors
            feedback = information_collection_agent.handle_validation_errors(session_id, validation_result['errors'])
            return jsonify(feedback), 400

        # Process validated information
        result = information_collection_agent.process_employee_information(session_id, data)

        if not result['valid']:
            # Handle processing errors
            return jsonify({
                'error': {
                    'code': 'PROCESSING_ERROR',
                    'message': 'Failed to process information',
                    'details': result.get('errors', [])
                }
            }), 500

        # Get database session and repository
        db = next(get_db())
        repo = get_employee_repository(db)

        # Get employee to return information ID
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

        db.close()

        return jsonify({
            'information_id': employee.id,
            'validation_result': {
                'valid': True,
                'errors': []
            },
            'next_step': result.get('next_step', 'show_responsibilities')
        }), 201

    except Exception as e:
        log_error(e, f"Failed to submit information for session {session_id}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500