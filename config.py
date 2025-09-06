import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-cambiar'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///ministerio.db'
    UPLOADS_FOLDER = os.environ.get('UPLOADS_FOLDER') or 'app/static/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16777216)

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    
class TestingConfig(Config):
    """Configuración de testing"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
