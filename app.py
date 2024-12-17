from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

GRADE4_FILE = 'static/data/grade4.characters.json'
GRADE5_FILE = 'static/data/grade5.characters.json'
GRADE6_FILE = 'static/data/grade6.characters.json'

def ensure_chars_file():
    if not os.path.exists('static/data'):
        os.makedirs('static/data')
    # 确保每个年级的文件都存在
    for file_path in [GRADE4_FILE, GRADE5_FILE, GRADE6_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)  # 初始化为空数组

def get_grade_characters(grade):
    file_map = {
        'grade4': GRADE4_FILE,
        'grade5': GRADE5_FILE,
        'grade6': GRADE6_FILE
    }
    file_path = file_map.get(grade)
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_grade_characters(grade, chars):
    file_map = {
        'grade4': GRADE4_FILE,
        'grade5': GRADE5_FILE,
        'grade6': GRADE6_FILE
    }
    file_path = file_map.get(grade)
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chars, f, ensure_ascii=False)

@app.route('/')
def index():
    grade4_chars = get_grade_characters('grade4')
    grade5_chars = get_grade_characters('grade5')
    grade6_chars = get_grade_characters('grade6')
    
    print("Grade 5 file path:", GRADE5_FILE)  # 添加这行
    print("Grade 5 chars:", grade5_chars)      # 添加这行
    
    return render_template('index.html', 
                         grade4_chars=grade4_chars,
                         grade5_chars=grade5_chars,
                         grade6_chars=grade6_chars)

@app.route('/practice/')
@app.route('/practice/<char>')
def practice(char=None):
    if char is None:
        # 从查询参数中获取字符
        char = request.args.get('char', '')
    
    # 将字符串转换为字符列表
    chars = list(char)
    current_index = request.args.get('index', 0, type=int)
    current_char = chars[current_index] if chars else ''
    
    # 处理导航
    prev_chars = None
    next_chars = None
    
    if len(chars) > 1:
        if current_index > 0:
            prev_chars = char + "?index=" + str(current_index - 1)
        if current_index < len(chars) - 1:
            next_chars = char + "?index=" + str(current_index + 1)
    
    return render_template('practice.html',
                         chars=chars,
                         current_char=current_char,
                         current_index=current_index,
                         prev_chars=prev_chars,
                         next_chars=next_chars)

@app.route('/add_char', methods=['POST'])
def add_char():
    char = request.form.get('char', '').strip()
    grade = request.form.get('grade', 'grade6')
    if char and len(char) == 1:
        chars = get_grade_characters(grade)
        if char not in chars:
            chars.append(char)
            save_grade_characters(grade, chars)
            return jsonify({'success': True, 'char': char})
    return jsonify({'success': False})

@app.route('/delete_char/<char>/<grade>')
def delete_char(char, grade):
    chars = get_grade_characters(grade)
    if char in chars:
        chars.remove(char)
        save_grade_characters(grade, chars)
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    ensure_chars_file()  # 确保文件存在
    app.run(host='0.0.0.0', port=5000, debug=True) 