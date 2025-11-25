"""CLI handler for the chat command."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.orchestration.conversation_manager import conversation_manager
from src.models.conversation import Conversation
from src.lib.logging_config import logger


def chat_command(args):
    """
    Handle the chat command.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Validate input parameters
        if not args.name:
            logger.error("Document name is required for chat command")
            print("Error: Document name is required", file=sys.stderr)
            return 1

        logger.info(f"Chat command invoked with parameters:")
        logger.info(f"  Document name: {args.name}")
        logger.info(f"  User ID: {args.user_id}")

        print(f"Starting chat session with document '{args.name}'...")
        print("Type 'exit' or 'quit' to end the conversation.\n")

        # Create a new conversation
        conversation = conversation_manager.create_conversation(
            user_id=args.user_id or "default_user",
            document_name=args.name
        )

        print(f"Conversation started (ID: {conversation.id})")

        # Chat loop
        message_count = 0
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['exit', 'quit']:
                    print("Ending conversation...")
                    conversation_manager.end_conversation(conversation)
                    logger.info(f"Chat session ended. Total messages: {message_count}")
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                # Process the message
                response = conversation_manager.process_message(conversation, user_input)
                message_count += 1

                print(f"\nAssistant: {response}")

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Ending conversation...")
                conversation_manager.end_conversation(conversation)
                logger.info(f"Chat session interrupted. Total messages: {message_count}")
                print("Goodbye!")
                return 0
            except Exception as e:
                logger.error(f"Error during chat: {str(e)}")
                print(f"Error: {str(e)}", file=sys.stderr)
                continue

        logger.info(f"Chat session completed successfully. Total messages: {message_count}")
        return 0

    except Exception as e:
        logger.error(f"Error during chat session: {str(e)}")
        logger.exception("Full traceback:")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # This is just for testing the module directly
    pass