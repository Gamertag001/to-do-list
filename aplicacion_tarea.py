import tkinter as tk
from tkinter import messagebox
import mysql.connector
from tkcalendar import DateEntry

#--------- CONEXIÓN MYSQL ------------
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="lista_tareas"
    )

#------- Pestaña de registro ------------
def ventana_registrarse():

    def guardar_usuario():
        usuario = entry_usuario.get()
        contraseña = entry_contraseña.get()
        
        if not usuario or not contraseña:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los datos")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            sql = "INSERT INTO personas(nombre, contraseña) VALUES (%s, %s)"
            valores = (usuario, contraseña)
            cursor.execute(sql, valores)
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Datos guardados correctamente")
            reg_win.destroy()
            ventana_logearse()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar en la base de datos\n{e}")

    reg_win = tk.Toplevel(ventana)
    reg_win.title("Registro")
    reg_win.geometry("500x450")

    tk.Label(reg_win, text="Usuario: ").pack(pady=5)
    entry_usuario = tk.Entry(reg_win)
    entry_usuario.pack(pady=5)

    tk.Label(reg_win, text="Contraseña: ").pack(pady=5)
    entry_contraseña = tk.Entry(reg_win, show="*")
    entry_contraseña.pack(pady=5)

    tk.Button(reg_win, text="Registrar", command=guardar_usuario, bg="green", fg="white").pack(pady=20)


#------- Pestaña login ------------
def ventana_logearse():

    def validar_datos():
        usuario = entry_usuario.get()
        contraseña = entry_contraseña.get()

        if not usuario or not contraseña:
            messagebox.showwarning("Campos vacíos", "Por favor completar todos los datos")
            return
        
        try:
            conn = conectar()
            cursor = conn.cursor()
            sql = "SELECT * FROM personas WHERE nombre = %s AND contraseña = %s"
            valores = (usuario, contraseña)
            cursor.execute(sql, valores)
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                messagebox.showinfo("Éxito", f"Bienvenido {usuario}")
                log_win.destroy()
                ventana_tareas(usuario)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema: {e}")

    log_win = tk.Toplevel(ventana)
    log_win.title("Login")
    log_win.geometry("500x450")

    tk.Label(log_win, text="Usuario: ").pack(pady=5)
    entry_usuario = tk.Entry(log_win)
    entry_usuario.pack(pady=5)

    tk.Label(log_win, text="Contraseña").pack(pady=5)
    entry_contraseña = tk.Entry(log_win, show="*")
    entry_contraseña.pack(pady=5)

    tk.Button(log_win, text="Ingresar", command=validar_datos, bg="blue", fg="white").pack(pady=20)


#-------- ventana de tareas ------
def ventana_tareas(usuario):

    # Obtener el ID del usuario
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM personas WHERE nombre = %s", (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            usuario_id = resultado[0]
        else:
            messagebox.showerror("Error", "Usuario no encontrado en la base de datos")
            return
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar para obtener el ID del usuario\n{e}")
        return

    #----- agregar tareas ----
    def agregar_tareas():
        tarea = entry_tareas.get()
        descripcion = entry_descripcion.get()
        inicio = fecha_inicio.get_date()
        final = fecha_fin.get_date()

        if not tarea or not descripcion or not inicio or not final:
            messagebox.showwarning("Campos vacíos", "Por favor completar todos los campos")
            return
        
        try:
            conn = conectar()
            cursor = conn.cursor()
            sql = """INSERT INTO tareas 
                     (nombre_tarea, descripcion_tarea, fecha_inicio, fecha_final, id) 
                     VALUES (%s, %s, %s, %s, %s)"""
            valores = (tarea, descripcion, inicio, final, usuario_id)
            cursor.execute(sql, valores)
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Tarea guardada con éxito")
            entry_tareas.delete(0, tk.END)
            entry_descripcion.delete(0, tk.END)
            consultar_datos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar en la base de datos\n{e}")

    def consultar_datos():
        try:
            conn = conectar()
            cursor = conn.cursor()
            sql = """SELECT id_tarea, nombre_tarea, descripcion_tarea, fecha_inicio, fecha_final 
                     FROM tareas WHERE id = %s"""
            cursor.execute(sql, (usuario_id,))
            resultados = cursor.fetchall()
            conn.close()

            lista_tareas.delete(0, tk.END)

            for fila in resultados:
                id_tarea, nombre_tarea, descripcion_tarea, fecha_inicio_tarea, fecha_final_tarea = fila
                lista_tareas.insert(
                    tk.END,
                    f"Id:{id_tarea} | {nombre_tarea} - {descripcion_tarea} | Inicio:{fecha_inicio_tarea} | Fin:{fecha_final_tarea}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo consultar en la base de datos\n{e}")
    
    def eliminar_tarea():
        seleccion_idx = lista_tareas.curselection()
        if not seleccion_idx:
            messagebox.showwarning("Advertencia", "Selecciona una tarea para eliminar.")
            return
        
        seleccion = lista_tareas.get(seleccion_idx)
        id_tarea = seleccion.split("|")[0].replace("Id:", "").strip()

        confirmacion = messagebox.askyesno("Confirmar", f"¿Eliminar la tarea con ID '{id_tarea}'?")
        if not confirmacion:
            return
        
        try:
            conn = conectar()
            cursor = conn.cursor()
            query = "DELETE FROM tareas WHERE id_tarea = %s"
            cursor.execute(query, (id_tarea,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", f"Tarea con ID '{id_tarea}' eliminada correctamente.")
            consultar_datos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la tarea:\n{e}")

    def completar_tarea():
        seleccion_idx = lista_tareas.curselection()
        if not seleccion_idx:
            messagebox.showwarning("Selección vacía", "Por favor seleccione una tarea.")
            return

        seleccion = lista_tareas.get(seleccion_idx)
        id_tarea = seleccion.split("|")[0].replace("Id:", "").strip()

        try:
            conn = conectar()
            cursor = conn.cursor()
            sql = "UPDATE tareas SET descripcion_tarea = CONCAT('✔️ ', descripcion_tarea) WHERE id_tarea = %s"
            cursor.execute(sql, (id_tarea,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Tarea marcada como completada.")
            consultar_datos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo marcar como completada:\n{e}")

    # ----- Ventana tareas -----
    tareas_win = tk.Toplevel(ventana)
    tareas_win.title("Mis tareas")
    tareas_win.geometry("850x870")

    tk.Label(tareas_win, text=f"Bienvenido, {usuario}").pack(pady=10)

    tk.Label(tareas_win, text="Escribir tarea:").pack(pady=5)
    entry_tareas = tk.Entry(tareas_win, width=40)
    entry_tareas.pack(pady=5)

    tk.Label(tareas_win, text="Descripción: ").pack(pady=5)
    entry_descripcion = tk.Entry(tareas_win, width=40)
    entry_descripcion.pack(pady=5)

    tk.Label(tareas_win, text="Fecha de inicio").pack(pady=5)
    fecha_inicio = DateEntry(tareas_win, date_pattern="yyyy-mm-dd")
    fecha_inicio.pack(pady=5)

    tk.Label(tareas_win, text="Fecha final").pack(pady=5)
    fecha_fin = DateEntry(tareas_win, date_pattern="yyyy-mm-dd")
    fecha_fin.pack(pady=5)

    tk.Button(tareas_win, text="Agregar tarea", command=agregar_tareas, bg="blue", fg="white").pack(pady=10)
    tk.Button(tareas_win, text="Consultar tareas", command=consultar_datos, bg="purple", fg="white").pack(pady=10)

    tk.Label(tareas_win, text="Tareas registradas").pack(pady=5)
    lista_tareas = tk.Listbox(tareas_win, width=100, height=15)
    lista_tareas.pack(pady=15)

    tk.Button(tareas_win, text="Eliminar tarea", command=eliminar_tarea, bg="red", fg="white").pack(pady=5)
    tk.Button(tareas_win, text="Marcar como completada", command=completar_tarea, bg="green", fg="white").pack(pady=5)


# ------- Ventana principal -------
ventana = tk.Tk()
ventana.title("Sesión de registro")
ventana.geometry("300x150")

tk.Label(ventana, text="¿Eres nuevo?").pack(pady=5)
tk.Button(ventana, text="Sí", command=ventana_registrarse, bg="green", fg="white").pack(pady=10)
tk.Button(ventana, text="No", command=ventana_logearse, bg="blue", fg="white").pack(pady=5)

ventana.mainloop()
