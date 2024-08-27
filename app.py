from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Importe o CORS
import sqlite3

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
CORS(app)  # Adicione CORS ao seu app Flask
jwt = JWTManager(app)


def conn_db():
    return sqlite3.connect('zoonation.db')

def init_db():
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS animals(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                breed TEXT,
                age INTEGER,
                description TEXT NOT NULL,
                city TEXT NOT NULL,
                contact TEXT NOT NULL
            )
        '''
        )
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        '''
    )
    conn.commit()
    conn.close()

    
init_db()

# users
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Nome de usuário e senha são necessários!'}), 400

    hashed_password = generate_password_hash(password)
    
    conn = conn_db()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Nome de usuário já existe!'}), 400
    finally:
        conn.close()

    return jsonify({'message': 'Usuário registrado com sucesso!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Nome de usuário e senha são necessários!'}), 400

    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        access_token = create_access_token(identity={'username': username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Credenciais inválidas!'}), 401
    

# animals
@app.route('/pets',methods=['POST'])
def add_pet():
    new_pet = request.get_json()
    name = new_pet.get('name')
    breed = new_pet.get('breed')
    age = new_pet.get('age')
    description = new_pet.get('description')
    city = new_pet.get('city')
    contact = new_pet.get('contact')

    try:
        conn = conn_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO animals (name, breed, age, description, city, contact) VALUES (?, ?, ?, ?, ?, ?)', (name, breed, age, description, city, contact))
        conn.commit()
        return 'deu certo'
    except sqlite3.Error as e:
        return jsonify({'mensagem': f'Erro ao adicionar pet: {e}'}), 500
    finally:
        conn.close()

@app.route('/pets', methods=['GET'])
def read_pets():
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM animals')
    rows = cursor.fetchall()
#cursor.fetchall retorna uma lista de tuplas, onde cada tupla é uma linha da tabela
    conn.close()
    pets = []
    for row in rows:
        pets.append({
            'id': row[0],
            'name': row[1],
            'breed': row[2],
            'age': row[3],
            'description': row[4],
            'city': row[5],
            'contact': row[6]
        })

    return jsonify(pets)

@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_animal(pet_id):
    data = request.json
    name = data.get('name')
    breed = data.get('breed')
    age = data.get('age')
    description = data.get('description')
    city = data.get('city')
    contact = data.get('contact')

    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("""
            UPDATE animals
            SET name = ?, breed = ?, age = ?, description = ?, city = ?, contact = ?
            WHERE id = ?
                   """, (name, breed, age, description, city, contact, pet_id))
    conn.commit()
    conn.close()

    return jsonify({'mensagem': 'Pet atualizado com sucesso!'})


@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_animal(pet_id):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM animals WHERE id = ?',(pet_id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Pet deletado com sucesso!'})
    
if __name__ == '__main__':
    app.run(debug=True)