from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
IMAGE_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

USERS = {
    'user1': 'password1',
    'user2': 'password2'
}

# ...
def create_file(file_name, content):
    try:
        with open(file_name, 'w') as file:
            file.write(content)
        return "File created successfully."
    except:
        return "An error occurred while creating the file."

def read_file(file_name):
    try:
        with open(file_name, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return "File not found."

file_name = "filename.txt"
file_content = "This is the content of the file."

# Create the file
create_result = create_file(file_name, file_content)
print(create_result)

# Read the file
read_result = read_file(file_name)
print(read_result)


def get_files():
    files = []
    activity_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'activity')

    if os.path.exists(activity_folder_path):
        activity_files = [f for f in os.listdir(activity_folder_path) if os.path.isfile(os.path.join(activity_folder_path, f))]

        for filename in activity_files:
            file_path = os.path.join(activity_folder_path, filename)
            with open(file_path, 'r') as file:
                content = file.read()

            files.append({'filename': filename, 'content': content})

    return files

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    files = get_files()
    return render_template('upload.html', files=files, current_user=session['username'])

# ...
@app.route('/activity', methods=['GET', 'POST'])
def activity():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        text = request.form['text']

        if file and is_allowed_extension(file.filename):
            filename = secure_filename(file.filename)
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'activity')

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            file.save(os.path.join(folder_path, filename))

            # Save the text somewhere (e.g., database)
            save_text(text)

            return redirect(url_for('activity'))

    files = get_files()
    return render_template('activity.html', files=files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        category = request.form['category']

        if file and is_allowed_extension(file.filename):
            filename = secure_filename(file.filename)
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], category)

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            file.save(os.path.join(folder_path, filename))

            return redirect(url_for('index'))

    return render_template('upload.html')

def is_allowed_extension(filename):
    return True

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/download/<path:category>/<path:filename>')
def download(category, filename):
    if 'username' not in session:
        return redirect(url_for('login'))

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], category)

    if os.path.isfile(os.path.join(folder_path, filename)):
        return send_from_directory(folder_path, filename, as_attachment=True)

    return 'File not found'

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['IMAGE_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
