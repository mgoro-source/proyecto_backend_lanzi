import logging
from flask import Flask, jsonify
from flask_cors import CORS
from constantes import BASE_URL 
from src.exceptions import ApiError
from src.route.deportes import deportes_bp
from src.route.canchas import bp as canchas_bp
#from src.route.socios import socios_bp
#from src.route.reservas import reservas_bp
#from src.route.extensiones import extensiones_bp



logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__)
app.json.sort_keys = False

# Habilitar CORS para que el frontend pueda consumir la API
CORS(app)

app.register_blueprint(deportes_bp, url_prefix=BASE_URL)
app.register_blueprint(canchas_bp, url_prefix=BASE_URL)
#app.register_blueprint(socios_bp, url_prefix=BASE_URL)
#app.register_blueprint(reservas_bp, url_prefix=BASE_URL)
#app.register_blueprint(extensiones_bp, url_prefix=BASE_URL)

@app.errorhandler(ApiError)
def handle_api_error(err):
    return jsonify(err.to_dict()), err.status_code

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"errors": [{"code": "NO_ENCONTRADO", "message": "Ruta no encontrada",
                                 "level": "error", "description": str(e)}]}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
