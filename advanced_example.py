from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from tools import FileTool, TerminalTool, WebSearchTool, SQLiteTool, HTMLScraperTool
from advanced_tools import JSONTool, APITool, DataAnalysisTool, ImageTool, CSVTool
import os

load_dotenv()

data_scientist = Agent(
    role="Data Scientist",
    goal="Анализировать данные и создавать информативные отчеты",
    backstory="Ты опытный аналитик данных, умеющий работать с различными форматами и API.",
    tools=[
        FileTool(), TerminalTool(), WebSearchTool(),
        SQLiteTool(), JSONTool(), APITool(), 
        DataAnalysisTool(), ImageTool(), CSVTool()
    ],
    verbose=True
)

task = Task(
    description="""
    Выполни следующие задачи:
    
    1. Создай CSV файл с данными о 5 городах (название, население, страна)
    2. Проанализируй этот CSV файл и создай отчет
    3. Сохрани результаты анализа в JSON файл
    4. Создай SQL базу данных и импортируй туда данные из CSV
    5. Выполни SQL запрос для получения городов с населением > 1 млн
    6. Скачай изображение города с наибольшим населением
    
    Все результаты сохрани в папку 'results'.
    """,
    expected_output="Отчет о проделанной работе с ссылками на созданные файлы.",
    agent=data_scientist
)

crew = Crew(
    agents=[data_scientist],
    tasks=[task]
)

if __name__ == "__main__":
    # Создаем папку для результатов, если её нет
    if not os.path.exists('results'):
        os.makedirs('results')
        
    result = crew.kickoff()
    print("\n\n=== Результат выполнения задачи ===")
    print(result)
