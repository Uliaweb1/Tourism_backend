from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import psycopg2
from jsonschema import validate
from datetime import datetime
from flask import request, jsonify, Flask
from flask_cors import CORS

app = Flask('tourism_backend')
CORS(app)

class backend_db():
    username = 'Kolomiets'
    password = '123a1'
    database = 'FrontendProject6s'
    host = 'localhost'
    port = '5432'
    def init(self):
        pass

    def connection(self):
        return psycopg2.connect(user=self.username, password=self.password, dbname=self.database, host=self.host, port=self.port)


def add_massage(user, message):
    add_message_sql = f"call insert_message('{user}', '{message}');"
    conn = backend_db().connection()
    with conn:
        cur = conn.cursor()
        cur.execute(add_message_sql)


def delete_massage(message_id):
    delete_message_sql = f"DELETE FROM chat_messages WHERE message_id = '{message_id}';"
    conn = backend_db().connection()
    with conn:
        cur = conn.cursor()
        cur.execute(delete_message_sql)


def recreate_tables():
    query_messages = open('recreate.sql', 'r').read()
    conn = backend_db().connection()
    with conn:
        print("Database opened successfully")
        cur = conn.cursor()
        cur.execute(query_messages)



def get_chat_messages():
    query_messages = open('query_messages.sql', 'r').read()
    conn = backend_db().connection()
    messages = []
    with conn:
        print("Database opened successfully")
        cur = conn.cursor()
        cur.execute(query_messages)
        rows = cur.fetchall()
        for row in rows:
            result_dict = dict(zip([column[0] for column in cur.description], row))
            # Convert datetime objects to string format
            for key, value in result_dict.items():
                if isinstance(value, datetime):
                    result_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            messages.append(result_dict)
    return messages

def login(username, password):
    conn = backend_db().connection()
    users = []
    with conn:
        print("Database opened successfully")
        cur = conn.cursor()
        cur.execute(f"select * from users where users.username = '{username}' and users.password = '{password}';")
        rows = cur.fetchall()
        for row in rows:
            result_dict = dict(zip([column[0] for column in cur.description], row))
            users.append(result_dict)
    return len(users) > 0

def register(username, email, password):
    conn = backend_db().connection()
    result = {}
    users = []
    with conn:
        print("Database opened successfully")
        cur = conn.cursor()
        try:
            cur.execute(f"INSERT INTO users(username, email, password) VALUES('{username}', '{email}', '{password}');")
            conn.commit()
            print("User created: {username}")
            cur.execute(f"select * from users where users.username = '{username}' and users.password = '{password}';")
            rows = cur.fetchall()
            for row in rows:
                result_dict = dict(zip([column[0] for column in cur.description], row))
                users.append(result_dict)
            result = {'register': ('success' if (len(users) > 0) else 'failed')}
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print(f"Error: {e}")
            result = {'register': 'failed', 'reason': 'user already exists'}
    return result


@app.route('/api/users', methods=['POST'])
def flask_login():
    schema_action = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "user": {"type": "string"},
            "email": {"type": "string"},
            "password": {"type": "string"}
        },
        "required": ["action", "user", "password"]
    }
    post_data_json = request.get_json()
    try:
        validate(instance=post_data_json, schema=schema_action)
        print("JSON data is valid against the schema.")
        response_data = {}
        if post_data_json["action"] == "login":
            if login(post_data_json["user"], post_data_json["password"]):
                response_data = {'login': 'success'}
            else:
                response_data = {'login': 'failed'}
        elif post_data_json["action"] == "register":
            response_data = register(post_data_json["user"], post_data_json["email"], post_data_json["password"])
        return json.dumps(response_data).encode('utf-8'), 200
    except:
        return jsonify({'error': 'Invalid request'}), 400


@app.route('/api/messages', methods=['POST'])
def flask_add_message():
    schema_add_message = {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "message": {"type": "string"}
        },
        "required": ["user_id", "message"]
    }
    post_data_json = request.get_json()
    try:
        validate(instance=post_data_json, schema=schema_add_message)
        print("JSON data is valid against the schema.")
        add_massage(post_data_json["user_id"], post_data_json["message"])
        return json.dumps({'messages': get_chat_messages()}).encode('utf-8'), 200
    except:
        return jsonify({'error': 'Invalid request'}), 400


@app.route('/api/messages', methods=['GET'])
def flask_get_message():
    return json.dumps({'messages': get_chat_messages()}).encode('utf-8'), 200


@app.route('/api/messages/<message_id>', methods=['DELETE'])
def flask_delete_message(message_id):
    delete_massage(message_id)
    return json.dumps({'messages': get_chat_messages()}).encode('utf-8'), 200

def run_server(port=8080):
    print(f'Starting Flask HTTP server on port {port}...')
    app.run(port=port, debug=True)
    print('Stopping HTTP server...')


if __name__ == '__main__':
    # recreate_tables()
    messages = get_chat_messages()
    for m in messages:
        print(m)
    run_server()
