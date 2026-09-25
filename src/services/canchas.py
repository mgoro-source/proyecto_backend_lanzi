from src.repositories import canchas as repo
from src.repositories import deportes as repo_deportes
from src.exceptions import ValidationError, NotFoundError
from src import utils
from src import constantes as C

CAMPOS_CREATE = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
CAMPOS_UPDATE = {"nombre", "precio_hora", "techada", "activa"}


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValidationError("El campo 'nombre' es inválido", "'nombre' no puede estar vacío")
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
        raise ValidationError(f"El campo '{campo}' es inválido", f"'{campo}' debe ser booleano")
    return valor


def _mapear_a_schema(cancha: dict) -> dict:
    """Traduce columnas DB → schema del swagger."""
    return {
        "id": cancha["id_cancha"],
        "nombre": cancha["nombre"],
        "id_deporte": cancha["id_deporte"],
        "precio_hora": cancha["precio_hora"],
        "techada": cancha["techada"],
        "activa": cancha["activa"],
    }


def listar(filtros, limit, offset):
    if limit < C.LIMIT_MIN or limit > C.LIMIT_MAX:
        raise ValidationError("'_limit' fuera de rango", "Debe estar entre 1 y 100")
    if offset < 0:
        raise ValidationError("'_offset' inválido", "Debe ser >= 0")
    filas, total = repo.obtener_todas(filtros, limit, offset)
    return [_mapear_a_schema(c) for c in filas], total


def obtener(id_cancha):
    return _mapear_a_schema(repo.obtener_por_id(id_cancha))


def crear(data):
    utils.validar_campos_permitidos(data, CAMPOS_CREATE)
    if not data:
        raise ValidationError("El cuerpo está vacío")

    nombre = _validar_nombre(data.get("nombre"))
    id_deporte = data.get("id_deporte")
    if not isinstance(id_deporte, int) or isinstance(id_deporte, bool):
        raise ValidationError("'id_deporte' inválido", "Debe ser un entero")

    if not repo_deportes.obtener_todos_los_deportes():
        raise ValidationError("No hay deportes cargados")
    deportes_ids = {d["id_deporte"] for d in repo_deportes.obtener_todos_los_deportes()}
    if id_deporte not in deportes_ids:
        raise NotFoundError("Deporte no encontrado", f"No existe deporte con id {id_deporte}")

    precio = _validar_precio(data.get("precio_hora"))
    techada = _validar_bool(data, "techada", False)
    activa = _validar_bool(data, "activa", True)

    nuevo_id = repo.crear({
        "nombre": nombre,
        "id_deporte": id_deporte,
        "precio_hora": precio,
        "techada": techada,
        "activa": activa,
    })
    return obtener(nuevo_id)


def actualizar(id_cancha, data):
    utils.validar_campos_permitidos(data, CAMPOS_UPDATE)
    if not data:
        raise ValidationError("El cuerpo está vacío")

    repo.obtener_por_id(id_cancha)  # 404 si no existe

    limpio = {}
    if "nombre" in data:
        limpio["nombre"] = _validar_nombre(data["nombre"])
    if "precio_hora" in data:
        limpio["precio_hora"] = _validar_precio(data["precio_hora"])
    if "techada" in data:
        limpio["techada"] = _validar_bool(data, "techada", False)
    if "activa" in data:
        limpio["activa"] = _validar_bool(data, "activa", True)

    repo.actualizar(id_cancha, limpio)


def eliminar(id_cancha):
    repo.obtener_por_id(id_cancha)
    repo.eliminar(id_cancha)


def disponibles(fecha_str, hora_inicio, hora_fin, filtros, limit, offset):
    fecha = utils.parsear_fecha(fecha_str, "fecha")
    utils.validar_hora_en_punto(hora_inicio, "hora_inicio")
    utils.validar_hora_en_punto(hora_fin, "hora_fin")

    inicio_dt = utils.parsear_fecha_hora(f"{fecha.isoformat()}T{hora_inicio}.000000-03:00", "hora_inicio")
    fin_dt = utils.parsear_fecha_hora(f"{fecha.isoformat()}T{hora_fin}.000000-03:00", "hora_fin")
    utils.validar_intervalo_reserva(inicio_dt, fin_dt)

    filas = repo.obtener_disponibles(fecha.isoformat(), hora_inicio, hora_fin, filtros)
    canchas = [_mapear_a_schema(c) for c in filas]
    total = len(canchas)
    return canchas[offset:offset + limit], total