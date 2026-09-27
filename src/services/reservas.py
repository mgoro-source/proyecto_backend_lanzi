
from datetime import datetime
from flask import abort, request

from src.repositories import reservas_repositorio as repo
from src import constantes as C

CAMPOS_CREATE = {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"}
CAMPOS_ESTADO = {"estado"}


def _mapear_a_schema(reserva: dict) -> dict:
    return {
        "id": reserva["id_reserva"],
        "id_socio": reserva["id_socio_reserva"],
        "id_cancha": reserva["id_cancha_reserva"],
        "fecha_hora_inicio": reserva["fecha_iso_inicio"],
        "fecha_hora_fin": reserva["fecha_iso_fin"],
        "estado": reserva["estado_actual"],
        "precio_hora": reserva["precio_hora"],
        "importe_total": reserva["importe_total"],
    }


def _parsear_fecha_hora(valor, campo):
    if not isinstance(valor, str):
        abort(400, description=f"'{campo}' debe ser un string en formato ISO 8601 con offset -03:00")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M:%S.%f-03:00")
    except ValueError:
        abort(400, description=f"'{campo}' debe cumplir el formato YYYY-MM-DDTHH:MM:SS.ffffff-03:00")


def _validar_intervalo(inicio: datetime, fin: datetime):
    if inicio >= fin:
        abort(400, description="fecha_hora_inicio debe ser anterior a fecha_hora_fin")
    if inicio.minute != 0 or inicio.second != 0 or inicio.microsecond != 0:
        abort(400, description="fecha_hora_inicio debe estar en hora en punto")
    if fin.minute != 0 or fin.second != 0 or fin.microsecond != 0:
        abort(400, description="fecha_hora_fin debe estar en hora en punto")

    duracion = (fin - inicio).total_seconds() / 3600
    if duracion < C.DURACION_MIN_HORAS or duracion > C.DURACION_MAX_HORAS:
        abort(400, description="La reserva debe durar entre 1 y 3 horas completas")

    if inicio.date() != fin.date():
        abort(400, description="La reserva no puede atravesar la medianoche")

    if inicio.hour < C.HORA_APERTURA or fin.hour > C.HORA_CIERRE:
        abort(400, description=f"El club atiende de {C.HORA_APERTURA}:00 a {C.HORA_CIERRE}:00")

    if inicio <= datetime.now():
        abort(400, description="El inicio de la reserva debe ser posterior al momento actual")


def _validar_id_entero(valor, campo):
    if not isinstance(valor, int) or isinstance(valor, bool):
        abort(400, description=f"'{campo}' debe ser un entero")
    return valor


def crear_reserva_service(data: dict) -> dict:
    if not isinstance(data, dict) or not data:
        abort(400, description="El cuerpo no puede estar vacío")

    desconocidos = set(data.keys()) - CAMPOS_CREATE
    if desconocidos:
        abort(400, description=f"Campos no permitidos: {', '.join(sorted(desconocidos))}")

    faltantes = CAMPOS_CREATE - set(data.keys())
    if faltantes:
        abort(400, description=f"Campos requeridos: {', '.join(sorted(faltantes))}")

    id_socio = _validar_id_entero(data["id_socio"], "id_socio")
    id_cancha = _validar_id_entero(data["id_cancha"], "id_cancha")

    inicio_dt = _parsear_fecha_hora(data["fecha_hora_inicio"], "fecha_hora_inicio")
    fin_dt = _parsear_fecha_hora(data["fecha_hora_fin"], "fecha_hora_fin")
    _validar_intervalo(inicio_dt, fin_dt)

    socio = repo.obtengo_socio(id_socio)
    if not socio:
        abort(404, description=f"No existe socio con id {id_socio}")
    if not socio["activo"]:
        abort(400, description="No se pueden crear reservas para un socio inactivo")

    cancha = repo.obtengo_cancha(id_cancha)
    if not cancha:
        abort(404, description=f"No existe cancha con id {id_cancha}")
    if not cancha["activa"]:
        abort(400, description="No se pueden crear reservas para una cancha inactiva")

    inicio_sql = inicio_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    fin_sql = fin_dt.strftime("%Y-%m-%d %H:%M:%S.%f")

    if repo.pregunto_superposicion(id_cancha, id_socio, inicio_sql, fin_sql):
        abort(409, description="Existe una reserva confirmada que se superpone con el intervalo solicitado")

    precio_hora = cancha["precio_hora"]
    nueva_reserva = repo.crear_reserva(id_socio, id_cancha, inicio_sql, fin_sql, precio_hora)
    return _mapear_a_schema(nueva_reserva)


def obtener_reserva_service(id_reserva: int) -> dict:
    reserva = repo.obtener_reserva_por_id(id_reserva)
    if not reserva:
        abort(404, description=f"No existe reserva con id {id_reserva}")
    return _mapear_a_schema(reserva)


def cambiar_estado_service(id_reserva: int, data: dict) -> dict:
    if not isinstance(data, dict):
        abort(400, description="El cuerpo debe ser un objeto JSON")

    desconocidos = set(data.keys()) - CAMPOS_ESTADO
    if desconocidos:
        abort(400, description=f"Campos no permitidos: {', '.join(sorted(desconocidos))}")

    if "estado" not in data:
        abort(400, description="Falta el campo 'estado'")

    nuevo_estado = data["estado"]
    if nuevo_estado not in C.ESTADOS_VALIDOS:
        abort(400, description=f"'estado' debe ser uno de: {', '.join(sorted(C.ESTADOS_VALIDOS))}")

    reserva = repo.obtener_reserva_por_id(id_reserva)
    if not reserva:
        abort(404, description=f"No existe reserva con id {id_reserva}")

    estado_actual = reserva["estado_actual"]

    if nuevo_estado == estado_actual:
        return _mapear_a_schema(reserva)

    if estado_actual in (C.ESTADO_CANCELADA, C.ESTADO_FINALIZADA):
        abort(409, description=f"Una reserva '{estado_actual}' no puede cambiar de estado")

    ahora = datetime.now()
    inicio_dt = datetime.strptime(str(reserva["fecha_reserva_inicio"]), "%Y-%m-%d %H:%M:%S")
    fin_dt = datetime.strptime(str(reserva["fecha_reserva_fin"]), "%Y-%m-%d %H:%M:%S")

    if nuevo_estado == C.ESTADO_CANCELADA:
        if ahora >= inicio_dt:
            abort(409, description="Solo se puede cancelar una reserva antes de que comience su horario")
        condicion = C.CONDICION_CANCELACION

    elif nuevo_estado == C.ESTADO_FINALIZADA:
        if ahora < fin_dt:
            abort(409, description="Solo se puede finalizar una reserva cuando ya se alcanzó su horario de fin")
        condicion = C.CONDICION_FINALIZACION

    else:
        abort(409, description=f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}'")

    reserva_actualizada = repo.actualizar_estado(id_reserva, nuevo_estado, nuevo_estado, condicion)
    return _mapear_a_schema(reserva_actualizada)


def listar_reservas_service(parametros: dict) -> dict:
    parametros_validos = {"_limit", "_offset", "id_cancha", "id_socio", "estado", "fecha_desde", "fecha_hasta"}
    for param in parametros.keys():
        if param not in parametros_validos:
            abort(400, description=f"Parámetro desconocido: {param}")

    try:
        _limit = int(parametros.get("_limit", C.LIMIT_DEFAULT))
        _offset = int(parametros.get("_offset", C.OFFSET_DEFAULT))
    except ValueError:
        abort(400, description="'_limit' y '_offset' deben ser enteros")

    if not (C.LIMIT_MIN <= _limit <= C.LIMIT_MAX):
        abort(400, description="'_limit' debe estar entre 1 y 100")
    if _offset < 0:
        abort(400, description="'_offset' debe ser >= 0")

    id_cancha = parametros.get("id_cancha")
    id_socio = parametros.get("id_socio")
    estado = parametros.get("estado")
    fecha_desde = parametros.get("fecha_desde")
    fecha_hasta = parametros.get("fecha_hasta")

    if id_cancha is not None:
        try:
            id_cancha = int(id_cancha)
        except ValueError:
            abort(400, description="'id_cancha' debe ser un entero")

    if id_socio is not None:
        try:
            id_socio = int(id_socio)
        except ValueError:
            abort(400, description="'id_socio' debe ser un entero")

    if estado is not None and estado not in C.ESTADOS_VALIDOS:
        abort(400, description=f"'estado' debe ser uno de: {', '.join(sorted(C.ESTADOS_VALIDOS))}")

    for nombre_campo, valor in (("fecha_desde", fecha_desde), ("fecha_hasta", fecha_hasta)):
        if valor is not None:
            try:
                datetime.strptime(valor, "%Y-%m-%d")
            except ValueError:
                abort(400, description=f"'{nombre_campo}' debe tener formato YYYY-MM-DD")

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        abort(400, description="'fecha_desde' debe ser menor o igual a 'fecha_hasta'")

    filas, total = repo.listar_reservas(
        id_cancha=id_cancha,
        id_socio=id_socio,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=_limit,
        offset=_offset,
    )
    reservas = [_mapear_a_schema(r) for r in filas]

    base_url = f"{request.host_url.rstrip('/')}/reservas"
    query_filtros = ""
    if id_cancha is not None:
        query_filtros += f"&id_cancha={id_cancha}"
    if id_socio is not None:
        query_filtros += f"&id_socio={id_socio}"
    if estado:
        query_filtros += f"&estado={estado}"
    if fecha_desde:
        query_filtros += f"&fecha_desde={fecha_desde}"
    if fecha_hasta:
        query_filtros += f"&fecha_hasta={fecha_hasta}"

    _first = f"{base_url}?_limit={_limit}&_offset=0{query_filtros}"
    ultimo_offset = max(0, total - _limit)
    _last = f"{base_url}?_limit={_limit}&_offset={ultimo_offset}{query_filtros}"

    _prev = None
    if _offset > 0:
        prev_offset = max(0, _offset - _limit)
        _prev = f"{base_url}?_limit={_limit}&_offset={prev_offset}{query_filtros}"

    _next = None
    if _offset + _limit < total:
        next_offset = _offset + _limit
        _next = f"{base_url}?_limit={_limit}&_offset={next_offset}{query_filtros}"

    return {
        "reservas": reservas,
        "_limit": _limit,
        "_offset": _offset,
        "_links": {"_first": _first, "_prev": _prev, "_next": _next, "_last": _last},
    }
