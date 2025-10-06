from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

# Conexión segura a MySQL
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="13921693LB",  # tu contraseña
            database="sistema_clinica"
        )
        return conn
    except Error as e:
        print("Error al conectar con MySQL:", e)
        return None
# ==========================
# CRUD DE USUARIOS (solo ADMIN)
# ==========================

@app.route("/usuarios")
def listar_usuarios():
    if "rol" not in session or session["rol"] != "administrador":
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/usuarios/lista.html", usuarios=usuarios)

@app.route("/usuarios/agregar", methods=["GET", "POST"])
def agregar_usuario():
    if "rol" not in session or session["rol"] != "administrador":
        return redirect(url_for("login"))
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        rol = request.form["rol"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (%s,%s,%s)", (usuario, password, rol))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Usuario agregado correctamente")
        return redirect(url_for("listar_usuarios"))
    return render_template("admin/usuarios/formulario.html", usuario=None)

@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    if "rol" not in session or session["rol"] != "administrador":
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id=%s", (id,))
    usuario = cursor.fetchone()
    if request.method == "POST":
        usuario_nuevo = request.form["usuario"]
        password = request.form["password"]
        rol = request.form["rol"]

        cursor.execute("""
            UPDATE usuarios SET usuario=%s, password=%s, rol=%s WHERE id=%s
        """, (usuario_nuevo, password, rol, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Usuario actualizado correctamente")
        return redirect(url_for("listar_usuarios"))
    cursor.close()
    conn.close()
    return render_template("admin/usuarios/formulario.html", usuario=usuario)

@app.route("/usuarios/eliminar/<int:id>")
def eliminar_usuario(id):
    if "rol" not in session or session["rol"] != "administrador":
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Usuario eliminado correctamente")
    return redirect(url_for("listar_usuarios"))


# Login
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        if not usuario or not password:
            error = "Por favor ingrese usuario y contraseña"
        else:
            conn = get_db_connection()
            if conn is None:
                error = "No se pudo conectar a la base de datos"
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s",
                               (usuario, password))
                user = cursor.fetchone()
                cursor.close()
                conn.close()

                if user:
                    session["usuario"] = user["usuario"]
                    session["rol"] = user["rol"]
                    if user["rol"] == "administrador":
                        return redirect(url_for("panel_admin"))
                    elif user["rol"] == "doctor":
                        return redirect(url_for("panel_doctor"))
                    elif user["rol"] == "enfermero":
                        return redirect(url_for("panel_enfermero"))
                else:
                    error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)

# Paneles por rol
@app.route("/panel/admin")
def panel_admin():
    if "rol" in session and session["rol"] == "administrador":
        return render_template("admin/panel_admin.html")
    return redirect(url_for("login"))

@app.route("/panel/doctor")
def panel_doctor():
    if "rol" in session and session["rol"] == "doctor":
        return render_template("doctor/panel_doctor.html")
    return redirect(url_for("login"))

@app.route("/panel/enfermero")
def panel_enfermero():
    if "rol" in session and session["rol"] == "enfermero":
        return render_template("enfermero/panel_enfermero.html")
    return redirect(url_for("login"))

# Cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Listar pacientes
@app.route("/pacientes")
def listar_pacientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("enfermero/pacientes/lista.html", pacientes=pacientes)

# Agregar paciente
@app.route("/pacientes/agregar", methods=["GET", "POST"])
def agregar_paciente():
    if request.method == "POST":
        data = (
            request.form["nombre"],
            request.form["apellido_paterno"],
            request.form["apellido_materno"],
            request.form["ci"],
            request.form["fecha_nacimiento"],
            request.form["edad"],
            request.form["genero"],
            request.form["telefono"]
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pacientes
            (nombre, apellido_paterno, apellido_materno, ci, fecha_nacimiento, edad, genero, telefono)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)
        conn.commit()
        cursor.close()
        conn.close()
        flash("Paciente agregado correctamente")
        return redirect(url_for("listar_pacientes"))
    return render_template("enfermero/pacientes/formulario.html", paciente=None)

# Editar paciente
@app.route("/pacientes/editar/<int:id>", methods=["GET", "POST"])
def editar_paciente(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pacientes WHERE id=%s", (id,))
    paciente = cursor.fetchone()
    if request.method == "POST":
        data = (
            request.form["nombre"],
            request.form["apellido_paterno"],
            request.form["apellido_materno"],
            request.form["ci"],
            request.form["fecha_nacimiento"],
            request.form["edad"],
            request.form["genero"],
            request.form["telefono"],
            id
        )
        cursor.execute("""
            UPDATE pacientes
            SET nombre=%s, apellido_paterno=%s, apellido_materno=%s, ci=%s,
                fecha_nacimiento=%s, edad=%s, genero=%s, telefono=%s
            WHERE id=%s
        """, data)
        conn.commit()
        cursor.close()
        conn.close()
        flash("Paciente actualizado correctamente")
        return redirect(url_for("listar_pacientes"))
    cursor.close()
    conn.close()
    return render_template("enfermero/pacientes/formulario.html", paciente=paciente)

# Eliminar paciente
@app.route("/pacientes/eliminar/<int:id>")
def eliminar_paciente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pacientes WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Paciente eliminado correctamente")
    return redirect(url_for("listar_pacientes"))

if __name__ == "__main__":
    app.run(debug=True)