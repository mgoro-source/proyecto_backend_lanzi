from flask import Blueprint, request, jsonify
from src.services.reservas_services import (
    crear_reserva_service,
    cambiar_estado_service,
    _mapear_a_schema
)
from src.repositories.reservas_reposit import (
    listar_reservas,
    obtener_reserva_por_id
)

from constantes import (
    LIMITE_PAGINACION_DEFECTO,
    OFFSET_PAGINACION_DEFECTO,
    LIMIT_MAXIMO,
    LIMIT_MINIMO,
    CAMPOS_PERMITIDOS_ESTADO,
    CAMPOS_REQUERIDOS_CREACION
)

reservas_bp = Blueprint('reservas', __name__)

# Auxiliar
def generar_hateoas_links(limit, offset, total, params_extra):
    base_url = request.base_url
    
    def build_url(off):
        p = params_extra.copy()
        p['_limit'] = limit
        p['_offset'] = off
        query_str = '&'.join([f"{k}={v}" for k, v in p.items() if v is not None])
        return f"{base_url}?{query_str}"

    first = build_url(0)
    last_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0
    last = build_url(last_offset)

    prev_url = build_url(offset - limit) if offset - limit >= 0 else None
    next_url = build_url(offset + limit) if offset + limit < total else None

    links = {
        "_first": first,
        "_prev": prev_url,
        "_next": next_url,
        "_last": last
    }
    return links

@reservas_bp.route('/reservas', methods=['GET'])
def obtener_reservas():
    try:
        limit = int(request.args.get('_limit', LIMITE_PAGINACION_DEFECTO))
        offset = int(request.args.get('_offset', OFFSET_PAGINACION_DEFECTO))
        
        if limit < LIMIT_MINIMO or limit > LIMIT_MAXIMO or offset < 0:
            respuesta_http = (jsonify({"error": "_limit debe estar entre 1 y 100, y _offset >= 0"}), 400)
        else:
            id_cancha = request.args.get('id_cancha')
            id_socio = request.args.get('id_socio')
            estado = request.args.get('estado')
            fecha_desde = request.args.get('fecha_desde')
            fecha_hasta = request.args.get('fecha_hasta')

            if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
                respuesta_http = (jsonify({"error": "fecha_desde no puede ser mayor que fecha_hasta"}), 400)
            else:
                reservas_db, total = listar_reservas(
                    id_cancha=id_cancha,
                    id_socio=id_socio,
                    estado=estado,
                    fecha_desde=fecha_desde,
                    fecha_hasta=fecha_hasta,
                    limit=limit,
                    offset=offset
                )

                reservas_formatted = [formatear_respuesta_reserva(r) for r in reservas_db]

                params_extra = {
                    'id_cancha': id_cancha,
                    'id_socio': id_socio,
                    'estado': estado,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                }
                links = generar_hateoas_links(limit, offset, total, params_extra)

                respuesta_http = (jsonify({
                    "reservas": reservas_formatted,
                    "_links": links
                }), 200)

    except ValueError:
        respuesta_http = (jsonify({"error": "_limit y _offset deben ser números enteros"}), 400)
    except Exception as e:
        respuesta_http = (jsonify({"error": str(e)}), 500)

    return respuesta_http

@reservas_bp.route('/reservas', methods=['POST'])
def crear_reserva():
    data = request.get_json()

    if not data:
        respuesta_http = (jsonify({"error": "El cuerpo de la solicitud no puede estar vacío"}), 400)
    elif not set(data.keys()).issubset(CAMPOS_REQUERIDOS_CREACION):
        respuesta_http = (jsonify({"error": "Se enviaron campos no permitidos"}), 400)
    else:
        respuesta, status_code = crear_reserva_service(data)
        respuesta_http = (jsonify(respuesta), status_code)

    return respuesta_http

@reservas_bp.route('/reservas/<int:id_reserva>', methods=['GET'])
def obtener_reserva(id_reserva):
    reserva = obtener_reserva_por_id(id_reserva)
    
    if not reserva:
        respuesta_http = (jsonify({"error": "Reserva no encontrada"}), 404)
    else:
        respuesta = formatear_respuesta_reserva(reserva)
        respuesta_http = (jsonify(respuesta), 200)

    return respuesta_http

@reservas_bp.route('/reservas/<int:id_reserva>/estado', methods=['PUT'])
def actualizar_estado_reserva(id_reserva):
    data = request.get_json()

    if not data or 'estado' not in data:
        respuesta_http = (jsonify({"error": "Debe especificar el campo 'estado'"}), 400)
    elif set(data.keys()) != CAMPOS_PERMITIDOS_ESTADO:
        respuesta_http = (jsonify({"error": "Cuerpo con campos desconocidos o inválidos"}), 400)
    else:
        respuesta, status_code = cambiar_estado_service(id_reserva, data['estado'])
        respuesta_http = (jsonify(respuesta), status_code)

    return respuesta_http
