from datetime import datetime, date
import db_manager

def obtener_ultimo_ingreso(persona_id):
    """Obtiene la fecha del último ingreso al lote"""
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
            return row[0].split()[0]  # Devuelve solo la fecha: YYYY-MM-DD
        return None
    except Exception as e:
        print(f"❌ Error en obtener_ultimo_ingreso: {e}")
        conn.close()
        return None

def obtener_ultima_salida(persona_id):
    """Obtiene la fecha de la última salida del lote"""
    conn = db_manager.get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT fecha FROM registros
            WHERE persona_id = ? AND tipo = 'salida'
            ORDER BY fecha DESC LIMIT 1
        """, (int(persona_id),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0].split()[0]  # Devuelve solo la fecha: YYYY-MM-DD
        return None
    except Exception as e:
        print(f"❌ Error en obtener_ultima_salida: {e}")
        conn.close()
        return None

def calcular_estado(fecha_inicio):
    """Calcula estado: en campo o descansando, sin resultados negativos"""
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        hoy = date.today()
        dias = (hoy - inicio).days
        
        # Si la fecha es futura
        if dias < 0:
            return "error", "Fecha futura", "—"
        
        # Usar módulo para ciclo de 31 días
        dia_en_ciclo = dias % 31  # 0 a 30
        if dia_en_ciclo < 21:
            estado = "en_campo"
            dias_en_campo = dia_en_ciclo + 1
            dias_restantes = 20 - dia_en_ciclo
            return estado, f"En campo ({dias_en_campo} días)", f"Faltan {dias_restantes} días más en campo"
        else:
            estado = "descansando"
            dia_descanso = dia_en_ciclo - 20  # 1 al 10
            dias_restantes = 31 - dia_en_ciclo
            return estado, f"Descansando ({dia_descanso}° día)", f"Faltan {dias_restantes} días de descanso"
    except Exception as e:
        print(f"❌ Error en calcular_estado: {e}")
        return "error", "Error", "—"

def calcular_estado_con_registros(persona_id, fecha_inicio):
    """Calcula estado considerando registros manuales de ingreso/salida"""
    ultimo_ingreso = obtener_ultimo_ingreso(persona_id)
    ultima_salida = obtener_ultima_salida(persona_id)
    
    # Si hay registros manuales
    if ultimo_ingreso or ultima_salida:
        # Si no hay salida o el último ingreso es más reciente que la última salida
        if not ultima_salida or (ultimo_ingreso and ultimo_ingreso > ultima_salida):
            # Está en campo - usar fecha de último ingreso
            fecha_usada = ultimo_ingreso
            estado, estado_texto, dias_rest = calcular_estado(fecha_usada)
            return estado, estado_texto, dias_rest
        else:
            # Está descansando - usar fecha de última salida
            fecha_usada = ultima_salida
            return "descansando", f"Descansando (desde {fecha_usada})", "—"
    else:
        # Sin registros manuales, usar ciclo automático desde fecha_inicio
        return calcular_estado(fecha_inicio)

def obtener_personal():
    """Obtiene lista completa con estado actual"""
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
        
        print(f"✅ Se encontraron {len(rows)} empleados en la base de datos")
        resultado = []
        for r in rows:
            id_emp = r[0]
            print(f"🔍 Procesando empleado ID={id_emp} - {r[1]}")
            
            # ✅ Ahora usa la nueva función que considera registros manuales
            estado, estado_texto, dias_rest = calcular_estado_con_registros(id_emp, r[2])
            
            alerta = ""
            if estado == "en_campo":
                try:
                    dias_restantes = int(dias_rest.split()[1])
                    if dias_restantes <= 7:
                        alerta = f"Faltan {dias_restantes} días en campo"
                except:
                    pass
            
            resultado.append({
                "id": id_emp,
                "nombre": r[1],
                "inicio": r[2],
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
    """Devuelve cobertura actual (solo en campo)"""
    personal = obtener_personal()
    en_campo = [p for p in personal if p["estado"] == "en_campo"]
    cobertura = {}
    for p in en_campo:
        puesto = p["puesto"]
        if puesto not in cobertura:
            cobertura[puesto] = {"actual": 0, "requerido": p["requeridos"]}
        cobertura[puesto]["actual"] += 1
    return cobertura