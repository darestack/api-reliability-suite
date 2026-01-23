import asyncio
import sys
import os

# Add project root to path so we can import src modules
sys.path.append(os.getcwd())

from src.core.llm import summarize_with_llm  # noqa: E402
import aiofiles  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.markdown import Markdown  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.json import JSON  # noqa: E402

console = Console()


async def debug_logs():
    log_file_path = "app.json"
    logs = []

    console.print("[bold blue]🔍 Scanning logs...[/bold blue]")

    try:
        if not os.path.exists(log_file_path):
            console.print("[bold red]❌ No log file found (app.json)[/bold red]")
            return

        async with aiofiles.open(log_file_path, mode="r") as file:
            async for line in file:
                if "error" in line.lower() or "exception" in line.lower():
                    logs.append(line.strip())

    except Exception as e:
        console.print(f"[bold red]Error reading logs: {e}[/bold red]")
        return

    if not logs:
        console.print("[bold green]✅ No errors found in logs.[/bold green]")
        return

    console.print(
        f"[yellow]Found {len(logs)} error logs. Analyzing with AI...[/yellow]"
    )

    try:
        # Import needs to happen here to avoid issues if .env isn't loaded yet in some contexts
        # though inside the container it should be fine.
        analysis = await summarize_with_llm(logs)

        summary = analysis.get("summary_text", "No summary available.")
        structured = analysis.get("structured_insight", {})

        console.print(
            Panel(Markdown(summary), title="🤖 AI Analysis", border_style="blue")
        )

        if structured:
            console.print(
                Panel(
                    JSON.from_data(structured),
                    title="🛠️ Structured Plan",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(f"[bold red]AI Analysis Failed: {e}[/bold red]")


if __name__ == "__main__":
    asyncio.run(debug_logs())
