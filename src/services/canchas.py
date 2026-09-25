from src.db import ejecutar_consulta
from src.repositories import canchas as repo
from src.repositories import deportes as repo_deportes
from src.exceptions import ValidationError, NotFoundError
from src import utils
from src import constantes as C

CAMPOS_CREATE = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
CAMPOS_UPDATE = {"nombre", "precio_hora", "techada", "activa"}


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValidationError(
            "El campo 'nombre' es inválido",
            "'nombre' no puede estar vacío"
        )
    return nombre.strip()


def _validar_precio(precio):
    if not isinstance(precio, int) or isinstance(precio, bool) or precio <= 0:
        raise ValidationError(
            "El campo 'precio_hora' es inválido",
            "'precio_hora' debe ser un entero positivo (centavos)"
        )
    return precio


def _validar_bool(data, campo, default):
    if campo not in data:
        return default
    valor = data[campo]
    if not isinstance(valor, bool):
        raise ValidationError(
            f"El campo '{campo}' es inválido",
            f"'{campo}' debe ser booleano"
        )
    return valor


def listar(filtros, limit, offset):
    if limit < C.LIMIT_MIN or limit > C.LIMIT_MAX:
        raise ValidationError("'_limit' fuera de rango", "Debe estar entre 1 y 100")
    if offset < 0:
        raise ValidationError("'_offset' inválido", "Debe ser >= 0")
    return repo.get_all(filtros, limit, offset)


def obtener(id_cancha):
    return repo.get_by_id(id_cancha)


def crear(data):
    utils.validar_campos_permitidos(data, CAMPOS_CREATE)
    if not data:
        raise ValidationError("El cuerpo está vacío")

    nombre = _validar_nombre(data.get("nombre"))
    id_deporte = data.get("id_deporte")
    if not isinstance(id_deporte, int) or isinstance(id_deporte, bool):
        raise ValidationError("'id_deporte' inválido", "Debe ser entero")

    # Validar que el deporte exista
    if not ejecutar_consulta("SELECT id FROM deporte WHERE id = :id", {"id": id_deporte}):
        raise NotFoundError("Deporte no encontrado", f"No existe deporte {id_deporte}")

    precio = _validar_precio(data.get("precio_hora"))
    techada = _validar_bool(data, "techada", False)
    activa = _validar_bool(data, "activa", True)

    nuevo_id = repo.create({
        "nombre": nombre,
        "id_deporte": id_deporte,
        "precio_hora": precio,
        "techada": techada,
        "activa": activa,
    })
    return repo.get_by_id(nuevo_id)


def actualizar(id_cancha, data):
    utils.validar_campos_permitidos(data, CAMPOS_UPDATE)
    if not data:
        raise ValidationError("El cuerpo está vacío")

    # Verificar que exista
    repo.get_by_id(id_cancha)

    limpio = {}
    if "nombre" in data:
        limpio["nombre"] = _validar_nombre(data["nombre"])
    if "precio_hora" in data:
        limpio["precio_hora"] = _validar_precio(data["precio_hora"])
    if "techada" in data:
        limpio["techada"] = _validar_bool(data, "techada", False)
    if "activa" in data:
        limpio["activa"] = _validar_bool(data, "activa", True)

    repo.update(id_cancha, limpio)


def eliminar(id_cancha):
    repo.get_by_id(id_cancha)  # 404 si no existe
    repo.delete(id_cancha)


def disponibles(fecha_str, hora_inicio, hora_fin, filtros, limit, offset):
    fecha = utils.parsear_fecha(fecha_str, "fecha")
    hi = utils.validar_hora_en_punto(hora_inicio, "hora_inicio")
    hf = utils.validar_hora_en_punto(hora_fin, "hora_fin")

    inicio_dt = utils.parsear_fecha_hora(
        f"{fecha.isoformat()}T{hora_inicio}.000000-03:00", "hora_inicio"
    )
    fin_dt = utils.parsear_fecha_hora(
        f"{fecha.isoformat()}T{hora_fin}.000000-03:00", "hora_fin"
    )
    utils.validar_intervalo_reserva(inicio_dt, fin_dt)

    canchas = repo.get_disponibles(fecha.isoformat(), hora_inicio, hora_fin, filtros)
    total = len(canchas)
    return canchas[offset:offset + limit], total