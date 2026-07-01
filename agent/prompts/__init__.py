from pathlib import Path

PROMPTS_DIR = Path(__file__).parent

system_prompt = "\n\n".join(
    (PROMPTS_DIR / name).read_text()
    for name in ("system.md", "faq.md")
)
