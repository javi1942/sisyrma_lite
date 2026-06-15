import db_manager
import csv
import os

def cargar_prueba():
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM personas")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Ya existen {count} empleados. No se cargan datos de prueba.")
            conn.close()
            return
        
        datos = [
            ("Arturo López", 1, "2025-07-01"),
            ("Carlos Ruiz", 1, "2025-07-01"),
            ("Luisa Mendoza", 2, "2025-07-01")
        ]

        for nombre, puesto_id, fecha_inicio in datos:
            conn.execute("""
                INSERT INTO personas (nombre, puesto_id, fecha_inicio)
                VALUES (?, ?, ?)
            """, (nombre, puesto_id, fecha_inicio))
        
        conn.commit()
        conn.close()
        print("✅ Datos de prueba cargados correctamente")
    except Exception as e:
        print(f"❌ Error al cargar datos de prueba: {e}")

def importar_csv(ruta_csv):
    if not os.path.exists(ruta_csv):
        return False, "❌ Archivo no encontrado"
    try:
        conn = db_manager.get_connection()
        contador = 0

        with open(ruta_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM personas WHERE nombre = ? AND fecha_inicio = ?", 
                             (row["nombre"], row["fecha_inicio"]))
                if cursor.fetchone() is None:
                    conn.execute("""
                        INSERT INTO personas (nombre, puesto_id, fecha_inicio)
                        VALUES (?, ?, ?)
                    """, (row["nombre"], int(row["puesto_id"]), row["fecha_inicio"]))
                    contador += 1

        conn.commit()
        conn.close()
        return True, f"✅ {contador} empleados importados"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
