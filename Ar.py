import os

def scan_directory_to_txt(root_dir, output_file="project_content.txt"):
    """
    Рекурсивно сканирует папку и сохраняет структуру + содержимое файлов в TXT.
    Игнорирует бинарные файлы и слишком большие файлы (>1 МБ).
    """
    with open(output_file, "w", encoding="utf-8") as out_f:
        for root, dirs, files in os.walk(root_dir):
            # Записываем текущую папку
            out_f.write(f"\n📁 {os.path.abspath(root)}\n")
            
            for file in files:
                file_path = os.path.join(root, file)
                out_f.write(f"\n📄 {file}\n")
                
                try:
                    # Пропускаем бинарные и большие файлы
                    if file.endswith((".png", ".jpg", ".exe", ".dll", ".zip", ".pth", ".bin")):
                        out_f.write("(бинарный файл, пропущен)\n")
                        continue
                    
                    file_size = os.path.getsize(file_path)
                    if file_size > 1_000_000:  # Не читаем файлы >1 MB
                        out_f.write(f"(файл слишком большой: {file_size} байт)\n")
                        continue
                    
                    # Записываем содержимое текстового файла
                    with open(file_path, "r", encoding="utf-8") as in_f:
                        content = in_f.read()
                        out_f.write(f"{content}\n")
                except UnicodeDecodeError:
                    out_f.write("(не текстовый файл или неверная кодировка)\n")
                except Exception as e:
                    out_f.write(f"(ошибка при чтении: {str(e)})\n")

if __name__ == "__main__":
    target_folder = input("Введите путь к папке проекта: ").strip()
    if not os.path.isdir(target_folder):
        print("Ошибка: папка не существует!")
    else:
        scan_directory_to_txt(target_folder)
        print(f"Готово! Результат сохранён в 'project_content.txt'.")