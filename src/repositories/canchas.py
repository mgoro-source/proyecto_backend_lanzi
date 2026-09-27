from ..db import ejecutar_consulta, ejecutar_mutacion


def obtener_todas(filtros):
    try:
        sql = """
            SELECT
                c.id_cancha AS id,
                c.nombre_cancha AS nombre,
                c.id_deporte_cancha AS id_deporte,
                c.precio_hora,
                c.techada,
                c.activa
            FROM canchas c
            WHERE 1=1
        """

        params = {}

        if filtros.get('id_deporte') is not None:
            sql += " AND c.id_deporte_cancha = :id_deporte"
            params['id_deporte'] = filtros['id_deporte']

        if filtros.get('nombre'):
            sql += " AND LOWER(c.nombre_cancha) LIKE LOWER(:nombre)"
            params['nombre'] = f"%{filtros['nombre']}%"

        if filtros.get('techada') is not None:
            sql += " AND c.techada = :techada"
            params['techada'] = 1 if filtros['techada'] else 0

        if filtros.get('activa') is not None:
            sql += " AND c.activa = :activa"
            params['activa'] = 1 if filtros['activa'] else 0

        sql += " ORDER BY c.id_cancha ASC LIMIT :limit OFFSET :offset"
        params['limit'] = filtros.get('_limit', 10)
        params['offset'] = filtros.get('_offset', 0)

        filas = ejecutar_consulta(sql, params)

        for c in filas:
            c['techada'] = bool(c['techada'])
            c['activa'] = bool(c['activa'])

        return filas, None
    
    except Exception as e:
        return None, f"Error SQL al obtener canchas: {str(e)}"

    
def contar_todas(filtros):
    try:
        sql = "SELECT COUNT(*) AS total FROM canchas c WHERE 1=1"
        params = {}

        if filtros.get('id_deporte') is not None:
            sql += " AND c.id_deporte_cancha = :id_deporte"
            params['id_deporte'] = filtros['id_deporte']

        if filtros.get('nombre'):
            sql += " AND LOWER(c.nombre_cancha) LIKE LOWER(:nombre)"
            params['nombre'] = f"%{filtros['nombre']}%"

        if filtros.get('techada') is not None:
            sql += " AND c.techada = :techada"
            params['techada'] = 1 if filtros['techada'] else 0

        if filtros.get('activa') is not None:
            sql += " AND c.activa = :activa"
            params['activa'] = 1 if filtros['activa'] else 0

        res = ejecutar_consulta(sql, params)
        total = res[0]['total'] if res else 0

        return total, None
    
    except Exception as e:
        return 0, f"Error SQL al contar canchas: {str(e)}"

    
def existe_deporte(id_deporte):
    try:
        sql = "SELECT 1 FROM deportes WHERE id_deporte = :id_deporte"
        res = ejecutar_consulta(sql, {"id_deporte": id_deporte})
        return len(res) > 0, None
    except Exception as e:
        return False, f"Error SQL al verificar deporte: {str(e)}"


def insertar(datos):
    try:
        sql = """
            INSERT INTO canchas (nombre_cancha, id_deporte_cancha, precio_hora, techada, activa)
            VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa)
        """
        params = {
            "nombre": datos['nombre'],
            "id_deporte": datos['id_deporte'],
            "precio_hora": datos['precio_hora'],
            "techada": 1 if datos['techada'] else 0,
            "activa": 1 if datos['activa'] else 0
        }

        cancha_id = ejecutar_mutacion(sql, params)
        return cancha_id, None
    
    except Exception as e:
        return None, f"Error SQL al insertar cancha: {str(e)}"


def obtener_por_id(cancha_id):
    try:
        sql = """
            SELECT
                id_cancha AS id,
                nombre_cancha AS nombre,
                id_deporte_cancha AS id_deporte,
                precio_hora,
                techada,
                activa
            FROM canchas
            WHERE id_cancha = :id_cancha
        """
        filas = ejecutar_consulta(sql, {"id_cancha": cancha_id})
        if not filas:
            return None, None
        
        cancha = filas[0]
        cancha['techada'] = bool(cancha['techada'])
        cancha['activa'] = bool(cancha['activa'])

        return cancha, None
    
    except Exception as e:
        return None, f"Error SQL al buscar cancha por ID: {str(e)}"


def obtener_disponibles(params):
    try:
        fecha_str = params['fecha'].strftime('%Y-%m-%d')
        inicio_str = f"{fecha_str} {params['hora_inicio'].strftime('%H:%M:%S')}.000000"
        fin_str = f"{fecha_str} {params['hora_fin'].strftime('%H:%M:%S')}.000000"
        sql = """
            SELECT
                c.id_cancha AS id,
                c.nombre_cancha AS nombre,
                c.id_deporte_cancha AS id_deporte,
                c.precio_hora,
                c.techada,
                c.activa
            FROM canchas c
            WHERE c.activa = 1
                AND c.id_cancha NOT IN (
                    SELECT r.id_cancha_reserva
                    FROM reservas r
                    WHERE r.id_cancha_reserva IS NOT NULL
                        AND r.estado_actual = 'confirmada'
                        AND r.fecha_reserva_inicio < :fin_str
                        AND r.fecha_reserva_fin > :inicio_str
                )
        """
        query_params = {
            "inicio_str": inicio_str,
            "fin_str": fin_str
        }

        if params.get('id_deporte') is not None:
            sql += " AND c.id_deporte_cancha = :id_deporte"
            query_params['id_deporte'] = params['id_deporte']

        if params.get('techada') is not None:
            sql += " AND c.techada = :techada"
            query_params['techada'] = 1 if params['techada'] else 0

        sql += " ORDER BY c.id_cancha ASC LIMIT :limit OFFSET :offset"
        query_params['limit'] = params.get('_limit', 10)
        query_params['offset'] = params.get('_offset', 0)

        canchas = ejecutar_consulta(sql, query_params)
        for c in canchas:
            c['techada'] = bool(c['techada'])
            c['activa'] = bool(c['activa'])

        return canchas, None
    
    except Exception as e:
        return None, f"Error SQL al buscar disponibilidades: {str(e)}"


def contar_disponibles(params):
    try:
        fecha_str = params['fecha'].strftime('%Y-%m-%d')
        inicio_str = f"{fecha_str} {params['hora_inicio'].strftime('%H:%M:%S')}.000000"
        fin_str = f"{fecha_str} {params['hora_fin'].strftime('%H:%M:%S')}.000000"

        sql = """
            SELECT COUNT(*) AS total
            FROM canchas c
            WHERE c.activa = 1
                AND c.id_cancha NOT IN (
                    SELECT r.id_cancha_reserva
                    FROM reservas r
                    WHERE r.id_cancha_reserva IS NOT NULL
                        AND r.estado_actual = 'confirmada'
                        AND r.fecha_reserva_inicio < :fin_str
                        AND r.fecha_reserva_fin > :inicio_str
                )
        """
        query_params = {
            "inicio_str": inicio_str,
            "fin_str": fin_str
        }

        if params.get('id_deporte') is not None:
            sql += " AND c.id_deporte_cancha = :id_deporte"
            query_params['id_deporte'] = params['id_deporte']

        if params.get('techada') is not None:
            sql += " AND c.techada = :techada"
            query_params['techada'] = 1 if params['techada'] else 0

        res = ejecutar_consulta(sql, query_params)
        total = res[0]['total'] if res else 0

        return total, None

    except Exception as e:
        return 0, f"Error SQL al contar disponibilidades: {str(e)}"


def actualizar(cancha_id, datos):
    try:
        asignaciones = []
        params = {"id_cancha": cancha_id}

        if 'nombre' in datos:
            asignaciones.append("nombre_cancha = :nombre")

            params['nombre'] = datos['nombre']
        if 'precio_hora' in datos:
            asignaciones.append("precio_hora = :precio_hora")
            params['precio_hora'] = datos['precio_hora']

        if 'techada' in datos:
            asignaciones.append("techada = :techada")
            params['techada'] = 1 if datos['techada'] else 0

        if 'activa' in datos:
            asignaciones.append("activa = :activa")
            params['activa'] = 1 if datos['activa'] else 0

        if not asignaciones:
            return True, None
        
        sql = f"UPDATE canchas SET {', '.join(asignaciones)} WHERE id_cancha = :id_cancha"
        ejecutar_mutacion(sql, params)

        return True, None
    
    except Exception as e:
        return False, f"Error SQL al actualizar cancha: {str(e)}"


def tiene_reservas_asociadas(cancha_id):
    try:
        sql = "SELECT 1 FROM reservas WHERE id_cancha_reserva = :id_cancha LIMIT 1"
        res = ejecutar_consulta(sql, {"id_cancha": cancha_id})
        return len(res) > 0, None
    except Exception as e:
        return False, f"Error SQL al verificar reservas asociadas: {str(e)}"


def eliminar(cancha_id):
    try:
        # 1. Verificar si la cancha existe
        cancha, err = obtener_por_id(cancha_id)
        if err or not cancha:
            return False, {"code": "NOT_FOUND", "description": "La cancha solicitada no existe."}

        # 2. Verificar si posee reservas asociadas
        posee_reservas, err_res = tiene_reservas_asociadas(cancha_id)
        if err_res:
            return False, {"code": "INTERNAL_ERROR", "description": err_res}

        if posee_reservas:
            return False, {"code": "CONFLICT", "description": "La cancha tiene reservas asociadas."}

        # 3. Eliminar si no tiene reservas
        sql = "DELETE FROM canchas WHERE id_cancha = :id_cancha"
        ejecutar_mutacion(sql, {"id_cancha": cancha_id})
        return True, None
    
    except Exception as e:
        return False, f"Error SQL al eliminar cancha: {str(e)}"