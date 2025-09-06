from flask import Blueprint, flash, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username and password:
            session["user_id"] = 1
            session["username"] = username
            flash(f"¡Bienvenido {username}!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Por favor ingresa usuario y contraseña.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return render_template("auth/register.html")


@auth_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Datos del usuario para el template
    usuario = {
        "username": session.get("username", "Usuario"),
        "nombre_completo": session.get("username", "Usuario Ejemplo"),
        "email": f"{session.get('username', 'usuario')}@ministerio.org",
        "rol": "Administrador",
        "fecha_registro": "2024-01-01",
        "ultimo_acceso": "2025-06-10",
    }

    # Stats completas que el template puede necesitar
    stats = {
        "total_tableros": 3,
        "total_listas": 12,
        "total_personas": 25,
        "total_tarjetas": 67,  # Esta era la que faltaba
        "tableros_activos": 2,
        "tareas_pendientes": 8,
        "tareas_completadas": 45,
        "miembros_activos": 15,
        "proyectos_completados": 23,
    }

    return render_template("auth/profile.html", usuario=usuario, stats=stats)
