from crewai_tools import BaseTool
import subprocess
import os
import requests
import sqlite3
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from duckduckgo_search import DDGS
import git

class FileTool(BaseTool):
    name = "FileTool"
    description = "Создаёт или обновляет файл с переданным содержимым."

    def _run(self, content: str, filename: str = "main.py"):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Файл {filename} создан или обновлён."

class TerminalTool(BaseTool):
    name = "TerminalTool"
    description = "Позволяет выполнять команды в терминале и получать вывод."

    def _run(self, command: str):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout or result.stderr
        except Exception as e:
            return f"Ошибка выполнения: {str(e)}"

class WebSearchTool(BaseTool):
    name = "WebSearch"
    description = "Ищет в интернете с помощью DuckDuckGo."

    def _run(self, query: str):
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            return "\n".join([r['body'] for r in results])

class PDFReaderTool(BaseTool):
    name = "PDFReader"
    description = "Читает и анализирует PDF-файл."

    def _run(self, path: str):
        reader = PdfReader(path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text[:3000]

class GitTool(BaseTool):
    name = "GitTool"
    description = "Выполняет git действия в текущем проекте."

    def _run(self, action: str):
        try:
            repo = git.Repo('.')
            if action == "commit":
                repo.git.add(A=True)
                repo.index.commit("auto-commit")
                return "Изменения закоммичены."
            elif action == "push":
                repo.git.push()
                return "Изменения отправлены."
            else:
                return f"Неизвестное действие {action}"
        except Exception as e:
            return str(e)

class SQLiteTool(BaseTool):
    name = "SQLiteTool"
    description = "Выполняет SQL-команды на локальной базе данных."

    def _run(self, query: str):
        conn = sqlite3.connect("local.db")
        cur = conn.cursor()
        try:
            cur.execute(query)
            rows = cur.fetchall()
            conn.commit()
            return str(rows)
        except Exception as e:
            return str(e)
        finally:
            conn.close()

class HTMLScraperTool(BaseTool):
    name = "HTMLScraper"
    description = "Скачивает страницу по URL и парсит содержимое."

    def _run(self, url: str):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text()[:3000]
        except Exception as e:
            return str(e)
