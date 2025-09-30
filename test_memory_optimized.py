#!/usr/bin/env python3
"""
Memory-optimized test script for chat completions.
This script demonstrates how to use the system with memory constraints.
"""

import sys
import os
import torch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from model.chat_completions import (
    ChatCompletions,
    ChatCompletionRequest,
    ChatCompletionMessage,
    create_chat_completion,
    AVAILABLE_MODELS,
)


def check_gpu_memory():
    """Check available GPU memory"""
    if torch.cuda.is_available():
        device = torch.cuda.current_device()
        total_memory = torch.cuda.get_device_properties(device).total_memory / (1024**3)
        allocated_memory = torch.cuda.memory_allocated(device) / (1024**3)
        cached_memory = torch.cuda.memory_reserved(device) / (1024**3)

        print(f"GPU Device: {torch.cuda.get_device_name(device)}")
        print(f"Total GPU Memory: {total_memory:.1f} GB")
        print(f"Allocated Memory: {allocated_memory:.2f} GB")
        print(f"Cached Memory: {cached_memory:.2f} GB")
        print(f"Available Memory: {total_memory - cached_memory:.1f} GB")
        return total_memory
    else:
        print("CUDA not available - will use CPU")
        return 0


def test_with_small_model():
    """Test with memory-efficient settings"""
    print("\\n=== Testing with Memory-Efficient Settings ===")

    # Use smaller model or fallback
    model = "gpt2"  # Start with smallest model
    if "openai/gpt-oss-20b" in AVAILABLE_MODELS:
        gpu_memory = check_gpu_memory()
        if gpu_memory > 40:  # Only use larger model if we have enough memory
            model = "openai/gpt-oss-20b"
        else:
            print(f"Insufficient GPU memory ({gpu_memory:.1f} GB), using {model}")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Keep responses concise.",
        },
        {"role": "user", "content": "What is Python programming language?"},
    ]

    try:
        response = create_chat_completion(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=100,  # Limit tokens to reduce memory usage
        )

        print(f"Model used: {response.model}")
        print(f"Response: {response.choices[0].message.content}")

        if response.usage:
            print(f"Tokens used: {response.usage.total_tokens}")

    except Exception as e:
        print(f"Error: {e}")


def test_with_cpu_fallback():
    """Test forcing CPU usage"""
    print("\\n=== Testing with CPU Fallback ===")

    # Import the OpenAIChat class to force CPU usage
    from core.chat.openai import OpenAIChat

    # Force CPU usage to avoid memory issues
    chat = OpenAIChat(model="gpt2", use_cpu=True)

    messages = [
        {"role": "user", "content": "Explain machine learning in one sentence."}
    ]

    try:
        result = chat.chat(messages, max_tokens=50)
        print(f"CPU Response: {result['choices'][0]['message']['content']}")

    except Exception as e:
        print(f"CPU Error: {e}")


def test_memory_cleanup():
    """Test memory cleanup functionality"""
    print("\\n=== Testing Memory Cleanup ===")

    from core.chat.openai import OpenAIChat

    if torch.cuda.is_available():
        print("Before cleanup:")
        allocated_before = torch.cuda.memory_allocated(0) / (1024**2)  # MB
        print(f"  Allocated: {allocated_before:.1f} MB")

        # Create and use a model
        chat = OpenAIChat(model="gpt2")

        print("After model loading:")
        allocated_after = torch.cuda.memory_allocated(0) / (1024**2)
        print(f"  Allocated: {allocated_after:.1f} MB")

        # Clear memory
        chat.clear_memory()

        print("After cleanup:")
        allocated_final = torch.cuda.memory_allocated(0) / (1024**2)
        print(f"  Allocated: {allocated_final:.1f} MB")
    else:
        print("CUDA not available - memory cleanup test skipped")


def main():
    print("=== Memory-Optimized Chat Completions Test ===")

    # Check system capabilities
    check_gpu_memory()

    print(f"\\nAvailable models: {AVAILABLE_MODELS}")

    # Run tests
    test_with_small_model()
    test_with_cpu_fallback()
    test_memory_cleanup()

    print("\\n=== Recommendations ===")
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"Your GPU has {gpu_memory:.1f} GB of memory.")

        if gpu_memory < 8:
            print("- Recommended: Use CPU mode with use_cpu=True")
            print("- Or use smaller models like 'gpt2' or 'gpt2-medium'")
        elif gpu_memory < 20:
            print("- You can use small models (gpt2, gpt2-medium)")
            print("- Avoid large models like openai/gpt-oss-120b")
        elif gpu_memory < 40:
            print("- You can use medium models")
            print("- Consider openai/gpt-oss-20b with caution")
        else:
            print("- You have sufficient memory for larger models")
            print("- Can try openai/gpt-oss-20b or openai/gpt-oss-120b")
    else:
        print("- CUDA not available, use CPU mode")
        print("- Stick to smaller models for better performance")


if __name__ == "__main__":
    main()
