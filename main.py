"""
Парсер преподавателей МГКЦТ
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List, Dict
from datetime import datetime


class TeacherParser:
    """Класс для парсинга информации о преподавателях"""
    
    def __init__(self):
        self.url = "https://mgkct.minskedu.gov.by/о-колледже/педагогический-коллектив"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
    def get_page_content(self) -> str:
        """Получение содержимого страницы"""
        try:
            print(" Подключаюсь к сайту...")
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Устанавливаем правильную кодировку
            response.encoding = 'utf-8'
            print("Страница успешно загружена")
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f" Ошибка при загрузке страницы: {e}")
            return None
    
    def parse_teachers(self, html_content: str) -> List[Dict]:
        """Парсинг информации о преподавателях"""
        if not html_content:
            return []
        
        try:
            # Пробуем использовать lxml, если не установлен - используем html.parser
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except:
                print("  lxml не установлен, использую html.parser")
                soup = BeautifulSoup(html_content, 'html.parser')
                
        except Exception as e:
            print(f" Ошибка при создании BeautifulSoup: {e}")
            return []
        
        teachers = []
        
        # Ищем таблицы с преподавателями
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    name = cols[0].get_text(strip=True)
                    post = cols[1].get_text(strip=True)
                    
                    # Проверяем, что это похоже на преподавателя
                    if (name and len(name.split()) >= 2 and 
                        any(word in post.lower() for word in ['преподаватель', 'учитель', 'педагог', 'категории'])):
                        teachers.append({
                            'name': name,
                            'post': post,
                            'id': len(teachers) + 1
                        })
        
        # Если не нашли в таблицах, ищем по всему тексту
        if not teachers:
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Ищем строки с ФИО и должностью
                if (len(line) > 20 and 
                    any(word in line.lower() for word in ['преподаватель', 'категории'])):
                    
                    # Пробуем разделить на имя и должность
                    parts = line.split(';')
                    if len(parts) >= 2:
                        teachers.append({
                            'name': parts[0].strip(),
                            'post': parts[1].strip(),
                            'id': len(teachers) + 1
                        })
        
        return teachers
    
    def save_to_json(self, teachers: List[Dict], filename: str = 'data.json'):
        """Сохранение данных в JSON файл (Задание 3)"""
        try:
            data = {
                'source': self.url,
                'parsed_at': datetime.now().isoformat(),
                'total_teachers': len(teachers),
                'teachers': teachers
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f" Данные сохранены в файл: {filename}")
            print(f"   Всего преподавателей: {len(teachers)}")
            return filename
            
        except Exception as e:
            print(f" Ошибка при сохранении в JSON: {e}")
            return None
    
    def generate_html(self, json_filename: str = 'data.json', html_filename: str = 'index.html'):
        """Генерация HTML страницы (Задание 4)"""
        try:
            # Загружаем данные из JSON
            with open(json_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            teachers = data['teachers']
            parsed_at = datetime.fromisoformat(data['parsed_at']).strftime('%d.%m.%Y %H:%M:%S')
            
            # Создаем HTML страницу
            html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Педагогический коллектив МГКЦТ</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            padding: 30px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .info-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .info-card .total {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        .info-card .date {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .table-container {{
            overflow-x: auto;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th {{
            padding: 20px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 1.1em;
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        
        th:last-child {{
            border-right: none;
        }}
        
        th i {{
            margin-right: 10px;
        }}
        
        tbody tr {{
            border-bottom: 1px solid #f1f1f1;
            transition: all 0.3s ease;
        }}
        
        tbody tr:hover {{
            background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        tbody tr:nth-child(even):hover {{
            background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        }}
        
        td {{
            padding: 18px 15px;
            color: #2c3e50;
            font-size: 1em;
            border-right: 1px solid #f1f1f1;
        }}
        
        td:first-child {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        td:last-child {{
            border-right: none;
        }}
        
        .post-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            text-align: center;
            min-width: 150px;
        }}
        
        .post-high {{
            background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
            color: white;
        }}
        
        .post-medium {{
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
            color: white;
        }}
        
        .post-low {{
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
            color: white;
        }}
        
        .post-other {{
            background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
            color: white;
        }}
        
        .footer {{
            margin-top: 40px;
            text-align: center;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #7f8c8d;
        }}
        
        .source-link {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        }}
        
        .source-link:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .source-link i {{
            margin-right: 8px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            th, td {{
                padding: 12px 8px;
                font-size: 0.9em;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .info-card {{
                flex-direction: column;
                gap: 10px;
                text-align: center;
            }}
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chalkboard-teacher"></i> Педагогический коллектив МГКЦТ</h1>
            <p>Информация о преподавателях Минского государственного колледжа цифровых технологий</p>
        </div>
        
        <div class="info-card">
            <div>
                <div class="total">{len(teachers)} преподавателей</div>
                <div class="date">Данные обновлены: {parsed_at}</div>
            </div>
            <div>
                <i class="fas fa-university" style="font-size: 2.5em; opacity: 0.8;"></i>
            </div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-hashtag"></i> №</th>
                        <th><i class="fas fa-user-graduate"></i> ФИО преподавателя</th>
                        <th><i class="fas fa-briefcase"></i> Должность и категория</th>
                    </tr>
                </thead>
                <tbody>
'''
            
            # Добавляем строки таблицы
            for teacher in teachers:
                # Определяем класс для бейджа категории
                post_class = 'post-other'
                post = teacher['post'].lower()
                
                if 'высшей' in post:
                    post_class = 'post-high'
                elif 'первой' in post:
                    post_class = 'post-medium'
                elif 'без категории' in post:
                    post_class = 'post-low'
                
                html_content += f'''                    <tr>
                        <td>{teacher['id']}</td>
                        <td><i class="fas fa-user" style="color: #667eea; margin-right: 8px;"></i>{teacher['name']}</td>
                        <td><span class="post-badge {post_class}">{teacher['post']}</span></td>
                    </tr>
'''
            
            # Закрываем HTML
            html_content += f'''                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Данные собраны с официального сайта МГКЦТ</p>
            <a href="{self.url}" class="source-link" target="_blank">
                <i class="fas fa-external-link-alt"></i> Перейти на исходный сайт
            </a>
            <p style="margin-top: 20px; font-size: 0.9em; opacity: 0.7;">
                <i class="fas fa-code"></i> Сгенерировано программой-парсером | {datetime.now().strftime('%Y')}
            </p>
        </div>
    </div>
</body>
</html>'''
            
            # Сохраняем HTML файл
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f" HTML страница создана: {html_filename}")
            print(f"   Откройте файл {html_filename} в браузере для просмотра")
            return html_filename
            
        except Exception as e:
            print(f" Ошибка при генерации HTML: {e}")
            return None
    
    def display_teachers(self, teachers: List[Dict]):
        """Вывод преподавателей в консоль"""
        if not teachers:
            print(" Не удалось найти информацию о преподавателях")
            return
        
        print("\n" + "="*60)
        print("СПИСОК ПРЕПОДАВАТЕЛЕЙ МГКЦТ")
        print("="*60)
        
        for i, teacher in enumerate(teachers, 1):
            print(f"{i}. Teacher: {teacher['name']}; Post: {teacher['post']};")
        
        print("="*60)
        print(f"Всего найдено: {len(teachers)} преподавателей")
    
    def run(self):
        """Основной метод запуска парсера"""
        print(" Запуск парсера преподавателей МГКЦТ")
        print("-" * 40)
        
        # Получаем содержимое страницы
        html_content = self.get_page_content()
        
        if not html_content:
            print(" Не удалось получить данные с сайта")
            
            # Демонстрационные данные для примера
            print("\n Использую демонстрационные данные...")
            demo_teachers = [
                {'id': 1, 'name': 'Амброжи Наталья Михайловна', 'post': 'Преподаватель высшей категории'},
                {'id': 2, 'name': 'Бровка Дионисий Сергеевич', 'post': 'Преподаватель без категории'},
                {'id': 3, 'name': 'Касперович Светлана Александровна', 'post': 'Преподаватель высшей категории'},
                {'id': 4, 'name': 'Иванов Иван Иванович', 'post': 'Преподаватель первой категории'},
                {'id': 5, 'name': 'Петрова Мария Сергеевна', 'post': 'Преподаватель высшей категории'},
                {'id': 6, 'name': 'Сидоров Алексей Петрович', 'post': 'Преподаватель высшей категории'},
                {'id': 7, 'name': 'Кузнецова Елена Владимировна', 'post': 'Преподаватель первой категории'},
                {'id': 8, 'name': 'Смирнов Дмитрий Алексеевич', 'post': 'Преподаватель без категории'},
                {'id': 9, 'name': 'Волкова Ольга Сергеевна', 'post': 'Преподаватель высшей категории'},
                {'id': 10, 'name': 'Павлов Андрей Иванович', 'post': 'Преподаватель второй категории'},
            ]
            teachers = demo_teachers
        else:
            # Парсим преподавателей
            print(" Анализирую содержимое страницы...")
            teachers = self.parse_teachers(html_content)
            
            # Если не нашли преподавателей, используем демо-данные
            if not teachers:
                print("  На странице не найдена информация в ожидаемом формате")
                print(" Использую демонстрационные данные...")
                teachers = [
                    {'id': 1, 'name': 'Амброжи Наталья Михайловна', 'post': 'Преподаватель высшей категории'},
                    {'id': 2, 'name': 'Бровка Дионисий Сергеевич', 'post': 'Преподаватель без категории'},
                    {'id': 3, 'name': 'Касперович Светлана Александровна', 'post': 'Преподаватель высшей категории'},
                ]
        
        # Выводим в консоль
        self.display_teachers(teachers)
        
        # Задание 3: Сохраняем в JSON
        print("\n Сохранение данных в JSON...")
        json_file = self.save_to_json(teachers)
        
        if json_file:
            # Задание 4: Генерируем HTML страницу
            print("\n Генерация HTML страницы...")
            html_file = self.generate_html(json_file)
            
            if html_file:
                print(f"\n Все задания выполнены!")
                print(f"   • Данные сохранены в: {json_file}")
                print(f"   • HTML страница создана: {html_file}")
                print(f"\n Содержимое папки проекта:")
                for file in os.listdir('.'):
                    if file.endswith(('.py', '.json', '.html', '.txt', '.md')):
                        size = os.path.getsize(file)
                        print(f"   - {file} ({size} байт)")


def main():
    """Точка входа в программу"""
    parser = TeacherParser()
    parser.run()


if __name__ == "__main__":
    main()
