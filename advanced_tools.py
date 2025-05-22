from crewai_tools import BaseTool
import json
import os
import requests
import time
from PIL import Image
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import csv

class JSONTool(BaseTool):
    name = "JSONTool"
    description = "Работает с JSON данными - чтение, запись, преобразование."

    def _run(self, action: str, data=None, filename=None):
        if action == "read" and filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                return f"Ошибка чтения JSON: {str(e)}"
        elif action == "write" and data and filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return f"JSON успешно записан в {filename}"
            except Exception as e:
                return f"Ошибка записи JSON: {str(e)}"
        else:
            return "Неверные параметры для JSONTool"

class APITool(BaseTool):
    name = "APITool"
    description = "Выполняет HTTP запросы к API."

    def _run(self, url: str, method="GET", headers=None, data=None, params=None):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                return f"Неподдерживаемый метод: {method}"
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text[:3000]  # Ограничиваем вывод
            }
        except Exception as e:
            return f"Ошибка API запроса: {str(e)}"

class DataAnalysisTool(BaseTool):
    name = "DataAnalysisTool"
    description = "Анализирует данные из CSV/Excel файлов."

    def _run(self, filename: str, action="summary"):
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filename)
            else:
                return "Неподдерживаемый формат файла. Используйте CSV или Excel."
            
            if action == "summary":
                return {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": str(df.dtypes),
                    "head": df.head(5).to_dict(),
                    "describe": df.describe().to_dict()
                }
            elif action == "plot" and len(df.columns) >= 2:
                plt.figure(figsize=(10, 6))
                plt.scatter(df[df.columns[0]], df[df.columns[1]])
                plt.title(f"{df.columns[0]} vs {df.columns[1]}")
                plt.xlabel(df.columns[0])
                plt.ylabel(df.columns[1])
                plot_file = "data_plot.png"
                plt.savefig(plot_file)
                plt.close()
                return f"График сохранен в {plot_file}"
            else:
                return "Неизвестное действие или недостаточно столбцов для построения графика"
        except Exception as e:
            return f"Ошибка анализа данных: {str(e)}"

class ImageTool(BaseTool):
    name = "ImageTool"
    description = "Работает с изображениями - скачивание, базовая обработка."

    def _run(self, action: str, url=None, path=None, width=None, height=None):
        try:
            if action == "download" and url:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                save_path = path or f"image_{int(time.time())}.jpg"
                img.save(save_path)
                return f"Изображение сохранено в {save_path}"
            
            elif action == "resize" and path:
                img = Image.open(path)
                if width and height:
                    resized = img.resize((width, height))
                    save_path = f"resized_{os.path.basename(path)}"
                    resized.save(save_path)
                    return f"Изображение изменено и сохранено в {save_path}"
                else:
                    return "Для изменения размера укажите width и height"
            else:
                return "Неверные параметры для ImageTool"
        except Exception as e:
            return f"Ошибка обработки изображения: {str(e)}"

class CSVTool(BaseTool):
    name = "CSVTool"
    description = "Работает с CSV файлами - чтение, запись, обработка."

    def _run(self, action: str, filename=None, data=None):
        try:
            if action == "read" and filename:
                rows = []
                with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        rows.append(dict(row))
                return rows
            
            elif action == "write" and filename and data:
                if not data or not isinstance(data, list) or not isinstance(data[0], dict):
                    return "Данные должны быть списком словарей"
                
                fieldnames = data[0].keys()
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                return f"CSV успешно записан в {filename}"
            
            else:
                return "Неверные параметры для CSVTool"
        except Exception as e:
            return f"Ошибка работы с CSV: {str(e)}"
