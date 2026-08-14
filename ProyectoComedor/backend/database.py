import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comedor.db")

SECURITY_QUESTIONS_CATALOG = {
    'primer_amor': '¿Cómo se llamaba tu primer amor?',
    'maestro_favorito': '¿Quién fue tu maestro(a) favorito(a)?',
    'lugar_nacimiento': '¿En qué ciudad o lugar naciste?',
    'pais_visitar': '¿Qué país te gustaría visitar?',
    'dia_memorable': '¿Cuál es tu día o fecha más memorable?',
    'primera_escuela': '¿Cómo se llamaba tu primera escuela?',
    'primera_mascota': '¿Cuál es el nombre de tu primera mascota?',
    'comida_favorita': '¿Cuál es tu comida favorita?',
    'mejor_amigo_infancia': '¿Cómo se llamaba tu mejor amigo(a) de la infancia?',
    'primer_trabajo': '¿Cuál fue tu primer trabajo?'
}

def get_connection():
    """Retorna una conexión a la base de datos SQLite con soporte para Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db():
    """Context manager para gestionar transacciones de base de datos."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Crea las tablas de la base de datos si no existen."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                ocupacion TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                genero TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabla de preguntas de seguridad por usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preguntas_seguridad_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                clave_pregunta TEXT NOT NULL,
                respuesta_hash TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
        """)
        
        # Tabla de sesiones de usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                token TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
        """)
