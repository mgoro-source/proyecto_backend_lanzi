import re
from datetime import datetime, time
from ..constantes import (
    HORA_APERTURA,
    HORA_CIERRE,
    DURACION_MIN_HORAS,
    DURACION_MAX_HORAS,
    LIMIT_DEFAULT,
    LIMIT_MIN,
    LIMIT_MAX,
    OFFSET_DEFAULT,
    ERROR_CODE_UNKNOWN_FIELD,
    ERROR_CODE_UNKNOWN_PARAMETER,
    ERROR_CODE_NAME_REQUIRED,
    ERROR_CODE_NAME_INVALID,
    ERROR_CODE_PRICE_INVALID,
    ERROR_CODE_SPORT_INVALID,
    ERROR_CODE_INVALID_LIMIT,
    ERROR_CODE_INVALID_OFFSET
)


def _parsear_booleano(valor, nombre_campo):
    if isinstance(valor, bool):
        return valor, None
    if isinstance(valor, str):
        valor_clean = valor.strip().lower()
        if valor_clean == 'true':
            return True, None
        if valor_clean == 'false':
            return False, None
    
    return None, f"El campo '{nombre_campo}' debe ser un valor booleano (true o false)."


def validar_id_cancha(id_cancha):
    try:
        id_num = int(id_cancha)
        if id_num <= 0:
            raise ValueError()
        return id_num, None
    except (ValueError, TypeError):
        return None, "El ID de la cancha debe ser un número entero estrictamente mayor a cero."

    
def validar_crear_cancha(body):
    if not isinstance(body, dict):
        return None, "El cuerpo de la solicitud debe ser un objeto JSON."
    
    campos_permitidos = {'nombre', 'id_deporte', 'precio_hora', 'techada', 'activa'}
    campos_desconocidos = set(body.keys()) - campos_permitidos
    if campos_desconocidos:
        return None, (ERROR_CODE_UNKNOWN_FIELD, f"Campos no permitidos: {', '.join(campos_desconocidos)}.")
    
    campos_requeridos = ['nombre', 'id_deporte', 'precio_hora']
    faltantes = [campo for campo in campos_requeridos if campo not in body]
    if faltantes:
        return None, (ERROR_CODE_NAME_REQUIRED, f"Los siguientes campos son requeridos: {', '.join(faltantes)}.")
    
    nombre = body.get('nombre')
    if not isinstance(nombre, str) or not nombre.strip():
        return None, (ERROR_CODE_NAME_INVALID, "El campo 'nombre' no puede estar vacío.")
    
    id_deporte = body.get('id_deporte')
    if isinstance(id_deporte, bool) or not isinstance(id_deporte, int) or id_deporte <= 0:
        return None, (ERROR_CODE_SPORT_INVALID, "El campo 'id_deporte' debe ser un número entero mayor a cero.")
    
    precio_hora = body.get('precio_hora')
    if isinstance(precio_hora, bool) or not isinstance(precio_hora, int) or precio_hora <= 0:
        return None, (ERROR_CODE_PRICE_INVALID, "El campo 'precio_hora' debe ser un entero mayor a cero en centavos.")
    
    techada, err_t = _parsear_booleano(body.get('techada', False), 'techada')
    if err_t:
        return None, err_t
    
    activa, err_a = _parsear_booleano(body.get('activa', True), 'activa')
    if err_a:
        return None, err_a
    
    return {
        "nombre": nombre.strip(),
        "id_deporte": id_deporte,
        "precio_hora": precio_hora,
        "techada": techada,
        "activa": activa
    }, None


def validar_actualizar_cancha(body):
    if not isinstance(body, dict) or not body:
        return None, "Debe proporcionar un objeto JSON con al menos un campo a actualizar."
    
    if 'id_deporte' in body:
        return None, "El deporte asociado a una cancha no se puede modificar una vez creada."
    
    campos_permitidos = {'nombre', 'precio_hora', 'techada', 'activa'}
    campos_desconocidos = set(body.keys()) - campos_permitidos
    if campos_desconocidos:
        return None, (ERROR_CODE_UNKNOWN_FIELD, f"Campos no permitidos: {', '.join(campos_desconocidos)}.")
    
    datos_actualizados = {}

    if 'nombre' in body:
        nombre = body['nombre']
        if not isinstance(nombre, str) or not nombre.strip():
            return None, (ERROR_CODE_NAME_INVALID, "El campo 'nombre' no puede estar vacío.")
        datos_actualizados['nombre'] = nombre.strip()

    if 'precio_hora' in body:
        precio_hora = body['precio_hora']
        if isinstance(precio_hora, bool) or not isinstance(precio_hora, int) or precio_hora <= 0:
            return None, (ERROR_CODE_PRICE_INVALID, "El campo 'precio_hora' debe ser un entero mayor a cero en centavos.")
        datos_actualizados['precio_hora'] = precio_hora

    if 'techada' in body:
        techada, err_t = _parsear_booleano(body['techada'], 'techada')
        if err_t:
            return None, err_t
        datos_actualizados['techada'] = techada

    if 'activa' in body:
        activa, err_a = _parsear_booleano(body['activa'], 'activa')
        if err_a:
            return None, err_a
        datos_actualizados['activa'] = activa

    return datos_actualizados, None


def validar_filtros_canchas(args):
    campos_permitidos = {'_limit', '_offset', 'id_deporte', 'nombre', 'techada', 'activa'}
    campos_desconocidos = set(args.keys()) - campos_permitidos
    if campos_desconocidos:
        return None, (ERROR_CODE_UNKNOWN_PARAMETER, f"Parámetros no permitidos en la URL: {', '.join(campos_desconocidos)}.")
    
    limit_str = args.get('_limit', str(LIMIT_DEFAULT))
    try:
        limit = int(limit_str)
        if limit < LIMIT_MIN or limit > LIMIT_MAX:
            raise ValueError()
    except ValueError:
        return None, (ERROR_CODE_INVALID_LIMIT, "El parámetro '_limit' debe ser un entero entre 1 y 100.")
    
    offset_str = args.get('_offset', str(OFFSET_DEFAULT))
    try:
        offset = int(offset_str)
        if offset < 0:
            raise ValueError()
    except ValueError:
        return None, (ERROR_CODE_INVALID_OFFSET, "El parámetro '_offset' debe ser un entero mayor o igual a cero.")
    
    filtros = {
        "_limit": limit,
        "_offset": offset,
        "id_deporte": None,
        "nombre": None,
        "techada": None,
        "activa": None
    }

    if 'id_deporte' in args and str(args['id_deporte']).strip():
        try:
            id_dep = int(args['id_deporte'])
            if id_dep <= 0:
                raise ValueError()
            filtros['id_deporte'] = id_dep
        except ValueError:
            return None, (ERROR_CODE_SPORT_INVALID, "El parámetro 'id_deporte' debe ser un entero positivo.")
        
    if 'nombre' in args and str(args['nombre']).strip():
        filtros['nombre'] = args['nombre'].strip()

    if 'techada' in args and str(args['techada']).strip():
        techada, err_t = _parsear_booleano(args['techada'], 'techada')
        if err_t:
            return None, err_t
        filtros['techada'] = techada

    if 'activa' in args and str(args['activa']).strip():
        activa, err_a = _parsear_booleano(args['activa'], 'activa')
        if err_a:
            return None, err_a
        filtros['activa'] = activa

    return filtros, None


def validar_consulta_disponibilidad(args):
    campos_permitidos = {'fecha', 'hora_inicio', 'hora_fin', 'id_deporte', 'techada', '_limit', '_offset'}
    campos_desconocidos = set(args.keys()) - campos_permitidos
    if campos_desconocidos:
        return None, (ERROR_CODE_UNKNOWN_PARAMETER, f"Parámetros no reconocidos: {', '.join(campos_desconocidos)}.")
    
    requeridos = ['fecha', 'hora_inicio', 'hora_fin']
    faltantes = [p for p in requeridos if p not in args or not str(args[p]).strip()]
    if faltantes:
        return None, f"Debe especificar los parámetros obligatorios: {', '.join(faltantes)}."
    
    fecha_str = str(args['fecha']).strip()
    try:
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return None, "El parámetro 'fecha' debe cumplir el formato ISO 8601 (YYYY-MM-DD)."
    
    patron_hora = re.compile(r'^(?:[01]?\d|2[0-3]):00:00$')

    hora_inicio_str = str(args['hora_inicio']).strip()
    if not patron_hora.match(hora_inicio_str):
        return None, "La 'hora_inicio' debe ser una hora en punto en formato HH:00:00 (ej: 18:00:00)."
    
    hora_fin_str = str(args['hora_fin']).strip()
    if not patron_hora.match(hora_fin_str):
        return None, "La 'hora_fin' debe ser una hora en punto en formato HH:00:00 (ej: 20:00:00)."
    
    h_inicio = int(hora_inicio_str.split(':')[0])
    h_fin = int(hora_fin_str.split(':')[0])

    if h_inicio < HORA_APERTURA or h_inicio >= HORA_CIERRE:
        return None, f"El horario de inicio debe estar dentro de la franja operativa del club ({HORA_APERTURA:02d}:00 a {HORA_CIERRE:02d}:00).."
    
    if h_fin <= HORA_APERTURA or h_fin > HORA_CIERRE:
        return None, f"El horario de fin debe mantenerse dentro del horario de cierre del club ({HORA_CIERRE:02d}:00)."
    
    duracion = h_fin - h_inicio
    if duracion <= 0:
        return None, "La 'hora_inicio' debe ser estrictamente menor que la 'hora_fin'."
    
    if duracion < DURACION_MIN_HORAS or duracion > DURACION_MAX_HORAS:
        return None, f"La reserva debe durar entre {DURACION_MIN_HORAS} y {DURACION_MAX_HORAS} horas completas."
    
    limit_str = args.get('_limit', str(LIMIT_DEFAULT))
    try:
        limit = int(limit_str)
        if limit < LIMIT_MIN or limit > LIMIT_MAX:
            raise ValueError()
    except ValueError:
        return None, (ERROR_CODE_INVALID_LIMIT, f"El parámetro '_limit' debe ser un entero entre {LIMIT_MIN} y {LIMIT_MAX}.")
    
    offset_str = args.get('_offset', str(OFFSET_DEFAULT))
    try:
        offset = int(offset_str)
        if offset < 0:
            raise ValueError()
    except ValueError:
        return None, (ERROR_CODE_INVALID_OFFSET, "El parámetro '_offset' debe ser un entero mayor o igual a cero.")
    
    id_deporte = None
    if 'id_deporte' in args and str(args['id_deporte']).strip():
        try:
            id_dep = int(args['id_deporte'])
            if id_dep <= 0:
                raise ValueError()
            id_deporte = id_dep
        except ValueError:
            return None, (ERROR_CODE_SPORT_INVALID, "El parámetro 'id_deporte' debe ser un entero positivo.")
        
    techada = None
    if 'techada' in args and str(args['techada']).strip():
        techada, err_techada = _parsear_booleano(args['techada'], 'techada')
        if err_techada:
            return None, err_techada
        
    datos = {
        "fecha": fecha_dt,
        "hora_inicio": time(h_inicio, 0, 0),
        "hora_fin": time(h_fin, 0, 0),
        "id_deporte": id_deporte,
        "techada": techada,
        "_limit": limit,
        "_offset": offset
    }
    
    return datos, None