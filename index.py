import base64
import os
from google import genai
from google.genai import types
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import mysql.connector
import json

KEY = os.getenv("KEY")
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
KEYS = [f"{KEY}", "123"]
WORK_KEY_INDEX = 0

def generate_text(promt):
    while (True):
        global WORK_KEY_INDEX
        client = genai.Client(
            api_key=KEYS[WORK_KEY_INDEX],
        )

        model = "gemini-2.5-flash-lite"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=promt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
        )
        full_response = ""
        try:
            for chunk in client.models.generate_content_stream(model=model, contents=contents, config=generate_content_config,):
                full_response += chunk.text
            break
        except Exception as proebali:
            print(f"{KEYS[WORK_KEY_INDEX]} сломан")
            WORK_KEY_INDEX += 1
            print(proebali)
    return full_response
    

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path = urllib.parse.unquote(self.path)
            if path.startswith('/users/'):
                try:
                    file_path = path.lstrip('/')
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        with open(file_path, 'rb') as f:
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.end_headers()
                            self.wfile.write(f.read())
                            return
                    else:
                        self.send_error(404, "File Not Found")
                except Exception as e:
                    self.send_error(500, f"Server Error: {e}")
                return

            if path == '/':
                try:
                    with open('html/main.html', 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(f.read())
                except FileNotFoundError:
                    self.send_error(404, "File Not Found")
                return
            elif path == '/css':
                try:
                    with open('html/test.css', 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/css; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(f.read())
                except FileNotFoundError:
                    self.send_error(404, "File Not Found")
                return
            elif path == '/webc':
                try:
                    with open('html/web_creator.html', 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(f.read())     
                except FileNotFoundError:
                    self.send_error(404, "File Not Found")
                return
            self.send_error(404, "Not Found")
            
        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected during request processing")
        except Exception as e:
            print(f"Unexpected error: {e}")
            try:
                self.send_error(500, "Internal Server Error")
            except:
                pass
    def do_POST(self):
        if self.path == '/generate':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = urllib.parse.parse_qs(post_data)
                
                promt_list = data.get('promt')
                print(data)
                promt = promt_list[0]
                print(promt)
                Otvet_ot_ii = generate_text(promt) 
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                print(Otvet_ot_ii)
                otvet = {'Uspeh': True, 'Otvet_ot_ii': Otvet_ot_ii}
                self.wfile.write(json.dumps(otvet).encode('utf-8'))
            except Exception as oshibka:
                print(oshibka)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                otvet = {'Uspeh': False, 'Otvet_ot_ii': 'промттытватытыв'}
                self.wfile.write(json.dumps(otvet).encode('utf-8'))
        elif self.path == '/generate_html':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = urllib.parse.parse_qs(post_data)
                print(data)
                site_name = data.get('site_name')
                site_name = site_name[0]
                style = data.get('style')
                style = site_name[0]
                color1 = data.get('color1')
                color_1 = color1[0]
                color2 = data.get('color2')
                color_2 = color2[0]
                color3 = data.get('color3')
                color_3 = color3[0]
                email = data.get('email_send')
                email = email[0].replace('.', '')
                
                final_promt = f"""Ты — экспертный AI Web Designer и Full-stack Developer. Твоя задача: создать современный, адаптивный одностраничный сайт (Landing Page) на основе входных данных и предоставить Html и css код в одном файле.

### ВХОДНЫЕ ДАННЫЕ:
1. Название сайта: {site_name}
2. Стилистика: {style}
3. Цветовая палитра: 
   - Основной (Background/Primary): {color_1}
   - Дополнительный 1 (Buttons/Accents): {color_2}
   - Дополнительный 2 (Secondary Text/Icons): {color_3}

### ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ К РЕАЛИЗАЦИИ:
- Структура: Сайт должен содержать Hero-секцию, блоки, секцию преимуществ и подвал с контактной формой.
- Адаптивность: Сайт должен идеально отображаться на мобильных устройствах и десктопах.
- Стилизация: 
    - Если "Строгий": используй прямые углы, шрифты Serif, много "белого пространства", консервативные отступы.
    - Если "Минимализм": используй чистые линии, шрифты Sans-serif, отсутствие лишних декоративных элементов.
    - Если "Забавный": используй скругленные углы (border-radius: 20px+), игровые анимации, мягкие тени и дружелюбные шрифты.
- Работа с цветом: Строго соблюдай переданные RGB-значения. Основной цвет должен доминировать в фоне или крупных блоках.

### ИНСТРУКЦИЯ ПО ВЫДАЧЕ:
1. Создай полный HTML/CSS/JS код.
2. Верни файл исключительно с HTML/CSS/JS кодом в ОДНОМ файле БЕЗ ЛИШНИХ КОММЕНТАРИЕВ """
                Otvet_ot_ii = generate_text(final_promt)
                Otvet_ot_ii = Otvet_ot_ii[7:-3]
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                print(Otvet_ot_ii)
                user_dir = os.path.join('users', email)
                os.makedirs(user_dir, exist_ok=True)

                existing_files = [f for f in os.listdir(user_dir) if f.endswith('.html')]
                next_number = len(existing_files) + 1
                file_name = f"{next_number}.html"
                full_file_path = os.path.join(user_dir, file_name)
                
                with open(full_file_path, 'w', encoding='utf-8') as f:
                    f.write(Otvet_ot_ii)
                link = f"http://blue.fnode.me:25548/users/{email}/{file_name}"
                otvet = {'Uspeh': True, 'Otvet_ot_ii': link}
                self.wfile.write(json.dumps(otvet).encode('utf-8'))
            except Exception as oshibka:
                print(oshibka)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                otvet = {'Uspeh': False, 'Otvet_ot_ii': 'промттытватытыв'}
                self.wfile.write(json.dumps(otvet).encode('utf-8'))
                
        elif self.path == '/register':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = urllib.parse.parse_qs(post_data)
                
                email = data.get('email', [''])[0]
                login = data.get('login', [''])[0]
                password = data.get('password', [''])[0]
                
                # Проверяем обязательные поля
                if not all([email, login, password]):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'message': 'Все поля обязательны'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                db = mysql.connector.connect(
                    host=f'{HOST}',
                    user=f'{USER}',
                    password=f'{PASSWORD}',
                    database=f'{DATABASE}'
                )
                cursor = db.cursor()
                cursor.execute('SELECT * FROM `users` WHERE email = %s OR login = %s', (email, login))
                if cursor.fetchone():
                    print('пользователь с таким email/логин уже существует')
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'message': 'пользователь с таким email/логин уже существует'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                cursor.execute('INSERT INTO users (email, login, password) VALUES (%s, %s, %s)', (email, login, password))
                db.commit()
                try:
                    # Создаем безопасное имя папки из email
                    safe_email = email.replace('.', '')
                    user_folder = os.path.join('users', safe_email)
                    
                    # Создаем папку если её нет
                    os.makedirs(user_folder, exist_ok=True)
                    print(f"Создана папка для пользователя: {user_folder}")
                except Exception as e:
                    print(f"Ошибка при создании папки: {e}")
                print('регистрация прошла успешно')
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': True, 'message': 'регистрация прошла успешно'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return 
            except Exception as e:
                print(f'ошибка обработки пост запроса {e}')
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'message': 'Внутренняя ошибка сервера'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif self.path == '/login':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = urllib.parse.parse_qs(post_data)

                identifier = data.get('login', [''])[0]
                password = data.get('password', [''])[0]

                if not identifier or not password:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'message': 'Все поля обязательны'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                db = mysql.connector.connect(
                    host=f'{HOST}',
                    user=f'{USER}',
                    password=f'{PASSWORD}',
                    database=f'{DATABASE}'
                )
                cursor = db.cursor()
                cursor.execute('SELECT * FROM users WHERE email = %s OR login = %s', (identifier, identifier))
                user = cursor.fetchone()

                if not user:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'message': 'Пользователь с таким логином/email не существует'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                if user[3] != password:  # Сравниваем пароль из базы
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'message': 'Неверный пароль'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': True, 'message': 'Вход выполнен успешно', 'redirect': '/webc'}
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                print(f'Ошибка при обработке входа: {e}')
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'message': 'Внутренняя ошибка сервера'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")
def run_http_server():
    try:
        http_server = HTTPServer(('0.0.0.0', 25548), HTTPRequestHandler)
        print("HTTP сервер запущен на порту 25548")
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("Сервер остановлен по запросу пользователя")
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")

if __name__ == '__main__':
    run_http_server()