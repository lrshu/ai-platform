"""
API router and server setup for the employee onboarding system.
"""

from flask import Flask
from .sessions import sessions_bp
from .id_photo import id_photo_bp
from .information import information_bp
from ..utils.exceptions import log_info, log_error

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(sessions_bp)
    app.register_blueprint(id_photo_bp)
    app.register_blueprint(information_bp)

    # Root endpoint
    @app.route('/')
    def index():
        return {
            'message': 'Employee Onboarding API',
            'version': '1.0.0',
            'endpoints': {
                'sessions': '/api/v1/onboarding/sessions',
                'id_photo': '/api/v1/onboarding/sessions/<session_id>/id-photo',
                'information': '/api/v1/onboarding/sessions/<session_id>/information'
            }
        }

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Endpoint not found',
                'details': str(error)
            }
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        log_error(error, "Internal server error")
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': 'An unexpected error occurred'
            }
        }, 500

    return app

def run_server(host='127.0.0.1', port=8000, debug=False):
    """Run the API server."""
    try:
        app = create_app()
        log_info(f"Starting server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        log_error(e, "Failed to start server")
        raise

if __name__ == '__main__':
    run_server()