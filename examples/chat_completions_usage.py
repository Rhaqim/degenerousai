"""
Usage examples for the revamped chat completions system.

This demonstrates how to use the new functional interface with proper
OpenAI-compatible request/response schemas.
"""

from src.model.chat_completions import (
    ChatCompletions,
    ChatCompletionRequest,
    ChatCompletionMessage,
    ChatCompletionResponseFormat,
    RoleEnum,
    create_chat_completion,
    AVAILABLE_MODELS,
)


# Example 1: Basic usage with the ChatCompletions.create() method
def example_basic_usage():
    """Basic chat completion example"""

    # Create messages
    messages = [
        ChatCompletionMessage(
            role=RoleEnum.system,
            content="You are a helpful AI assistant that provides concise answers.",
        ),
        ChatCompletionMessage(
            role=RoleEnum.user,
            content="Explain what machine learning is in one sentence.",
        ),
    ]

    # Create request
    request = ChatCompletionRequest(
        model="openai/gpt-oss-20b",  # Use available model
        messages=messages,
        temperature=0.7,
        max_tokens=150,
    )

    # Get response
    response = ChatCompletions.create(request)

    # Access the response
    assistant_message = response.choices[0].message.content
    print(f"Assistant: {assistant_message}")

    return response


# Example 2: Using the convenience function
def example_convenience_function():
    """Using the convenience function for simpler usage"""

    messages = [
        {"role": "user", "content": "What are the benefits of renewable energy?"}
    ]

    response = create_chat_completion(
        model="openai/gpt-oss-20b", messages=messages, temperature=0.5, max_tokens=200
    )

    print(f"Response: {response.choices[0].message.content}")
    return response


# Example 3: Multi-turn conversation
def example_conversation():
    """Example of a multi-turn conversation"""

    conversation_history = [
        ChatCompletionMessage(
            role=RoleEnum.system,
            content="You are a knowledgeable tutor helping a student learn programming.",
        ),
        ChatCompletionMessage(
            role=RoleEnum.user,
            content="Can you explain what a function is in programming?",
        ),
    ]

    # First exchange
    request = ChatCompletionRequest(
        model="openai/gpt-oss-20b",
        messages=conversation_history,
        temperature=0.6,
        max_tokens=200,
    )

    response = ChatCompletions.create(request)
    assistant_response = response.choices[0].message.content

    print(f"User: Can you explain what a function is in programming?")
    print(f"Assistant: {assistant_response}")

    # Add assistant's response to history
    conversation_history.append(
        ChatCompletionMessage(role=RoleEnum.assistant, content=assistant_response)
    )

    # Continue conversation
    conversation_history.append(
        ChatCompletionMessage(
            role=RoleEnum.user, content="Can you give me a simple example in Python?"
        )
    )

    # Second exchange
    request.messages = conversation_history
    response = ChatCompletions.create(request)

    print(f"User: Can you give me a simple example in Python?")
    print(f"Assistant: {response.choices[0].message.content}")

    return response


# Example 4: Model availability and error handling
def example_model_management():
    """Example of checking available models and error handling"""

    # Check available models
    available_models = ChatCompletions.get_available_models()
    print(f"Available models: {available_models}")

    # Try with a valid model
    try:
        response = create_chat_completion(
            model=available_models[0],
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=50,
        )
        print(f"Success with {available_models[0]}")

    except Exception as e:
        print(f"Error with valid model: {e}")

    # Try with an invalid model
    try:
        response = create_chat_completion(
            model="non-existent-model",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=50,
        )
        print("Unexpected success with invalid model")

    except ValueError as e:
        print(f"Expected error with invalid model: {e}")


# Example 5: Accessing response metadata
def example_response_metadata():
    """Example of accessing all response metadata"""

    response = create_chat_completion(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "user", "content": "Tell me about the weather in a few words."}
        ],
        temperature=0.3,
        max_tokens=50,
    )

    print("=== Response Metadata ===")
    print(f"ID: {response.id}")
    print(f"Object: {response.object}")
    print(f"Created: {response.created}")
    print(f"Model: {response.model}")

    if response.choices:
        choice = response.choices[0]
        print(f"Choice index: {choice.index}")
        print(f"Finish reason: {choice.finish_reason}")
        print(f"Message role: {choice.message.role}")
        print(f"Message content: {choice.message.content}")

    if response.usage:
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Completion tokens: {response.usage.completion_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")


if __name__ == "__main__":
    print("=== Chat Completions Usage Examples ===\n")

    print("1. Basic Usage:")
    example_basic_usage()
    print("\n" + "=" * 50 + "\n")

    print("2. Convenience Function:")
    example_convenience_function()
    print("\n" + "=" * 50 + "\n")

    print("3. Multi-turn Conversation:")
    example_conversation()
    print("\n" + "=" * 50 + "\n")

    print("4. Model Management:")
    example_model_management()
    print("\n" + "=" * 50 + "\n")

    print("5. Response Metadata:")
    example_response_metadata()
