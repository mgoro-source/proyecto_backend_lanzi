from src.db import ejecutar_consulta, ejecutar_mutacion
from src.exceptions import NotFoundError, ConflictError


def _construir_filtros(filtros: dict):
    condiciones = []
    params = {}
    if filtros.get("id_deporte") is not None:
        condiciones.append("id_deporte = :id_deporte")
        params["id_deporte"] = filtros["id_deporte"]
    if filtros.get("nombre"):
        condiciones.append("LOWER(nombre) LIKE :nombre")
        params["nombre"] = f"%{filtros['nombre'].lower()}%"
    if filtros.get("techada") is not None:
        condiciones.append("techada = :techada")
        params["techada"] = int(filtros["techada"])
    if filtros.get("activa") is not None:
        condiciones.append("activa = :activa")
        params["activa"] = int(filtros["activa"])
    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where, params


def get_all(filtros, limit, offset):
    where, params = _construir_filtros(filtros)
    sql_total = f"SELECT COUNT(*) AS total FROM cancha {where}"
    total = ejecutar_consulta(sql_total, params)[0]["total"]

    sql = f"""
        SELECT id, nombre, id_deporte, precio_hora, techada, activa
        FROM cancha
        {where}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset
    """
    params_pag = {**params, "limit": limit, "offset": offset}
    filas = ejecutar_consulta(sql, params_pag)
    return [_normalizar(f) for f in filas], total


def get_by_id(id_cancha: int):
    sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM cancha WHERE id = :id"
    filas = ejecutar_consulta(sql, {"id": id_cancha})
    if not filas:
        raise NotFoundError("Cancha no encontrada", f"No existe cancha con id {id_cancha}")
    return _normalizar(filas[0])


def create(data: dict) -> int:
    sql = """
        INSERT INTO cancha (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa)
    """
    return ejecutar_mutacion(sql, {
        "nombre": data["nombre"],
        "id_deporte": data["id_deporte"],
        "precio_hora": data["precio_hora"],
        "techada": int(data.get("techada", False)),
        "activa": int(data.get("activa", True)),
    })


def update(id_cancha: int, data: dict):
    set_clauses, params = [], {"id": id_cancha}
    for campo in ("nombre", "precio_hora", "techada", "activa"):
        if campo in data:
            valor = data[campo]
            if campo in ("techada", "activa"):
                valor = int(valor)
            set_clauses.append(f"{campo} = :{campo}")
            params[campo] = valor
    if not set_clauses:
        return
    sql = f"UPDATE cancha SET {', '.join(set_clauses)} WHERE id = :id"
    ejecutar_mutacion(sql, params)


def delete(id_cancha: int):
    sql = "SELECT COUNT(*) AS total FROM reserva WHERE id_cancha = :id"
    total = ejecutar_consulta(sql, {"id": id_cancha})[0]["total"]
    if total > 0:
        raise ConflictError(
            "No se puede eliminar la cancha",
            "La cancha tiene reservas asociadas; puede desactivarla con PATCH"
        )
    ejecutar_mutacion("DELETE FROM cancha WHERE id = :id", {"id": id_cancha})


def get_disponibles(fecha, hora_inicio, hora_fin, filtros):
    """
    Canchas activas que NO tienen reserva confirmada superpuesta
    ni bloqueo superpuesto (si la tabla bloqueo existe).
    """
    inicio_dt = f"{fecha} {hora_inicio}"
    fin_dt = f"{fecha} {hora_fin}"

    condiciones = ["c.activa = 1"]
    params = {"inicio": inicio_dt, "fin": fin_dt}

    if filtros.get("id_deporte") is not None:
        condiciones.append("c.id_deporte = :id_deporte")
        params["id_deporte"] = filtros["id_deporte"]
    if filtros.get("techada") is not None:
        condiciones.append("c.techada = :techada")
        params["techada"] = int(filtros["techada"])

    sql = f"""
        SELECT c.id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM cancha c
        WHERE {' AND '.join(condiciones)}
          AND NOT EXISTS (
              SELECT 1 FROM reserva r
              WHERE r.id_cancha = c.id
                AND r.estado = 'confirmada'
                AND r.fecha_hora_inicio < :fin
                AND r.fecha_hora_fin > :inicio
          )
        ORDER BY c.id ASC
    """
    return [_normalizar(f) for f in ejecutar_consulta(sql, params)]


def _normalizar(fila):
    fila["techada"] = bool(fila["techada"])
    fila["activa"] = bool(fila["activa"])
    return fila