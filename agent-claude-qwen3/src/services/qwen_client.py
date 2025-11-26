"""
Qwen API client for language and vision-language model interactions.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from ..utils.config import get_config, get_required_config
from ..utils.exceptions import ExternalServiceError, log_error, log_info

class QwenClient:
    """Client for interacting with Qwen models."""

    def __init__(self):
        """Initialize Qwen client with configuration."""
        config = get_config()
        self.api_base = config.get('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.api_key = get_required_config('QWEN_API_KEY')

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        })

    def _make_request(self, model: str, messages: List[Dict[str, str]],
                     temperature: float = 0.7, max_tokens: int = 1000) -> Dict[Any, Any]:
        """
        Make a request to the Qwen API.

        Args:
            model: Model name (e.g., 'qwen3-max', 'qwen3-vl-max')
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response data as dictionary

        Raises:
            ExternalServiceError: If the request fails
        """
        url = f"{self.api_base}/chat/completions"

        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        try:
            log_info(f"Making request to Qwen API with model {model}")

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            log_info(f"Qwen API response received with {len(result.get('choices', []))} choices")

            return result

        except requests.exceptions.RequestException as e:
            log_error(e, f"Qwen API request failed: {url}")
            raise ExternalServiceError(f"Failed to communicate with Qwen API: {str(e)}")
        except json.JSONDecodeError as e:
            log_error(e, f"Invalid JSON response from Qwen API: {url}")
            raise ExternalServiceError(f"Invalid response from Qwen API: {str(e)}")

    def chat_completion(self, messages: List[Dict[str, str]],
                       temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Get a chat completion from Qwen3-Max.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        response = self._make_request('qwen3-max', messages, temperature, max_tokens)

        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            raise ExternalServiceError("No response generated from Qwen model")

    def vision_completion(self, messages: List[Dict[str, str]],
                         temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Get a vision-language completion from Qwen3-VL-Max.

        Args:
            messages: List of message dictionaries (including image URLs)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        response = self._make_request('qwen3-vl-max', messages, temperature, max_tokens)

        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            raise ExternalServiceError("No response generated from Qwen VL model")

    def extract_id_information(self, image_url: str) -> Dict[str, Any]:
        """
        Extract information from an ID photo using vision-language model.

        Args:
            image_url: URL or path to the ID photo

        Returns:
            Extracted information as dictionary
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please extract the following information from this ID photo: first name, last name, and ID number. Return the information in JSON format."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]

        response_text = self.vision_completion(messages)

        try:
            # Try to parse the response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If not JSON, return as text
            return {"raw_response": response_text}

# Global Qwen client instance
qwen_client = QwenClient()