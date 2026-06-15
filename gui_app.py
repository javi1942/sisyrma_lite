import tkinter as tk
from tkinter import ttk, messagebox
import core_logic
import db_manager
import data_loader
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Seguimiento de Personal Consorcio EBD - Control 21x10")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e293b")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#334155",
                        foreground="#f8fafc",
                        fieldbackground="#334155",
                        borderwidth=0,
                        font=("Segoe UI", 9))
        style.map("Treeview", background=[("selected", "#2563eb")])
        style.configure("Treeview.Heading",
                        background="#1e40af",
                        foreground="#f8fafc",
                        font=("Segoe UI", 9, "bold"))

        tk.Label(self.root, text="Seguim_Personal Consorcio EBD by Arturo Tapullima", 
                 font=("Segoe UI", 14, "bold"),
                 bg="#1e293b", fg="#f8fafc").pack(pady=10)

        frame_table = tk.Frame(self.root, bg="#1e293b")
        frame_table.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        cols = ("ID", "Nombre", "Puesto", "Inicio Ciclo", "Estado", "Próximo Evento", "Alerta")
        self.tree = ttk.Treeview(frame_table, columns=cols, show="headings", selectmode="browse")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=80)

        vscroll = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vscroll.set)
        hscroll = ttk.Scrollbar(frame_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")
        frame_table.grid_rowconfigure(0, weight=1)
        frame_table.grid_columnconfigure(0, weight=1)

        button_frame = tk.Frame(self.root, bg="#1e293b")
        button_frame.pack(fill=tk.X, padx=14, pady=14)

        botones = [
            ("Actualizar", self.cargar, "#3b82f6"),
            ("Ingreso al Lote", self.ingreso, "#10b981"),
            ("Reg.Salida", self.salida, "#ef4444"),
            ("Agregar Manual", self.agregar_manual, "#f59e0b"),
            ("Agregar Puesto", self.agregar_puesto, "#06b6d4"),
            ("Importar CSV", self.importar_csv, "#6b7280"),
            ("Reporte", self.reporte, "#8b5cf6"),
            ("Borrar", self.borrar_empleado, "#ef4444"),
        ]

        for texto, comando, color in botones:
            btn = tk.Button(button_frame, text=texto, command=comando,
                          bg=color, fg="white", font=("Segoe UI", 8, "bold"),
                          relief="flat", padx=10, pady=6)
            btn.pack(side=tk.LEFT, padx=3, pady=2)

        self.cargar()

    def cargar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            empleados = core_logic.obtener_personal()
            for emp in empleados:
                alerta_text = "⚠️ Sí" if emp["alerta"] else "No"
                iid = self.tree.insert("", "end", values=(
                    emp["id"], emp["nombre"], emp["puesto"],
                    emp["inicio"], emp["estado_texto"],
                    emp["dias_restantes"], alerta_text
                ))
                if emp["alerta"]:
                    self.tree.tag_configure('alerta', foreground='#fbbf24')
                    self.tree.item(iid, tags=('alerta',))
        except Exception as e:
            messagebox.showerror("Error", f"No se cargaron datos:\n{str(e)}")

    def ingreso(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "⚠️ Seleccione un empleado")
            return
        item = self.tree.item(selected[0])
        persona_id = item['values'][0]
        nombre = item['values'][1]
        if not messagebox.askyesno("Confirmar", f"¿Registrar INGRESO al lote para {nombre}?"):
            return
        try:
            conn = db_manager.get_connection()
            conn.execute("INSERT INTO registros (persona_id, tipo, fecha) VALUES (?, 'ingreso', datetime('now', 'localtime'))", (persona_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"✅ {nombre} ingresó al lote")
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {e}")

    def salida(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "⚠️ Seleccione un empleado")
            return
        item = self.tree.item(selected[0])
        persona_id = item['values'][0]
        nombre = item['values'][1]
        if not messagebox.askyesno("Confirmar", f"¿Registrar SALIDA del lote para {nombre}?"):
            return
        try:
            conn = db_manager.get_connection()
            conn.execute("INSERT INTO registros (persona_id, tipo, fecha) VALUES (?, 'salida', datetime('now', 'localtime'))", (persona_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"✅ {nombre} salió del lote")
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {e}")

    def agregar_manual(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Empleado")
        dialog.geometry("400x350")
        dialog.configure(bg="#1e293b")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Nombre:", bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 10)).pack(pady=5)
        entry_nombre = tk.Entry(dialog, width=40)
        entry_nombre.pack(pady=5)

        tk.Label(dialog, text="Fecha inicio (YYYY-MM-DD):", bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 10)).pack(pady=5)
        entry_fecha = tk.Entry(dialog, width=40)
        entry_fecha.pack(pady=5)

        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM puestos ORDER BY nombre")
            puestos_db = cursor.fetchall()
            conn.close()

            puestos_nombres = [f"{p[0]} - {p[1]}" for p in puestos_db]
            puesto_var = tk.StringVar()

            tk.Label(dialog, text="Puesto:", bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 10)).pack(pady=5)
            combo = ttk.Combobox(dialog, values=puestos_nombres, textvariable=puesto_var, state="readonly", width=37)
            combo.pack(pady=5)
            combo.set(puestos_nombres[0])
        except Exception as e:
            messagebox.showerror("Error", f"No se cargaron puestos: {e}")
            dialog.destroy()
            return

        def guardar():
            nombre = entry_nombre.get().strip()
            fecha = entry_fecha.get().strip()
            if not puesto_var.get():
                messagebox.showerror("Error", "Seleccione un puesto")
                return
            try:
                puesto_id = int(puesto_var.get().split(" - ")[0])
            except:
                messagebox.showerror("Error", "Puesto inválido")
                return
            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return
            if not fecha or len(fecha) != 10 or fecha[4] != '-' or fecha[7] != '-':
                messagebox.showwarning("Advertencia", "Formato de fecha inválido")
                return
            try:
                conn = db_manager.get_connection()
                conn.execute("INSERT INTO personas (nombre, puesto_id, fecha_inicio) VALUES (?, ?, ?)", (nombre, puesto_id, fecha))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", f"✅ '{nombre}' agregado correctamente")
                dialog.destroy()
                self.cargar()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        frame_btn = tk.Frame(dialog, bg="#1e293b")
        frame_btn.pack(pady=20)
        tk.Button(frame_btn, text="Guardar", command=guardar, bg="#10b981", fg="white", font=("Segoe UI", 9, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="Cancelar", command=dialog.destroy, bg="#6b7280", fg="white", font=("Segoe UI", 9), width=10).pack(side=tk.LEFT, padx=5)

    def agregar_puesto(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Puesto")
        dialog.geometry("350x200")
        dialog.configure(bg="#1e293b")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Nombre del puesto:", bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 10)).pack(pady=5)
        entry_nombre = tk.Entry(dialog, width=40)
        entry_nombre.pack(pady=5)

        tk.Label(dialog, text="Requeridos por turno:", bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 10)).pack(pady=5)
        entry_req = tk.Entry(dialog, width=40)
        entry_req.pack(pady=5)

        def guardar():
            nombre = entry_nombre.get().strip()
            try:
                requeridos = int(entry_req.get().strip())
                if requeridos < 1: raise ValueError
            except:
                messagebox.showerror("Error", "Número inválido")
                return
            if not nombre:
                messagebox.showerror("Error", "Nombre es obligatorio")
                return
            try:
                conn = db_manager.get_connection()
                conn.execute("INSERT INTO puestos (nombre, requeridos) VALUES (?, ?)", (nombre, requeridos))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", f"✅ Puesto '{nombre}' agregado")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        frame_btn = tk.Frame(dialog, bg="#1e293b")
        frame_btn.pack(pady=20)
        tk.Button(frame_btn, text="Guardar", command=guardar, bg="#06b6d4", fg="white", font=("Segoe UI", 9, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="Cancelar", command=dialog.destroy, bg="#6b7280", fg="white", font=("Segoe UI", 9), width=10).pack(side=tk.LEFT, padx=5)

    def importar_csv(self):
        ruta = os.path.join(os.path.dirname(__file__), "empleados.csv")
        if not os.path.exists(ruta):
            messagebox.showerror("Archivo no encontrado", f"No se encontró 'empleados.csv' en:\n{ruta}")
            return
        if not messagebox.askyesno("Importar CSV", f"Usar:\n{ruta}\n\n¿Continuar?"):
            return
        exito, mensaje = data_loader.importar_csv(ruta)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar()
        else:
            messagebox.showerror("Error", mensaje)

    def reporte(self):
        try:
            cob = core_logic.reporte_cobertura()
            msg = "📋 COBERTURA EN CAMPO\n\n"
            completo = True
            for puesto, datos in cob.items():
                estado = "✅" if datos["actual"] >= datos["requerido"] else "❌"
                if datos["actual"] < datos["requerido"]: completo = False
                msg += f"{puesto}: {datos['actual']} / {datos['requerido']} {estado}\n"
            msg += f"\nOperación: {'🟢 Estable' if completo else '🔴 Con riesgo'}"
            messagebox.showinfo("Reporte", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def borrar_empleado(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "⚠️ Seleccione un empleado")
            return
        item = self.tree.item(selected[0])
        persona_id = item['values'][0]
        nombre = item['values'][1]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar permanentemente a {nombre}?"):
            return
        try:
            conn = db_manager.get_connection()
            conn.execute("DELETE FROM registros WHERE persona_id = ?", (persona_id,))
            conn.execute("DELETE FROM personas WHERE id = ?", (persona_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"✅ {nombre} eliminado del sistema")
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo borrar: {e}")
