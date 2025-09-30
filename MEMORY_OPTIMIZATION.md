# GPU Memory Optimization Guide

This guide helps you resolve CUDA out of memory errors when using the chat completions system.

## Quick Fixes

### 1. Force CPU Usage
```python
from src.core.chat.openai import OpenAIChat

# Force CPU usage to avoid GPU memory issues
chat = OpenAIChat(model="gpt2", use_cpu=True)
```

### 2. Use Smaller Models
```python
from src.model.chat_completions import create_chat_completion

# Use smaller, memory-friendly models
response = create_chat_completion(
    model="gpt2",  # Instead of "openai/gpt-oss-120b"
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100  # Limit output length
)
```

### 3. Set Environment Variables
```bash
# Before running your script
export CUDA_LAUNCH_BLOCKING=1
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

## Model Memory Requirements

| Model | Approximate VRAM Required | Recommended For |
|-------|---------------------------|-----------------|
| `gpt2` | ~0.5 GB | Any GPU, CPU-friendly |
| `gpt2-medium` | ~1.5 GB | GPUs with 4GB+ VRAM |
| `openai/gpt-oss-20b` | ~40 GB | High-end GPUs (A100, etc.) |
| `openai/gpt-oss-120b` | ~200+ GB | Multi-GPU setups |

## Code Examples

### Automatic Memory Detection
```python
from src.core.chat.openai import OpenAIChat

# The system will automatically detect GPU memory and choose appropriate settings
chat = OpenAIChat(model="openai/gpt-oss-120b")  # Will fallback to CPU if needed
```

### Manual Memory Management
```python
import torch
from src.core.chat.openai import OpenAIChat

# Check GPU memory before loading
if torch.cuda.is_available():
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"GPU Memory: {gpu_memory:.1f} GB")
    
    if gpu_memory < 40:  # Less than 40GB
        chat = OpenAIChat(model="gpt2", use_cpu=True)
    else:
        chat = OpenAIChat(model="openai/gpt-oss-20b")
else:
    chat = OpenAIChat(model="gpt2", use_cpu=True)
```

### Memory Cleanup
```python
# Clear GPU cache between generations
chat.clear_memory()

# Or manually
import torch
import gc

torch.cuda.empty_cache()
gc.collect()
```

## Troubleshooting Steps

1. **First try**: Force CPU usage
   ```python
   chat = OpenAIChat(use_cpu=True)
   ```

2. **If still failing**: Use smallest model
   ```python
   chat = OpenAIChat(model="gpt2", use_cpu=True)
   ```

3. **For production**: Set up proper model selection
   ```python
   import torch
   
   def get_optimal_model():
       if not torch.cuda.is_available():
           return "gpt2"
       
       gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
       
       if gpu_memory >= 200:
           return "openai/gpt-oss-120b"
       elif gpu_memory >= 40:
           return "openai/gpt-oss-20b"
       elif gpu_memory >= 4:
           return "gpt2-medium"
       else:
           return "gpt2"
   
   model = get_optimal_model()
   chat = OpenAIChat(model=model)
   ```

## Performance Tips

1. **Limit max_tokens**: Reduce memory usage during generation
   ```python
   response = chat.chat(messages, max_tokens=100)  # Instead of 512+
   ```

2. **Use lower precision**: The system automatically uses float16 on GPU
   
3. **Batch processing**: Process one conversation at a time
   
4. **Clear memory**: Call `chat.clear_memory()` between sessions

## Error Messages and Solutions

### "CUDA error: out of memory"
- **Solution**: Use `use_cpu=True` or smaller model
- **Code**: `chat = OpenAIChat(model="gpt2", use_cpu=True)`

### "RuntimeError: CUDA out of memory"
- **Solution**: Clear cache and retry with smaller tokens
- **Code**: 
  ```python
  torch.cuda.empty_cache()
  response = chat.chat(messages, max_tokens=50)
  ```

### Model loading fails
- **Solution**: The system will automatically fallback to gpt2
- **Manual**: `chat = OpenAIChat(model="gpt2")`

## System Requirements by Use Case

### Development/Testing
- **GPU**: Any modern GPU with 4GB+ VRAM
- **Model**: `gpt2` or `gpt2-medium`
- **Settings**: `use_cpu=True` for reliability

### Production (Small Scale)
- **GPU**: 8GB+ VRAM (RTX 3080, etc.)
- **Model**: `gpt2-medium`
- **Settings**: Automatic detection enabled

### Production (Large Scale)
- **GPU**: 40GB+ VRAM (A100, H100)
- **Model**: `openai/gpt-oss-20b`
- **Settings**: Multi-GPU setup with device mapping

### CPU-Only Systems
- **Model**: `gpt2` (fastest on CPU)
- **Settings**: `use_cpu=True`
- **Performance**: Slower but reliable