"""Step 3: Rewrite script via DeepSeek API."""

import json
import os

from openai import OpenAI

from ..app import celery_app
from ...core.config import settings


REWRITE_SYSTEM_PROMPT = """你是一个专业的口播文案改写助手。请根据以下要求改写用户的文案：
1. 保持原文的核心信息和观点不变
2. 使用更口语化、更有感染力的表达方式
3. 保持原文的语言风格（专业/轻松/激情等）
4. 不要改变原文的结构顺序
5. 长度与原文保持相近
6. 直接输出改写后的文案，不要输出任何解释"""


@celery_app.task(bind=True, name="pipeline.rewrite", queue="pipeline_queue",
                  soft_time_limit=300, time_limit=600)
def rewrite_script(self, task_id: str, script_text: str, pipeline_params: dict) -> dict:
    """
    Rewrite script text using DeepSeek API.
    Returns: {rewritten_text, token_usage}
    """
    if not settings.DEEPSEEK_API_KEY:
        return {"rewritten_text": script_text, "note": "DeepSeek API key not configured, returning original"}

    rewrite_config = pipeline_params.get("script_rewrite", {})
    style = rewrite_config.get("style", "professional")
    additional = rewrite_config.get("additional_instructions", "")

    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
    )

    user_prompt = f"改写风格: {style}\n"
    if additional:
        user_prompt += f"额外要求: {additional}\n"
    user_prompt += f"\n原文:\n{script_text}"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    rewritten_text = response.choices[0].message.content.strip()

    # Save rewritten script
    script_dir = os.path.join(settings.TEMP_DIR, task_id, "script")
    os.makedirs(script_dir, exist_ok=True)
    script_path = os.path.join(script_dir, "rewritten_script.json")
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump({
            "original": script_text,
            "rewritten": rewritten_text,
            "style": style,
            "token_usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
        }, f, ensure_ascii=False)

    return {
        "rewritten_text": rewritten_text,
        "script_path": script_path,
    }
