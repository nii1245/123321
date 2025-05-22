from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from tools import FileTool, TerminalTool, WebSearchTool, PDFReaderTool, GitTool, SQLiteTool, HTMLScraperTool
import os

load_dotenv()

developer = Agent(
    role="Full-Stack Autonomous Coder",
    goal="Создавать, запускать и улучшать ПО, выполняя команды пользователя и действуя как полноценный агент",
    backstory="Ты автономный инженер, способный анализировать, кодить, работать с базами, PDF, Git и Web.",
    tools=[
        FileTool(), TerminalTool(), WebSearchTool(),
        PDFReaderTool(), GitTool(), SQLiteTool(), HTMLScraperTool()
    ],
    verbose=True
)

task = Task(
    description="Создай консольную адресную книгу на Python с базой SQLite и CLI интерфейсом.",
    expected_output="Код в файле main.py + база данных.",
    agent=developer
)

crew = Crew(
    agents=[developer],
    tasks=[task]
)

if __name__ == "__main__":
    crew.kickoff()
