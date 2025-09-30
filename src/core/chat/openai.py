import gc
from typing import List, Dict, Any

import torch
from transformers import pipeline


class OpenAIChat:
    """OpenAI-compatible chat interface using transformers with memory optimization"""

    def __init__(
        self, model="openai/gpt-oss-20b", device=None, use_cpu=False, **kwargs
    ):
        """
        Initialize the chat model with memory optimization options.

        Args:
            model: The model name to use
            device: Specific device to use ('cuda', 'cpu', etc.)
            use_cpu: Force CPU usage to avoid CUDA memory issues
            **kwargs: Additional arguments for the pipeline
        """
        self.model = model
        self.use_cpu = use_cpu

        # Determine device
        if use_cpu or not torch.cuda.is_available():
            self.device = "cpu"
        elif device:
            self.device = device
        else:
            # Check available GPU memory
            if torch.cuda.is_available():
                try:
                    # Get GPU memory info
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (
                        1024**3
                    )  # GB
                    print(f"Available GPU memory: {gpu_memory:.1f} GB")

                    # Use CPU for very large models if GPU memory is limited
                    if (
                        "120b" in model and gpu_memory < 200
                    ):  # 120B model needs ~200GB+ VRAM
                        print(
                            f"Warning: Model {model} requires significant VRAM. Using CPU instead."
                        )
                        self.device = "cpu"
                    elif (
                        "20b" in model and gpu_memory < 40
                    ):  # 20B model needs ~40GB+ VRAM
                        print(
                            f"Warning: Model {model} requires significant VRAM. Using CPU instead."
                        )
                        self.device = "cpu"
                    else:
                        self.device = "cuda"
                except:
                    self.device = "cpu"
            else:
                self.device = "cpu"

        print(f"Using device: {self.device}")

        # Clear GPU cache before loading
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

        try:
            # Try to load with memory optimizations
            if self.device == "cpu":
                # CPU-optimized loading
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model,
                    device=-1,  # Force CPU
                    torch_dtype=torch.float32,  # Use float32 for CPU
                    **kwargs,
                )
            else:
                # GPU-optimized loading with reduced precision
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model,
                    device=0,
                    torch_dtype=torch.float16,  # Use half precision to save memory
                    model_kwargs={
                        "low_cpu_mem_usage": True,
                        "device_map": "auto",  # Automatically distribute across available devices
                    },
                    **kwargs,
                )

        except torch.cuda.OutOfMemoryError:
            print("CUDA out of memory. Falling back to CPU...")
            self.device = "cpu"
            # Clear cache and try CPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()

            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                device=-1,  # Force CPU
                torch_dtype=torch.float32,
                **kwargs,
            )

        except Exception as e:
            # Final fallback to a smaller model
            print(
                f"Warning: Failed to load model {model}, falling back to smaller model: {e}"
            )
            fallback_model = "gpt2" if "gpt" in model else "microsoft/DialoGPT-small"

            self.pipe = pipeline(
                "text-generation",
                model=fallback_model,
                device=-1 if self.device == "cpu" else 0,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                **kwargs,
            )
            self.model = fallback_model

    def chat(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 256,
        temperature: float = 1.0,
        top_p: float = 1.0,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion with memory optimization.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional generation parameters

        Returns:
            Dictionary with OpenAI-compatible structure
        """
        # Build conversation prompt
        prompt = self._build_prompt(messages)

        # Clear cache before generation if using GPU
        if self.device != "cpu" and torch.cuda.is_available():
            torch.cuda.empty_cache()

        try:
            # Generate response with memory-efficient settings
            generation_kwargs = {
                "max_new_tokens": min(
                    max_tokens, 512
                ),  # Limit max tokens to prevent OOM
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": True,
                "pad_token_id": (
                    self.pipe.tokenizer.eos_token_id if self.pipe.tokenizer else None
                ),
                "return_full_text": False,  # Only return generated text
                **kwargs,
            }

            # Remove None values
            generation_kwargs = {
                k: v for k, v in generation_kwargs.items() if v is not None
            }

            response = self.pipe(prompt, **generation_kwargs)

            # Extract generated text
            if isinstance(response, list) and len(response) > 0:
                generated_text = response[0].get("generated_text", "")
            else:
                generated_text = str(response)

            # Clean up the content
            new_content = generated_text.strip()

            return {
                "choices": [
                    {
                        "message": {"role": "assistant", "content": new_content},
                        "finish_reason": "stop",
                    }
                ]
            }

        except torch.cuda.OutOfMemoryError:
            # If we get OOM during generation, try with smaller max_tokens
            print("CUDA OOM during generation. Reducing max_tokens and retrying...")
            torch.cuda.empty_cache()
            gc.collect()

            try:
                # Retry with much smaller token limit
                smaller_kwargs = generation_kwargs.copy()
                smaller_kwargs["max_new_tokens"] = min(50, max_tokens // 4)

                response = self.pipe(prompt, **smaller_kwargs)

                if isinstance(response, list) and len(response) > 0:
                    generated_text = response[0].get("generated_text", "")
                else:
                    generated_text = str(response)

                return {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": generated_text.strip(),
                            },
                            "finish_reason": "length",  # Stopped due to memory constraints
                        }
                    ]
                }
            except Exception as e:
                return {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": f"Error: Unable to generate response due to memory constraints - {str(e)}",
                            },
                            "finish_reason": "error",
                        }
                    ]
                }

        except Exception as e:
            print(f"Error during generation: {e}")
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": f"Error: Unable to generate response - {str(e)}",
                        },
                        "finish_reason": "error",
                    }
                ]
            }
        finally:
            # Clean up after generation
            if self.device != "cpu" and torch.cuda.is_available():
                torch.cuda.empty_cache()

    def _build_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """
        Build a conversation prompt from messages.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            elif role == "function":
                function_name = msg.get("name", "unknown")
                prompt_parts.append(f"Function {function_name}: {content}")

        # Add prompt for assistant response
        prompt = "\n".join(prompt_parts) + "\nAssistant:"
        return prompt

    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available models"""
        return [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",  # Added smaller variant
            "gpt2",
            "gpt2-medium",
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-small",
            # Add more models as they become available
        ]

    def clear_memory(self):
        """Manually clear GPU memory cache"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()


# Example usage:
if __name__ == "__main__":
    # For systems with limited GPU memory, force CPU usage
    chat = OpenAIChat(device="cuda")  # or chat = OpenAIChat() for auto-detection
    messages = [{"role": "user", "content": "Who are you?"}]
    result = chat.chat(messages)
    print(result)
