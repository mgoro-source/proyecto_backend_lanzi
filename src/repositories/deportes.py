import src.db 

def obtener_todos_los_deportes() -> list[dict]:
    """Retorna todos los alumnos ordenados por padron."""
    sql = 'SELECT id_deporte, nombre_deporte FROM deportes ORDER BY id_deporte'

    return src.db.ejecutar_consulta(sql)

