import os
from datetime import datetime, timezone, timedelta

# URL base de la API
BASE_URL = '/'


# Configuracion de la base de datos MySQL (levantada via docker-compose)
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME     = os.getenv('DB_NAME', 'facultad')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Codigos de error
ERROR_CODE_INVALID_BODY        = 'invalid.body'
ERROR_CODE_INVALID_MIN_VALUE   = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE   = 'invalid.max.value'
ERROR_CODE_ALUMNO_NOT_FOUND    = 'alumno.not.found'
ERROR_CODE_MATERIA_NOT_FOUND   = 'materia.not.found'

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

# valores fijos
ESTADOS_VALIDOS = ['cancelada', 'finalizada', 'confirmada']
ESTADO_CONFIRMADA = 'confirmada'
CONDICION_CREACION_EXITOSA = 'Creada exitosamente'
CONDICION_CANCELACION = "Cancelación realizada antes del horario de inicio"
CONDICION_FINALIZACION = "Finalización confirmada tras transcurrir el turno"
ESTADO_CANCELADA = 'cancelada'
ESTADO_FINALIZADA = 'finalizada'

LIMITE_PAGINACION_DEFECTO = 10
OFFSET_PAGINACION_DEFECTO = 0
LIMIT_MINIMO = 1
LIMIT_MAXIMO = 100

# constantes para reservas.py
SQL_OBTENER_SOCIO = 'SELECT id_socio, nombre_socio, email_socio, activo FROM socios WHERE id_socio = %s'
SQL_OBTENER_CANCHA = 'SELECT id_cancha, nombre_cancha, techada, precio_hora, activa, id_deporte_cancha FROM canchas WHERE id_cancha = %s'
SQL_OBTENER_RESERVA_POR_ID = 'SELECT * FROM reservas WHERE id_reserva = %s'
SQL_ULTIMO_ID_INSERTADO = 'SELECT LAST_INSERT_ID() AS id'

CAMPOS_REQUERIDOS_CREACION = ['id_socio', 'id_cancha', 'fecha_hora_inicio', 'fecha_hora_fin']
CAMPOS_PERMITIDOS_ESTADO = {'estado'}

# horarios
HORA_APERTURA_CLUB = 8
HORA_CIERRE_CLUB = 23
DURACION_MINIMA_HORAS = 1
DURACION_MAXIMA_HORAS = 3

ZONA_HORARIA_ARGENTINA = timezone(timedelta(hours=-3))
