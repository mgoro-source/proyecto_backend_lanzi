from flask import abort
from src.repositories.socios import (obtener_socio_por_email,
                                        insertar_socio, obtener_socio_por_id,
                                        obtener_todos_los_socios,
                                        contar_socios,
                                        actualizar_socio)
from src.validators.socios import validar_creacion_socio, validar_actualizacion_socio
from src.constantes import (ERROR_CODE_EMAIL_DUPLICATE,
                            ERROR_CODE_SOCIO_NOT_FOUND,
                            ERROR_CODE_UNKNOWN_PARAMETER,
                            ERROR_CODE_ACTIVE_FILTER_INVALID,
                            ERROR_CODE_PAGINATION_TYPE_INVALID,
                            ERROR_CODE_INVALID_LIMIT,
                            ERROR_CODE_INVALID_OFFSET)

def crear_socio_service(datos: dict) -> dict:

    error_validacion = validar_creacion_socio(datos)
    
    if error_validacion:
        abort(400, description = str(error_validacion))

    email = datos["email"].strip().lower()
    
    if obtener_socio_por_email(email):
        abort(409, description = ERROR_CODE_EMAIL_DUPLICATE)

    nombre = datos["nombre"].strip()
    activo = datos.get("activo", True)
    nuevo_id = insertar_socio(nombre_socio=nombre, email_socio=email, activo=activo)

    return obtener_socio_por_id(nuevo_id)

def obtener_socio_por_id_service(id_socio: int) -> dict:
   
    socio = obtener_socio_por_id(id_socio)
    
    if not socio:
        abort(404, description = ERROR_CODE_SOCIO_NOT_FOUND)
        
    return socio

def listar_socios_service(parametros: dict) -> dict:
    
    parametros_validos = {"_limit", "_offset", "nombre", "activo"}
    for param in parametros.keys():
        if param not in parametros_validos:
            abort(400, description = f"{ERROR_CODE_UNKNOWN_PARAMETER}: {param}")

    nombre = parametros.get("nombre", "").strip()
    activo_recibido = parametros.get("activo")
    activo = None
    
    if activo_recibido is not None:
        if activo_recibido.lower() == "true":
            activo = True
        elif activo_recibido.lower() == "false":
            activo = False
        else:
            abort(400, description = ERROR_CODE_ACTIVE_FILTER_INVALID)

    try:
        _limit = int(parametros.get("_limit", 10))
        _offset = int(parametros.get("_offset", 0))
    except ValueError:
        abort(400, description = ERROR_CODE_PAGINATION_TYPE_INVALID)

    if not (1 <= _limit <= 100):
        abort(400, description = ERROR_CODE_INVALID_LIMIT)
    if _offset < 0:
        abort(400, description = ERROR_CODE_INVALID_OFFSET)

    socios = obtener_todos_los_socios(nombre=nombre if nombre else None,
                                      activo=activo,
                                      limite=_limit,
                                      offset=_offset)
    total_registros = contar_socios(nombre=nombre if nombre else None, activo=activo)

    base_url = "/socios"
    _first = f"{base_url}?_limit={_limit}&_offset=0"
    ultimo_offset = max(0, total_registros - _limit)
    _last = f"{base_url}?_limit={_limit}&_offset={ultimo_offset}"
    _prev = None
    
    if _offset > 0:
        prev_offset = max(0, _offset - _limit)
        _prev = f"{base_url}?_limit={_limit}&_offset={prev_offset}"

    _next = None
    
    if _offset + _limit < total_registros:
        next_offset = _offset + _limit
        _next = f"{base_url}?_limit={_limit}&_offset={next_offset}"

    return {"socios": socios, "_limit": _limit, "_offset": _offset, "_links": {"_first": _first,
                                                                               "_prev": _prev,
                                                                               "_next": _next,
                                                                               "_last": _last}}

def actualizar_socio_service(id_socio: int, datos: dict) -> dict:
    
    socio_actual = obtener_socio_por_id(id_socio)
    
    if not socio_actual:
        abort(404, description = ERROR_CODE_SOCIO_NOT_FOUND)

    error_validacion = validar_actualizacion_socio(datos)
    
    if error_validacion:
        abort(400, description = str(error_validacion))

    nuevo_nombre = datos.get("nombre", socio_actual["nombre_socio"])
    nuevo_activo = datos.get("activo", socio_actual["activo"])
    
    if "email" in datos:
        nuevo_email = datos["email"].strip().lower()
        socio_con_mismo_email = obtener_socio_por_email(nuevo_email)
        if socio_con_mismo_email and socio_con_mismo_email["id_socio"] != id_socio:
            abort(409, description = ERROR_CODE_EMAIL_DUPLICATE)
    else:
        nuevo_email = socio_actual["email_socio"].strip().lower()
    
    actualizar_socio(id_socio=id_socio,
                     nombre_socio=nuevo_nombre,
                     email_socio=nuevo_email,
                     activo=nuevo_activo)

    return obtener_socio_por_id(id_socio)