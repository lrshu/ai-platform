#!/usr/bin/env python3
"""
Employee Onboarding Multi-Agent System
"""

import argparse
import sys
from typing import Optional

# Import Flask for serve mode
try:
    from flask import Flask
    from src.api.sessions import sessions_bp
    from src.api.id_photo import id_photo_bp
    from src.api.information import information_bp
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

def chat_mode():
    """Start interactive chat mode with the onboarding agent."""
    print("Welcome to the Employee Onboarding System!")
    print("Initializing multi-agent onboarding process...")

    # Add src to path for imports
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    # Import agents
    from src.agents.supervisor import supervisor_agent
    from src.agents.identity_verification import identity_verification_agent
    from src.agents.information_collection import information_collection_agent
    from src.agents.tool_calling import tool_calling_agent
    from src.agents.qa import qa_agent

    print("\nEmployee Onboarding Assistant:")
    print("1. Start new onboarding session")
    print("2. Check onboarding status")
    print("3. Ask a question")
    print("4. Exit")

    while True:
        try:
            choice = input("\nPlease select an option (1-4): ").strip()

            if choice == "1":
                first_name = input("Enter employee first name: ").strip()
                last_name = input("Enter employee last name: ").strip()

                if first_name and last_name:
                    result = supervisor_agent.start_onboarding(first_name, last_name)
                    if 'error' in result:
                        print(f"Error: {result['error']}")
                    else:
                        print(f"Onboarding session started successfully!")
                        print(f"Session ID: {result['session_id']}")
                        print(f"Next step: {result['next_step']}")
                else:
                    print("Error: Both first name and last name are required.")

            elif choice == "2":
                session_id = input("Enter session ID: ").strip()
                if session_id:
                    status = supervisor_agent.get_onboarding_status(session_id)
                    if 'error' in status:
                        print(f"Error: {status['error']}")
                    else:
                        print(f"Employee ID: {status['employee_id']}")
                        print(f"Status: {status['onboarding_status']}")
                        print(f"Next step: {status['next_step']}")
                        print("Checklist:")
                        for key, value in status['checklist'].items():
                            print(f"  {key}: {value}")
                else:
                    print("Error: Session ID is required.")

            elif choice == "3":
                question = input("Enter your question: ").strip()
                if question:
                    answer = qa_agent.answer_question(question)
                    print(f"\nAnswer: {answer['answer']}")
                else:
                    print("Error: Question cannot be empty.")

            elif choice == "4":
                print("Thank you for using the Employee Onboarding System!")
                break

            else:
                print("Invalid option. Please select 1, 2, 3, or 4.")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

def serve_mode():
    """Start the REST API server."""
    print("Starting Employee Onboarding REST API server...")

    if not FLASK_AVAILABLE:
        print("Error: Flask is not installed. Please install it with 'pip install flask'")
        return

    # Add src to path for imports
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    # Import blueprints
    from src.api.sessions import sessions_bp
    from src.api.id_photo import id_photo_bp
    from src.api.information import information_bp

    # Create Flask app
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(sessions_bp)
    app.register_blueprint(id_photo_bp)
    app.register_blueprint(information_bp)

    # Add a health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Employee Onboarding API is running'}

    print("Server starting on http://localhost:5000")
    print("API endpoints:")
    print("  POST   /api/v1/onboarding/sessions          - Create new session")
    print("  GET    /api/v1/onboarding/sessions/<id>     - Get session info")
    print("  POST   /api/v1/onboarding/sessions/<id>/id-photo - Upload ID photo")
    print("  GET    /api/v1/onboarding/sessions/<id>/id-photo/status - Get ID verification status")
    print("  GET    /api/v1/onboarding/sessions/<id>/information - Get information form")
    print("  POST   /api/v1/onboarding/sessions/<id>/information - Submit information")
    print("  GET    /health                              - Health check")
    print("\nPress Ctrl+C to stop the server")

    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")

def main():
    parser = argparse.ArgumentParser(description="Employee Onboarding Multi-Agent System")
    parser.add_argument(
        "mode",
        nargs='?',
        choices=["chat", "serve"],
        help="Run mode: 'chat' for interactive agent, 'serve' for REST API"
    )

    args = parser.parse_args()

    if args.mode == "chat":
        chat_mode()
    elif args.mode == "serve":
        serve_mode()
    else:
        # Default behavior - show help
        parser.print_help()

if __name__ == "__main__":
    main()