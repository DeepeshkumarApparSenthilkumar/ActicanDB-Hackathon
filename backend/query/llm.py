# repomind/backend/query/llm.py
from openai import OpenAI
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
    client = OpenAI(api_key=s.nvidia_api_key, base_url=s.nvidia_base_url)
    prompt = build_prompt(question, chunks)

    stream = client.chat.completions.create(
        model=s.llm_model,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
