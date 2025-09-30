#!/usr/bin/env python3
"""
Test script for the revamped chat completions functionality.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from model.chat_completions import (
    ChatCompletions,
    ChatCompletionRequest,
    ChatCompletionMessage,
    RoleEnum,
    create_chat_completion,
    AVAILABLE_MODELS,
)


def test_available_models():
    """Test getting available models"""
    print("Available models:")
    models = ChatCompletions.get_available_models()
    for model in models:
        print(f"  - {model}")
    print()


def test_chat_completion_with_request():
    """Test chat completion using ChatCompletionRequest"""
    print("Testing chat completion with ChatCompletionRequest:")

    # Create messages
    messages = [
        ChatCompletionMessage(
            role=RoleEnum.system, content="You are a helpful assistant."
        ),
        ChatCompletionMessage(
            role=RoleEnum.user, content="Hello! Can you tell me a short joke?"
        ),
    ]

    # Create request
    request = ChatCompletionRequest(
        model=AVAILABLE_MODELS[0],  # Use the first available model
        messages=messages,
        temperature=0.7,
        max_tokens=100,
    )

    try:
        # Create completion
        response = ChatCompletions.create(request)

        print(f"Response ID: {response.id}")
        print(f"Model: {response.model}")
        print(f"Created: {response.created}")
        print(f"Object: {response.object}")

        if response.choices:
            choice = response.choices[0]
            print(f"Choice index: {choice.index}")
            print(f"Finish reason: {choice.finish_reason}")
            print(f"Assistant response: {choice.message.content}")

        if response.usage:
            print(f"Token usage:")
            print(f"  Prompt tokens: {response.usage.prompt_tokens}")
            print(f"  Completion tokens: {response.usage.completion_tokens}")
            print(f"  Total tokens: {response.usage.total_tokens}")

    except Exception as e:
        print(f"Error: {e}")

    print()


def test_convenience_function():
    """Test the convenience function"""
    print("Testing convenience function:")

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]

    try:
        response = create_chat_completion(
            model=AVAILABLE_MODELS[0], messages=messages, temperature=0.5, max_tokens=50
        )

        print(f"Response: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Error: {e}")

    print()


def test_invalid_model():
    """Test with invalid model"""
    print("Testing with invalid model:")

    messages = [ChatCompletionMessage(role=RoleEnum.user, content="Hello")]

    request = ChatCompletionRequest(model="invalid-model", messages=messages)

    try:
        response = ChatCompletions.create(request)
        print("Unexpected success!")
    except ValueError as e:
        print(f"Expected error caught: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print()


if __name__ == "__main__":
    print("=== Chat Completions Test ===\n")

    test_available_models()
    test_chat_completion_with_request()
    test_convenience_function()
    test_invalid_model()

    print("=== Test Complete ===")
