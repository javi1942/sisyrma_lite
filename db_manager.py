mport sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "empleados.db"

def init_db():
    try:
        DB_PATH.parent.mkdir(exist_ok=True)
        if not os.access(DB_PATH.parent, os.W_OK):
        raise PermissionError(f"No hay permisos de escritura en {DB_PATH.parent}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS puestos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                requeridos INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                puesto_id INTEGER,
                fecha_inicio TEXT NOT NULL,
                FOREIGN KEY (puesto_id) REFERENCES puestos (id)
            );

            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_id INTEGER,
                tipo TEXT CHECK(tipo IN ('ingreso', 'salida')),
                fecha TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (persona_id) REFERENCES personas (id)
            );
        """)

        cursor.execute("INSERT OR IGNORE INTO puestos (nombre, requeridos) VALUES (?, ?)", ("Operador", 2))
        cursor.execute("INSERT OR IGNORE INTO puestos (nombre, requeridos) VALUES (?, ?)", ("Supervisor", 1))

        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada")
    except PermissionError as e:
        print(f"❌ Error de permisos: {e}")
    except Exception as e:
        print(f"❌ Error al inicializar DB: {e}")
   
def get_connection():
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"❌ No se pudo conectar: {e}")
        return None
        
