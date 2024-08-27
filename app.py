from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

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
    conn.commit()
    conn.close()
    
init_db()

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

    
if __name__ == '__main__':
    app.run(debug=True)