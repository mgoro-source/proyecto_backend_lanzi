from flask import Blueprint, jsonify, request
from ..utils import construir_error_api
from ..constantes import (
    ERROR_CODE_EMPTY_BODY,
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_DEPORTE_NOT_FOUND,
    ERROR_CODE_CANCHA_HAS_RESERVATIONS,
    ERROR_CODE_INTERNAL_ERROR,
)
from ..validators.canchas import (
    validar_filtros_canchas,
    validar_crear_cancha,
    validar_consulta_disponibilidad,
    validar_id_cancha,
    validar_actualizar_cancha,
)
from ..services.canchas import (
    listar_canchas,
    crear_cancha,
    consultar_canchas_disponibles,
    obtener_cancha_por_id,
    actualizar_cancha,
    eliminar_cancha,
)
canchas_bp = Blueprint('canchas', __name__)

@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
 
 #"""Listar canchas con paginación (_limit, _offset) y filtros opcionales."""
    filtros, error_val = validar_filtros_canchas(request.args)
    if error_val:
        if isinstance(error_val, tuple):
            cod_err, desc_err = error_val
        else:
            cod_err, desc_err = "BAD_REQUEST", error_val
        return jsonify(construir_error_api(cod_err, "Parámetros de consulta inválidos", "error", desc_err)), 400
    resultado, error_srv = listar_canchas(filtros)
    if error_srv:
        return jsonify(construir_error_api(ERROR_CODE_INTERNAL_ERROR, "Error interno del servidor", "error", error_srv)), 500
    
    if not resultado.get('canchas'):
        return '', 204
    
    return jsonify(resultado), 200


@canchas_bp.route('/canchas', methods=['POST'])
def post_cancha():

# """Crear una nueva cancha."""
    body = request.get_json(silent=True)
    if body is None:
        return jsonify(construir_error_api(
            ERROR_CODE_EMPTY_BODY,
            "Cuerpo JSON inválido",
            "error",
            "El cuerpo de la solicitud debe ser un objeto JSON válido."
        )), 400
    
    datos, error_val = validar_crear_cancha(body)
    if error_val:
        if isinstance(error_val, tuple):
            cod_err, desc_err = error_val
        else:
            cod_err, desc_err = "BAD_REQUEST", error_val
        return jsonify(construir_error_api(cod_err, "Datos de cancha inválidos", "error", desc_err)), 400
    cancha, error_srv = crear_cancha(datos)
    if error_srv:
        if error_srv.get('code') in ['NOT_FOUND', ERROR_CODE_DEPORTE_NOT_FOUND]:
            return jsonify(construir_error_api(
                ERROR_CODE_DEPORTE_NOT_FOUND,
                "Deporte no encontrado",
                "error",
                error_srv.get('description', 'El deporte indicado no existe.')
            )), 404
        return jsonify(construir_error_api(
            ERROR_CODE_INTERNAL_ERROR,
            "Error al crear cancha",
            "error",
            error_srv.get('description', 'Error interno')
        )), 500
    
    return jsonify(cancha), 201


@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def get_canchas_disponibles():
 
 #"""Consultar canchas activas e independientes que estén libres durante un intervalo."""
    params, error_val = validar_consulta_disponibilidad(request.args)
    if error_val:
        if isinstance(error_val, tuple):
            cod_err, desc_err = error_val
        else:
            cod_err, desc_err = "BAD_REQUEST", error_val
        return jsonify(construir_error_api(cod_err, "Parámetros de disponibilidad inválidos", "error", desc_err)), 400
    
    resultado, error_srv = consultar_canchas_disponibles(params)
    if error_srv:
        return jsonify(construir_error_api(ERROR_CODE_INTERNAL_ERROR, "Error interno del servidor", "error", error_srv)), 500
    return jsonify(resultado), 200


@canchas_bp.route('/canchas/<id>', methods=['GET'])
def get_cancha_por_id(id):
 
 #"""Obtener los datos de una cancha por su ID."""
    cancha_id, error_val = validar_id_cancha(id)
    if error_val:
        if isinstance(error_val, tuple):
            cod_err, desc_err = error_val
        else:
            cod_err, desc_err = "BAD_REQUEST", error_val
        return jsonify(construir_error_api(cod_err, "Identificador de cancha inválido", "error", desc_err)), 400
    cancha, error_srv = obtener_cancha_por_id(cancha_id)
    if error_srv:
        if error_srv.get('code') in ['NOT_FOUND', ERROR_CODE_CANCHA_NOT_FOUND]:
            return jsonify(construir_error_api(
                ERROR_CODE_CANCHA_NOT_FOUND,
                "Cancha no encontrada",
                "error",
                error_srv.get('description', 'La cancha solicitada no existe.')
            )), 404
        return jsonify(construir_error_api(
            ERROR_CODE_INTERNAL_ERROR,
            "Error interno del servidor",
            "error",
            error_srv.get('description', 'Error interno')
        )), 500
    return jsonify(cancha), 200


@canchas_bp.route('/canchas/<id>', methods=['PATCH'])
def patch_cancha(id):
 
 #"""Actualizar parcialmente los atributos de una cancha existente."""
    cancha_id, error_id = validar_id_cancha(id)
    if error_id:
        if isinstance(error_id, tuple):
            cod_err, desc_err = error_id
        else:
            cod_err, desc_err = "BAD_REQUEST", error_id
        return jsonify(construir_error_api(cod_err, "Identificador de cancha inválido", "error", desc_err)), 400
    
    body = request.get_json(silent=True)
    if not body:
        return jsonify(construir_error_api(
            ERROR_CODE_EMPTY_BODY,
            "Cuerpo de actualización vacío",
            "error",
            "Debe proporcionar un objeto JSON con al menos un campo a actualizar."
        )), 400
    
    datos, error_val = validar_actualizar_cancha(body)
    if error_val:
        if isinstance(error_val, tuple):
            cod_err, desc_err = error_val
        else:
            cod_err, desc_err = "BAD_REQUEST", error_val
        return jsonify(construir_error_api(cod_err, "Datos de actualización inválidos", "error", desc_err)), 400
    
    exito, error_srv = actualizar_cancha(cancha_id, datos)
    if error_srv:
        if error_srv.get('code') in ['NOT_FOUND', ERROR_CODE_CANCHA_NOT_FOUND]:
            return jsonify(construir_error_api(
                ERROR_CODE_CANCHA_NOT_FOUND,
                "Cancha no encontrada",
                "error",
                error_srv.get('description', 'La cancha solicitada no existe.')
            )), 404
        return jsonify(construir_error_api(
            ERROR_CODE_INTERNAL_ERROR,
            "Error al actualizar cancha",
            "error",
            error_srv.get('description', 'Error interno')
        )), 500
    
    return '', 204


@canchas_bp.route('/canchas/<id>', methods=['DELETE'])
def delete_cancha(id):
    #"""Eliminar una cancha si no tiene reservas asociadas."""
    cancha_id, error_id = validar_id_cancha(id)
    if error_id:
        if isinstance(error_id, tuple):
            cod_err, desc_err = error_id
        else:
            cod_err, desc_err = "BAD_REQUEST", error_id
        return jsonify(construir_error_api(cod_err, "Identificador de cancha inválido", "error", desc_err)), 400
    
    exito, error_srv = eliminar_cancha(cancha_id)
    if error_srv:
        if error_srv.get('code') in ['NOT_FOUND', ERROR_CODE_CANCHA_NOT_FOUND]:
            return jsonify(construir_error_api(
                ERROR_CODE_CANCHA_NOT_FOUND,
                "Cancha no encontrada",
                "error",
                error_srv.get('description', 'La cancha solicitada no existe.')
            )), 404
        if error_srv.get('code') in ['CONFLICT', ERROR_CODE_CANCHA_HAS_RESERVATIONS]:
            return jsonify(construir_error_api(
                ERROR_CODE_CANCHA_HAS_RESERVATIONS,
                "No se puede eliminar la cancha",
                "error",
                error_srv.get('description', 'La cancha tiene reservas asociadas.')
            )), 409
        return jsonify(construir_error_api(
            ERROR_CODE_INTERNAL_ERROR,
            "Error al eliminar cancha",
            "error",
            error_srv.get('description', 'Error interno')
        )), 500
    
    return '', 204