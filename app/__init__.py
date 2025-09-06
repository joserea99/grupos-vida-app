import os

from dotenv import load_dotenv
from flask import Flask


def create_app():
    # Cargar variables de entorno
    load_dotenv()

    app = Flask(__name__)

    # Configuración desde variables de entorno
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-por-defecto-cambiar")
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Registrar blueprints
    from app.api.routes import api_bp
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.tableros.routes import tableros_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(tableros_bp, url_prefix="/tableros")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
