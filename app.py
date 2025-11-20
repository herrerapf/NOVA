import os
import json
from datetime import datetime, date
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash

from models import db, User, Routine, Exercise
from forms import RegisterForm, LoginForm, RoutineForm, ExerciseForm, RoutineWithExercisesForm


# -------------------------- APP FACTORY --------------------------
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nova-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # ------------------------ LOGIN MANAGER ------------------------
    login_manager = LoginManager()
    login_manager.login_view = 'index'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ------------------------ ADMIN REQUIRED ------------------------
    def admin_required(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin():
                abort(403)
            return f(*args, **kwargs)
        return decorated

    # ---------------------- CREATE TABLES + ADMIN ----------------------
    with app.app_context():
        db.create_all()

        admin_email = os.environ.get('ADMIN_EMAIL', 'andresnova@gmail.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', '123456')
        admin_nombre = os.environ.get('ADMIN_NOMBRE', 'Administrador')

        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin = User(nombre=admin_nombre, email=admin_email, role='admin')
            admin.password_hash = generate_password_hash(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin creado: {admin_email} / {admin_password}")

    # ---------------------- TEMPLATE FILTERS ----------------------
    @app.template_filter('nl2br')
    def nl2br(s):
        if s is None:
            return ''
        return s.replace('\n', '<br/>')


    # ================================================================
    #                           RUTAS PRINCIPALES
    # ================================================================

    # ---------------------- INDEX (LOGIN + REGISTRO) ----------------------
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard' if current_user.is_admin() else 'dashboard'))

        login_form = LoginForm(prefix="login")
        register_form = RegisterForm(prefix="register")

        if request.method == 'POST':
            form_type = request.form.get('form-type')

            # -------- LOGIN --------
            if form_type == 'login':
                email = request.form.get('email')
                password = request.form.get('password')
                user = User.query.filter_by(email=email).first()

                if user and user.check_password(password):
                    login_user(user)
                    flash('Inicio de sesión exitoso.', 'success')
                    return redirect(url_for('admin_dashboard' if user.is_admin() else 'dashboard'))
                else:
                    flash('Correo o contraseña incorrectos.', 'danger')

            # -------- REGISTRO --------
            elif form_type == 'register':
                nombre = request.form.get('nombre')
                email = request.form.get('email')
                phone = request.form.get('phone')
                password = request.form.get('password')

                if User.query.filter_by(email=email).first():
                    flash('El correo ya está registrado.', 'warning')
                else:
                    user = User(nombre=nombre, email=email, phone=phone)
                    user.password_hash = generate_password_hash(password)
                    db.session.add(user)
                    db.session.commit()
                    flash('Registro exitoso.', 'success')
                    return redirect(url_for('index'))

        return render_template('index.html', login_form=login_form, register_form=register_form)

    # ---------------------- LOGOUT ----------------------
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Sesión cerrada correctamente.', 'info')
        return redirect(url_for('index'))


    # ================================================================
    #                         DASHBOARD USUARIO
    # ================================================================
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        routines = Routine.query.filter_by(user_id=current_user.id).order_by(Routine.fecha_creacion.desc()).all()
        return render_template('user_dashboard.html', routines=routines)


    # ================================================================
    #                            ADMIN
    # ================================================================
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        users = User.query.filter(User.role != 'admin').order_by(User.created_at.desc()).all()
        return render_template('admin_dashboard.html', users=users)

    @app.route('/admin/user/<int:user_id>')
    @login_required
    @admin_required
    def admin_user_detail(user_id):
        user = User.query.get_or_404(user_id)
        routines = Routine.query.filter_by(user_id=user.id).order_by(Routine.fecha_creacion.desc()).all()
        days_remaining = user.days_remaining()
        return render_template('admin_user_detail.html',
                               user=user,
                               routines=routines,
                               days_remaining=days_remaining)

    # -------- ACTUALIZACIÓN DE SUSCRIPCIÓN --------
    @app.route('/admin/user/<int:user_id>/subscription', methods=['POST'])
    @login_required
    @admin_required
    def admin_user_update_subscription(user_id):
        user = User.query.get_or_404(user_id)

        fecha_str = request.form.get('fecha_pago')
        dias_str = request.form.get('dias')

        parsed_date, parsed_days = None, None

        if fecha_str:
            try:
                parsed_date = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except:
                pass

        if dias_str:
            try:
                parsed_days = int(dias_str)
            except:
                pass

        if parsed_date:
            user.subscription_date = parsed_date
        if parsed_days is not None:
            user.subscription_days = parsed_days

        try:
            db.session.commit()
            flash('Suscripción guardada correctamente.', 'success')
        except:
            db.session.rollback()
            flash('Error al guardar la suscripción.', 'danger')

        return redirect(url_for('admin_user_detail', user_id=user.id))


    # -------- ELIMINAR USUARIO --------
    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def admin_user_delete(user_id):
        user = User.query.get_or_404(user_id)

        if user.id == current_user.id:
            flash('No puedes eliminar tu propia cuenta.', 'warning')
            return redirect(url_for('admin_dashboard'))

        try:
            db.session.delete(user)
            db.session.commit()
            flash('Usuario eliminado correctamente.', 'info')
        except:
            db.session.rollback()
            flash('Error eliminando usuario.', 'danger')

        return redirect(url_for('admin_dashboard'))


    # ================================================================
    #                     RUTINAS (ADMIN)
    # ================================================================
    @app.route('/admin/user/<int:user_id>/routine/new', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_create_routine(user_id):
        user = User.query.get_or_404(user_id)
        days_remaining = user.days_remaining()

        if request.method == 'POST':
            if not days_remaining or days_remaining <= 0:
                flash('El usuario no tiene una suscripción activa.', 'warning')
                return redirect(url_for('admin_user_detail', user_id=user.id))

            titulo = request.form.get('titulo')
            descripcion = request.form.get('descripcion')
            exercises_payload = request.form.get('exercises')

            if not titulo:
                flash('El título es obligatorio.', 'warning')
                return redirect(url_for('admin_create_routine', user_id=user.id))

            r = Routine(titulo=titulo, descripcion=descripcion, user_id=user.id, creado_por=current_user.nombre)
            db.session.add(r)
            db.session.flush()

            if exercises_payload:
                try:
                    ex_list = json.loads(exercises_payload)
                    for ex in ex_list:
                        e = Exercise(
                            nombre=ex.get('nombre'),
                            series=int(ex.get('series')) if ex.get('series') else None,
                            repeticiones=ex.get('repeticiones'),
                            peso=ex.get('peso'),
                            dia=ex.get('dia'),
                            notas=ex.get('notas'),
                            rutina_id=r.id
                        )
                        db.session.add(e)
                except:
                    pass

            db.session.commit()
            flash('Rutina creada con éxito.', 'success')
            return redirect(url_for('admin_user_detail', user_id=user.id))

        form = RoutineWithExercisesForm()
        return render_template('admin_create_routine.html', user=user, form=form, days_remaining=days_remaining)


    # -------- EDITAR RUTINA --------
    @app.route('/admin/routine/<int:rid>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_edit_routine(rid):
        r = Routine.query.get_or_404(rid)
        form = RoutineForm(obj=r)

        if form.validate_on_submit():
            r.titulo = form.titulo.data
            r.descripcion = form.descripcion.data
            db.session.commit()
            flash('Rutina actualizada', 'success')
            return redirect(url_for('admin_user_detail', user_id=r.user_id))

        exercises = Exercise.query.filter_by(rutina_id=r.id).all()
        return render_template('admin_edit_routine.html', r=r, form=form, exercises=exercises)


    # -------- ELIMINAR RUTINA --------
    @app.route('/admin/routine/<int:rid>/delete', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_routine(rid):
        r = Routine.query.get_or_404(rid)
        user_id = r.user_id
        db.session.delete(r)
        db.session.commit()
        flash('Rutina eliminada', 'info')
        return redirect(url_for('admin_user_detail', user_id=user_id))


    # -------- ELIMINAR EJERCICIO --------
    @app.route('/admin/exercise/<int:eid>/delete', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_exercise(eid):
        e = Exercise.query.get_or_404(eid)
        db.session.delete(e)
        db.session.commit()
        return jsonify({'ok': True})


    # ================================================================
    #                    RUTINAS (USUARIO NORMAL)
    # ================================================================
    @app.route('/mis_rutinas')
    @login_required
    def mis_rutinas():
        routines = Routine.query.filter_by(user_id=current_user.id).order_by(Routine.fecha_creacion.desc()).all()
        return render_template('mis_rutinas.html', routines=routines)

    @app.route('/routine/<int:rid>')
    @login_required
    def view_routine(rid):
        r = Routine.query.get_or_404(rid)
        if r.user_id != current_user.id and not current_user.is_admin():
            abort(403)
        exercises = Exercise.query.filter_by(rutina_id=r.id).all()
        return render_template('view_routine.html', r=r, exercises=exercises)


    return app


# -------------------------- RUN --------------------------
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
