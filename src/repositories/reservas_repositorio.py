import db
from constantes import (
    ESTADO_CONFIRMADA,
    CONDICION_CREACION_EXITOSA,
    LIMITE_PAGINACION_DEFECTO,
    OFFSET_PAGINACION_DEFECTO,
    SQL_OBTENER_CANCHA,
    SQL_OBTENER_RESERVA_POR_ID,
    SQL_OBTENER_SOCIO,
    SQL_ULTIMO_ID_INSERTADO
)

# # valores fijos
# ESTADO_CONFIRMADA = 'confirmada'
# CONDICION_CREACION_EXITOSA = 'Creada exitosamente'

# LIMITE_PAGINACION_DEFECTO = 10
# OFFSET_PAGINACION_DEFECTO = 0

# # constantes para reservas.py :)
# SQL_OBTENER_SOCIO = 'SELECT id_socio, nombre_socio, email_socio, activo FROM socios WHERE id_socio = %s'
# SQL_OBTENER_CANCHA = 'SELECT id_cancha, nombre_cancha, techada, precio_hora, activa, id_deporte_cancha FROM canchas WHERE id_cancha = %s'
# SQL_OBTENER_RESERVA_POR_ID = 'SELECT * FROM reservas WHERE id_reserva = %s'
# SQL_ULTIMO_ID_INSERTADO = 'SELECT LAST_INSERT_ID() AS id'

# esto es Auxiliar
def obtengo_socio(id_socio: int):
    resultados = db.ejecutar_consulta(SQL_OBTENER_SOCIO,(id_socio,))

    if resultados:
        retorna = resultados[0]

    return retorna

# auxiliar
def obtengo_cancha(id_cancha: int):
    resultados = db.ejecutar_consulta(SQL_OBTENER_CANCHA, (id_cancha,))
    
    if resultados:
        retorna = resultados[0]

    return retorna

# auxiliar
def pregunto_superposicion(id_cancha: int, id_socio: int, inicio: str, fin: str, id_reserva_ignore: int = None):
    sql = '''
        SELECT id_reserva 
        FROM reservas 
        WHERE estado_actual = 'confirmada'
          AND (id_cancha_reserva = %s OR id_socio_reserva = %s)
          AND (%s < fecha_reserva_fin AND %s > fecha_reserva_inicio)
    '''
    parametros = [ESTADO_CONFIRMADA, id_cancha, id_socio, inicio, fin]

    if id_reserva_ignore:
        sql += ' AND id_reserva != %s'
        parametros.append(id_reserva_ignore)

    resultados = db.ejecutar_consulta(sql, tuple(parametros))

    superpuesto = len(resultados) > 0
    return superpuesto

def crear_reserva(id_socio: int, id_cancha: int, inicio_str: str, fin_str: str, precio_hora: int):
    sql = '''
        INSERT INTO reservas 
        (estado_actual, estado_solicitado, condicion, fecha_reserva_inicio, fecha_reserva_fin, precio_hora, id_cancha_reserva, id_socio_reserva)
        VALUES ('confirmada', 'confirmada', 'Creada exitosamente', %s, %s, %s, %s, %s)
    '''

    parametros = (
        ESTADO_CONFIRMADA,
        ESTADO_CONFIRMADA,
        CONDICION_CREACION_EXITOSA,
        inicio_str,
        fin_str,
        precio_hora,
        id_cancha,
        id_socio
    )
    reserva_id = db.ejecutar_consulta(sql, parametros)
    
    if not isinstance(reserva_id, int):
        resultado = db.ejecutar_consulta(SQL_ULTIMO_ID_INSERTADO)
        reserva_id = list(resultado[0].values())[0]

    return obtener_reserva_por_id(reserva_id)

# Auxiliar
def obtener_reserva_por_id(id_reserva: int):
    resultados = db.ejecutar_consulta(SQL_OBTENER_RESERVA_POR_ID, (id_reserva,))
    
    if resultados:
        retorna = resultados[0]

    return retorna

def actualizar_estado(id_reserva: int, nuevo_estado: str, estado_solicitado: str, condicion: str):
    sql = '''
        UPDATE reservas 
        SET estado_actual = %s, estado_solicitado = %s, condicion = %s 
        WHERE id_reserva = %s
    '''
    db.ejecutar_consulta(sql, (nuevo_estado, estado_solicitado, condicion, id_reserva))
    return obtener_reserva_por_id(id_reserva)

def listar_reservas(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None, limit=10, offset=0):
    sql_base = 'FROM reservas WHERE 1=1'
    parametros = []

    if id_cancha:
        sql_base += ' AND id_cancha_reserva = %s'
        parametros.append(id_cancha)
    if id_socio:
        sql_base += ' AND id_socio_reserva = %s'
        parametros.append(id_socio)
    if estado:
        sql_base += ' AND estado_actual = %s'
        parametros.append(estado)
    if fecha_desde:
        sql_base += ' AND DATE(fecha_reserva_inicio) >= %s'
        parametros.append(fecha_desde)
    if fecha_hasta:
        sql_base += ' AND DATE(fecha_reserva_inicio) <= %s'
        parametros.append(fecha_hasta)

    sql_total = f'SELECT COUNT(*) as total {sql_base}'
    res_total = db.ejecutar_consulta(sql_total, tuple(parametros))
    if res_total:
        total = res_total[0]['total']

    sql_datos = f'SELECT * {sql_base} ORDER BY id_reserva ASC LIMIT %s OFFSET %s'
    parametros_paginados = parametros + [limit, offset]
    reservas = db.ejecutar_consulta(sql_datos, tuple(parametros_paginados))

    return reservas, total
