# repomind/backend/query/llm.py
import anthropic
from backend.config import get_settings
from typing import Iterator

SYSTEM_PROMPT = (
    "You are a code assistant. Answer the user's question using ONLY the code excerpts provided. "
    "Always cite file paths and line numbers in your answer. "
    "If the excerpts don't contain the answer, say so — do not guess."
)

def build_prompt(question: str, chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Excerpt {i}: {chunk['file_path']} lines {chunk['start_line']}–{chunk['end_line']}]\n"
            f"```\n{chunk['content']}\n```"
        )
    code_context = "\n\n".join(parts)
    return f"{code_context}\n\nQuestion: {question}"

def stream_answer(question: str, chunks: list[dict]) -> Iterator[str]:
    s = get_settings()
    client = anthropic.Anthropic(api_key=s.anthropic_api_key)
    prompt = build_prompt(question, chunks)

    with client.messages.stream(
        model=s.llm_model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                yield event.delta.text
