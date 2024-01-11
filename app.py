from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo # Necesita el paquete Flask-PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId
from datetime import date, datetime

app = Flask(__name__)

# Para conexiones en la nube se requiere tener instalado el paquete dnspython
# También se requiere instalar el paquete pymongo[srv]

app.config["MONGO_URI"] = 'mongodb+srv://daniromero:palomeras@cluster0.k5qwzob.mongodb.net/pais'

mongo = PyMongo(app)

#obtiene todos los usuarios
@app.route('/', methods=['GET'])
def get_paises():
    paises = mongo.db.paises.find()
    response = json_util.dumps(paises) # Strings con formato JSON

    return Response(response, mimetype='application/json') # Formato JSON

#busca un usuario por id
@app.route('/paises/<nompais>', methods=['GET'])
def get_pais_id(nompais):
    paises = mongo.db.paises.find_one({'nompais': nompais})
    if paises:
        response = json_util.dumps(paises) # Strings con formato JSON

        return Response(response, mimetype='application/json') # Formato JSON

#crea usuarios
@app.route('/paises', methods=['POST'])
def create_pais():
    request_data = request.get_json()
    # Comprobando que se ha cada uno de los datos
    if 'nompais' in request_data:
        nompais = request.json['nompais']
    else:
        return datos_incompletos()
    if 'capital' in request_data:
        capital = request.json['capital']
    else:
        return datos_incompletos()
    if 'habitantes' in request_data:
        habitantes_str = request.json['habitantes']
        if not habitantes_str.isdigit():
            return habitantes_no_valido()
        habitantes = int(habitantes_str)
    else:
        return datos_incompletos()
    
    if 'diaNacional' in request_data:
        diaNacional_str = request.json['diaNacional']
        try:
            diaNacional = datetime.strptime(diaNacional_str, '%Y-%m-%d')
        except ValueError:
            return dia_nacional_no_valido()
    else:
        return datos_incompletos()
    
    id = mongo.db.paises.insert_one({'nompais': nompais, 'capital':
    capital, 'habitantes': habitantes, "diaNacional": diaNacional})
    response = {
    'id': str(id),
    'nompais': nompais,
    'capital': capital,
    'habitantes': habitantes,
    "diaNacional": diaNacional
    }
    return response

#elimina usuarios
@app.route('/paises/<nompais>', methods=['DELETE'])
def delete_pais(nompais):
    paises = mongo.db.paises.find_one({'_id': ObjectId(nompais)})

    if paises: # Encontrado para ser eliminado
        paisborrar = mongo.db.paises.delete_one({'_id': ObjectId(nompais)})
        response = jsonify({'mensaje': nompais + 'fue eliminado satisfactoriamente'})
        return response
    else:
        return not_found()
@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
    'mensaje': 'Recurso no encontrado: ' + request.url,
    'status': 404
    })
    response.status_code = 404
    return response

#modifica usuarios
@app.route('/paises/<pais>', methods=['PUT'])
def update_pais(pais):
    request_data = request.get_json()
    # Comprobando que se ha cada uno de los datos
    if 'nompais' in request_data:
        nompais = request.json['nompais']
    else:
        return datos_incompletos()
    if 'capital' in request_data:
        capital = request.json['capital']
    else:
        return datos_incompletos()
    if 'habitantes' in request_data:
        habitantes_str = request.json['habitantes']
        if not habitantes_str.isdigit():
            return habitantes_no_valido()
        habitantes = int(habitantes_str)
    else:
        return datos_incompletos()
    
    if 'diaNacional' in request_data:
        diaNacional_str = request.json['diaNacional']
        try:
            diaNacional = datetime.strptime(diaNacional_str, '%Y-%m-%d')
        except ValueError:
            return dia_nacional_no_valido()
    else:
        return datos_incompletos()
    
    paisBuscado = mongo.db.paises.find_one({'nompais': pais})
    if paisBuscado: # Encontrado para ser modificado
        mongo.db.paises.update_one({'nompais': pais}, {'$set':
        {
        'nompais': nompais,
        'capital': capital,
        'habitantes': habitantes,
        "diaNacional": diaNacional
        }})
    else:
        return not_found()
    response = jsonify({'mensaje': pais + ' fue actualizado satisfactoriamente'})
    return response

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'mensaje': 'Recurso no encontrado: ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return response
@app.errorhandler(400)
def datos_incompletos(error=None):
    response = jsonify({
        'mensaje': 'Datos incompletos',
        'status': 400
    })
    response.status_code = 400
    return response

@app.errorhandler(422)
def habitantes_no_valido(error=None):
    response = jsonify({
        'mensaje': 'Habitantes debe ser un número entero',
        'status': 422
    })
    response.status_code = 422
    return response

@app.errorhandler(422)
def dia_nacional_no_valido(error=None):
    response = jsonify({
        'mensaje': 'Formato de diaNacional no válido. Utilice el formato YYYY-MM-DD',
        'status': 422
    })
    response.status_code = 422
    return response

if __name__ == "__main__":
    app.run(debug=True)