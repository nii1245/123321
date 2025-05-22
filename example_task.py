from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from tools import FileTool, TerminalTool, WebSearchTool, PDFReaderTool, GitTool, SQLiteTool, HTMLScraperTool
import os

load_dotenv()

developer = Agent(
    role="Full-Stack Developer",
    goal="Создать Telegram-бота для сохранения и анализа ссылок",
    backstory="Ты опытный разработчик, специализирующийся на создании ботов и работе с данными.",
    tools=[
        FileTool(), TerminalTool(), WebSearchTool(),
        SQLiteTool(), HTMLScraperTool()
    ],
    verbose=True
)

task = Task(
    description="""
    Создай Telegram-бота на Python с использованием библиотеки python-telegram-bot.
    Бот должен:
    1. Сохранять ссылки, которые отправляет пользователь, в базу данных SQLite
    2. Парсить HTML-содержимое этих ссылок и сохранять заголовок и краткое описание
    3. Позволять пользователю просматривать сохраненные ссылки
    4. Иметь команду для поиска по сохраненным ссылкам
    
    Создай все необходимые файлы, включая main.py и schema.sql.
    """,
    expected_output="Полностью рабочий код бота в файле main.py и структура базы данных.",
    agent=developer
)

crew = Crew(
    agents=[developer],
    tasks=[task]
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n\n=== Результат выполнения задачи ===")
    print(result)
