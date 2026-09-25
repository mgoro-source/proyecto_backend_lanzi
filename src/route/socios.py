from flask import Blueprint, jsonify, request
from src.services.socios import (crear_socio_service,
                                          obtener_socio_por_id_service,
                                          listar_socios_service,
                                          actualizar_socio_service)

socios_bp = Blueprint('socios', __name__)

@socios_bp.route('/socios', methods=['GET'])
def listar_socios():
    
    parametros = request.args.to_dict()
    resultado = listar_socios_service(parametros)
    
    return jsonify(resultado), 200

@socios_bp.route('/socios', methods=['POST'])
def crear_socio():
    
    datos = request.get_json(silent = True) or {}
    nuevo_socio = crear_socio_service(datos)
    
    return jsonify(nuevo_socio), 201

@socios_bp.route ('/socios/<int:id>', methods=['GET'])
def obtener_socio(id):
    
    socio = obtener_socio_por_id_service(id)
    
    return jsonify(socio), 200

@socios_bp.route ('/socios/<int:id>', methods=['PATCH'])
def actualizar_socio(id):
    
    datos = request.get_json(silent = True) or {}
    socio_actualizado = actualizar_socio_service(id, datos)
    
    return jsonify(socio_actualizado), 200
