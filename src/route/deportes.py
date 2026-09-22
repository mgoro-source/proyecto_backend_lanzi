from flask import Blueprint, jsonify, request
from ..services.deportes import (
    listar_deportes,
    )

deportes_bp = Blueprint('deportes', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    deportes = listar_deportes()

    if not deportes:
        return '', 204

    return jsonify(deportes)

