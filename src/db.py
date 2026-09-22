from sqlalchemy import create_engine, text
from constantes import DB_URL


# Motor de conexion compartido por toda la aplicacion.
# El pool de conexiones lo maneja SQLAlchemy automaticamente.
motor = create_engine(DB_URL, pool_pre_ping=True)


# ---------------------------------------------------------------
# Funciones de soporte
# ---------------------------------------------------------------

def fila_a_dict(fila) -> dict:
    """Convierte una fila del resultado de una query en un diccionario."""
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    """Ejecuta una SELECT y devuelve todas las filas como lista de dicts."""
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    """
    Ejecuta un INSERT, UPDATE o DELETE y hace commit.
    Retorna el id autoincremental generado por el INSERT (0 si no aplica).
    """
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0


# ---------------------------------------------------------------
# Queries de deportes
# ---------------------------------------------------------------

def obtener_todos_los_deportes() -> list[dict]:
    """Retorna todos los alumnos ordenados por padron."""
    sql = 'SELECT id_deporte, nombre_deporte FROM deportes ORDER BY id_deporte'

    return ejecutar_consulta(sql)

# ---------------------------------------------------------------
# Queries de socios
# ---------------------------------------------------------------


def obtener_todos_los_socios() -> list[dict]:
    """Retorna todos los alumnos ordenados por padron."""
    sql = 'SELECT id_socio, nombre_socio, email_socio, activo FROM socios ORDER BY id_socio'

    return ejecutar_consulta(sql)

def insertar_socio(id_socio: int, nombre_socio: str,email_socio: str, activo : bool) -> int:
    """Inserta una nueva nota y retorna el id generado."""
    sql = """
        INSERT INTO socios (id_socio, nombre_socio, email_socio, activo)
        VALUES (:id_socio, :nombre_socio, :email_socio, :activo)
    """

    return ejecutar_mutacion(sql, {
        'id_socio':         id_socio,
        'nombre_socio': nombre_socio,
        'email_socio':   email_socio,
        'activo':         activo ,
    })



