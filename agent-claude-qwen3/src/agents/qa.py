"""
Q&A agent for answering employee onboarding questions.
"""

from typing import Dict, Any
from ..services.position_service import position_service
from ..utils.exceptions import log_info, log_error


class QA_Agent:
    """Agent responsible for answering employee questions."""

    def __init__(self):
        """Initialize Q&A agent."""
        pass

    def answer_question(self, question: str, employee_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Answer an employee question based on context.

        Args:
            question: The question to answer
            employee_context: Optional context about the employee

        Returns:
            Answer to the question
        """
        try:
            log_info(f"Answering question: {question}")

            # Determine the type of question and provide appropriate answer
            question_lower = question.lower()

            # Handle position responsibilities questions
            if 'responsibility' in question_lower or 'responsibilities' in question_lower:
                if employee_context and 'position' in employee_context:
                    position_info = position_service.get_position_responsibilities(employee_context['position'])
                    if position_info:
                        return {
                            'question': question,
                            'answer': f"Your position ({position_info['name']}) responsibilities:\n{position_info['responsibilities']}",
                            'category': 'responsibilities'
                        }

            # Handle post-onboarding tasks questions
            if 'task' in question_lower or 'next' in question_lower:
                if employee_context and 'position' in employee_context:
                    tasks = position_service.get_post_onboarding_tasks(employee_context['position'])
                    if tasks:
                        tasks_str = "\n".join([f"- {task}" for task in tasks])
                        return {
                            'question': question,
                            'answer': f"Your post-onboarding tasks:\n{tasks_str}",
                            'category': 'post_tasks'
                        }

            # Handle general onboarding questions
            if 'onboard' in question_lower or 'process' in question_lower:
                return {
                    'question': question,
                    'answer': "The onboarding process includes:\n1. Identity verification\n2. Personal information collection\n3. Position responsibilities review\n4. Account provisioning\n5. Post-onboarding task reminders",
                    'category': 'onboarding_process'
                }

            # Default response for unrecognized questions
            return {
                'question': question,
                'answer': "I'm not sure about that. Please contact HR for more specific information.",
                'category': 'general'
            }

        except Exception as e:
            log_error(e, f"Failed to answer question: {question}")
            return {
                'question': question,
                'answer': "Sorry, I encountered an error while processing your question.",
                'category': 'error',
                'error': str(e)
            }

    def get_position_responsibilities(self, position_name: str) -> Dict[str, Any]:
        """
        Get detailed position responsibilities.

        Args:
            position_name: Name of the position

        Returns:
            Position responsibilities information
        """
        try:
            log_info(f"Getting responsibilities for position: {position_name}")
            responsibilities = position_service.get_position_responsibilities(position_name)

            if responsibilities:
                return {
                    'position': position_name,
                    'name': responsibilities['name'],
                    'department': responsibilities['department'],
                    'responsibilities': responsibilities['responsibilities'],
                    'required_permissions': responsibilities['required_permissions']
                }
            else:
                return {
                    'position': position_name,
                    'error': 'Position not found'
                }

        except Exception as e:
            log_error(e, f"Failed to get responsibilities for position: {position_name}")
            return {
                'position': position_name,
                'error': f"Failed to get responsibilities: {str(e)}"
            }

    def get_post_onboarding_tasks(self, position_name: str) -> Dict[str, Any]:
        """
        Get post-onboarding tasks for a position.

        Args:
            position_name: Name of the position

        Returns:
            Post-onboarding tasks information
        """
        try:
            log_info(f"Getting post-onboarding tasks for position: {position_name}")
            tasks = position_service.get_post_onboarding_tasks(position_name)

            return {
                'position': position_name,
                'tasks': tasks
            }

        except Exception as e:
            log_error(e, f"Failed to get post-onboarding tasks for position: {position_name}")
            return {
                'position': position_name,
                'error': f"Failed to get tasks: {str(e)}"
            }


# Global Q&A agent instance
qa_agent = QA_Agent()