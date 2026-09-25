from flask import Blueprint, request, jsonify
from src.services import canchas as service
from src.exceptions import ValidationError
from src import constantes as C
from src.utils import parsear_bool

bp = Blueprint("canchas", __name__)


def _paginacion():
    try:
        limit = int(request.args.get("_limit", C.LIMIT_DEFAULT))
        offset = int(request.args.get("_offset", C.OFFSET_DEFAULT))
    except ValueError:
        raise ValidationError("Parámetros de paginación inválidos")
    return limit, offset


def _filtros_cancha():
    f = {}
    if "id_deporte" in request.args:
        try:
            f["id_deporte"] = int(request.args["id_deporte"])
        except ValueError:
            raise ValidationError("'id_deporte' debe ser entero")
    if "nombre" in request.args:
        f["nombre"] = request.args["nombre"]
    if "techada" in request.args:
        f["techada"] = parsear_bool(request.args["techada"], "techada")
    if "activa" in request.args:
        f["activa"] = parsear_bool(request.args["activa"], "activa")
    return f


@bp.get("/canchas/disponibles")
def disponibles():
    for req in ("fecha", "hora_inicio", "hora_fin"):
        if req not in request.args:
            raise ValidationError(f"Falta el parámetro obligatorio '{req}'")
    filtros = _filtros_cancha()
    limit, offset = _paginacion()
    canchas, _ = service.disponibles(
        request.args["fecha"],
        request.args["hora_inicio"],
        request.args["hora_fin"],
        filtros, limit, offset
    )
    return jsonify({"canchas": canchas, "_links": {}}), 200


@bp.get("/canchas")
def listar():
    filtros = _filtros_cancha()
    limit, offset = _paginacion()
    canchas, _ = service.listar(filtros, limit, offset)
    if not canchas:
        return "", 204
    return jsonify({"canchas": canchas, "_links": {}}), 200


@bp.post("/canchas")
def crear():
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError("El cuerpo debe ser JSON")
    return jsonify(service.crear(data)), 201


@bp.get("/canchas/<int:id>")
def obtener(id):
    return jsonify(service.obtener(id)), 200


@bp.patch("/canchas/<int:id>")
def actualizar(id):
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError("El cuerpo debe ser JSON")
    service.actualizar(id, data)
    return "", 204


@bp.delete("/canchas/<int:id>")
def eliminar(id):
    service.eliminar(id)
    return "", 204