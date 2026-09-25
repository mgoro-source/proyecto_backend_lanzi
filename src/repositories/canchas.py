import db
from src.exceptions import NotFoundError, ConflictError


def _construir_filtros(filtros: dict):
    condiciones, params = [], {}
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


def obtener_todas(filtros, limit, offset):
    where, params = _construir_filtros(filtros)
    total_sql = f"SELECT COUNT(*) AS total FROM canchas {where}"
    total = db.ejecutar_consulta(total_sql, params)[0]["total"]

    sql = f"""
        SELECT id_cancha, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas
        {where}
        ORDER BY id_cancha ASC
        LIMIT :limit OFFSET :offset
    """
    filas = db.ejecutar_consulta(sql, {**params, "limit": limit, "offset": offset})
    return [_normalizar(f) for f in filas], total


def obtener_por_id(id_cancha: int):
    sql = """
        SELECT id_cancha, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas WHERE id_cancha = :id
    """
    filas = db.ejecutar_consulta(sql, {"id": id_cancha})
    if not filas:
        raise NotFoundError("Cancha no encontrada", f"No existe cancha con id {id_cancha}")
    return _normalizar(filas[0])


def crear(data: dict) -> int:
    sql = """
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa)
    """
    return db.ejecutar_mutacion(sql, {
        "nombre": data["nombre"],
        "id_deporte": data["id_deporte"],
        "precio_hora": data["precio_hora"],
        "techada": int(data.get("techada", False)),
        "activa": int(data.get("activa", True)),
    })


def actualizar(id_cancha: int, data: dict):
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
    sql = f"UPDATE canchas SET {', '.join(set_clauses)} WHERE id_cancha = :id"
    db.ejecutar_mutacion(sql, params)


def eliminar(id_cancha: int):
    total = db.ejecutar_consulta(
        "SELECT COUNT(*) AS total FROM reservas WHERE id_cancha = :id",
        {"id": id_cancha}
    )[0]["total"]
    if total > 0:
        raise ConflictError(
            "No se puede eliminar la cancha",
            "La cancha tiene reservas asociadas; puede desactivarla con PATCH"
        )
    db.ejecutar_mutacion("DELETE FROM canchas WHERE id_cancha = :id", {"id": id_cancha})


def obtener_disponibles(fecha, hora_inicio, hora_fin, filtros):
    """Canchas activas sin reserva confirmada superpuesta (y sin bloqueo si existe)."""
    condiciones = ["c.activa = 1"]
    params = {"inicio": f"{fecha} {hora_inicio}", "fin": f"{fecha} {hora_fin}"}

    if filtros.get("id_deporte") is not None:
        condiciones.append("c.id_deporte = :id_deporte")
        params["id_deporte"] = filtros["id_deporte"]
    if filtros.get("techada") is not None:
        condiciones.append("c.techada = :techada")
        params["techada"] = int(filtros["techada"])

    sql = f"""
        SELECT c.id_cancha, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c
        WHERE {' AND '.join(condiciones)}
          AND NOT EXISTS (
              SELECT 1 FROM reservas r
              WHERE r.id_cancha = c.id_cancha
                AND r.estado = 'confirmada'
                AND r.fecha_hora_inicio < :fin
                AND r.fecha_hora_fin > :inicio
          )
        ORDER BY c.id_cancha ASC
    """
    return [_normalizar(f) for f in db.ejecutar_consulta(sql, params)]


def _normalizar(fila):
    fila["techada"] = bool(fila["techada"])
    fila["activa"] = bool(fila["activa"])
    return fila