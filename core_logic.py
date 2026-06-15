from datetime import datetime, date
import db_manager

def obtener_ultimo_ingreso(persona_id):
    conn = db_manager.get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT fecha FROM registros
            WHERE persona_id = ? AND tipo = 'ingreso'
            ORDER BY fecha DESC LIMIT 1
        """, (int(persona_id),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0].split()[0]
        return None
    except Exception as e:
        print(f"❌ Error en obtener_ultimo_ingreso: {e}")
        conn.close()
        return None

def calcular_estado(fecha_inicio):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        hoy = date.today()
        dias = (hoy - inicio).days

        if dias < 0:
            return "error", "Fecha futura", "—"

        dia_en_ciclo = dias % 31

        if dia_en_ciclo < 21:
            estado = "en_campo"
            dias_en_campo = dia_en_ciclo + 1
            dias_restantes = 20 - dia_en_ciclo
            return estado, f"En campo ({dias_en_campo} días)", f"Faltan {dias_restantes} días en campo"
        else:
            estado = "descansando"
            dia_descanso = dia_en_ciclo - 20
            dias_restantes = 31 - dia_en_ciclo
            return estado, f"Descansando ({dia_descanso}° día)", f"Faltan {dias_restantes} días de descanso"
    except Exception as e:
        print(f"❌ Error en calcular_estado: {e}")
        return "error", "Error", "—"

def obtener_personal():
    conn = db_manager.get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.id, p.nombre, p.fecha_inicio, pos.nombre, pos.requeridos
            FROM personas p
            JOIN puestos pos ON p.puesto_id = pos.id
        """)
        rows = cursor.fetchall()
        conn.close()
        resultado = []
        for r in rows:
            id_emp = r[0]
            ultimo_ingreso = obtener_ultimo_ingreso(id_emp)
            fecha_usada = ultimo_ingreso or r[2]
            estado, estado_texto, dias_rest = calcular_estado(fecha_usada)
            alerta = ""
            if estado == "en_campo":
                dias_restantes = int(dias_rest.split()[1])
                if dias_restantes <= 7:
                    alerta = f"Faltan {dias_restantes} días más en campo"
            resultado.append({
                "id": id_emp,
                "nombre": r[1],
                "inicio": fecha_usada,
                "puesto": r[3],
                "requeridos": r[4],
                "estado": estado,
                "estado_texto": estado_texto,
                "dias_restantes": dias_rest,
                "alerta": alerta
            })
        return resultado
    except Exception as e:
        print(f"❌ Error al obtener personal: {e}")
        conn.close()
        return []

def reporte_cobertura():
    personal = obtener_personal()
    en_campo = [p for p in personal if p["estado"] == "en_campo"]
    cobertura = {}
    for p in en_campo:
        puesto = p["puesto"]
        if puesto not in cobertura:
            cobertura[puesto] = {"actual": 0, "requerido": p["requeridos"]}
        cobertura[puesto]["actual"] += 1
    return cobertura
