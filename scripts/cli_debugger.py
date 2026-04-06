import asyncio
import json
from pathlib import Path

import aiofiles

from src.core.config import settings
from src.core.llm import summarize_with_llm
from src.core.logs import is_error_log_line


async def debug_logs():
    log_file_path = Path(settings.LOG_FILE_PATH)
    logs = []

    print(f"Scanning logs from {log_file_path}...")

    try:
        if not log_file_path.exists():
            print(f"No log file found: {log_file_path}")
            return

        async with aiofiles.open(log_file_path, mode="r") as file:
            async for line in file:
                if is_error_log_line(line):
                    logs.append(line.strip())

    except Exception as e:
        print(f"Error reading logs: {e}")
        return

    if not logs:
        print("No errors found in logs.")
        return

    print(f"Found {len(logs)} error logs. Analyzing with AI...")

    try:
        analysis = await summarize_with_llm(logs)

        summary = analysis.get("summary_text", "No summary available.")
        structured = analysis.get("structured_insight", {})
        provider = analysis.get("provider")

        if provider:
            print(f"\nProvider: {provider}")

        print("\nAI Analysis\n-----------")
        print(summary)

        if structured:
            print("\nStructured Plan\n---------------")
            print(json.dumps(structured, indent=2))

    except Exception as e:
        print(f"AI analysis failed: {e}")


if __name__ == "__main__":
    asyncio.run(debug_logs())
