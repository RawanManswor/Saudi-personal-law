from flask import Flask, render_template, request, jsonify
import os
from chatbot import SaudiPersonalLawAssistant
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
chatbot = SaudiPersonalLawAssistant()
app.config['SECRET_KEY']=""

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app) 
# Inside your Flask route or function where you're using MySQL functionality
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/edu_systems')
def systems():
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM educational_system")
        edu_systems = cursor.fetchall()

    edu_systems_with_systems = []

    for edu_system in edu_systems:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM systems WHERE system_id = %s", (edu_system[0],))
            systems = cursor.fetchall()
        
        edu_systems_with_systems.append({
            'edu_system': edu_system,
            'systems': systems
        })

    return render_template('systems.html', edu_systems_with_systems=edu_systems_with_systems)

@app.route('/forms')
def forms():
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM form_template")
        form_templates = cursor.fetchall()

    form_templates_with_forms = []

    for form_template in form_templates:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM forms WHERE form_id = %s", (form_template[0],))
            forms = cursor.fetchall()
        
        form_templates_with_forms.append({
            'form_template': form_template,
            'forms': forms
        })

    return render_template('forms.html', form_templates_with_forms=form_templates_with_forms)

@app.route('/chatbot')
def chatbo():
    return render_template('chatbot.html')

@app.route('/get', methods=['POST'])
def get_bot_response():
    if request.method == 'POST':
        message = request.form['msg']
        chatbot.chat_input(message)
        response = chatbot.messages[-1]['content']
        return jsonify(response)
    return jsonify('Error: Invalid request')

if __name__ == "__main__":
     app.run(host="localhost", port=8000, debug=False)