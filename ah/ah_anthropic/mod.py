import asyncio
from ..services import service
import anthropic
import os

@service()
async def stream_chat(model, messages=[], context=None, num_ctx=200000, temperature=0.0, max_tokens=400, num_gpu_layers=0):
    try:
        model = "claude-3-5-sonnet-20240620"
        client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        async with client.messages.stream(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
        ) as original_stream:
            async for chunk in original_stream.text_stream:
                yield chunk


    except Exception as e:
        print('claude.ai error:', e)
