# ==========================
# forms.py
# ==========================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


# ---------------------- FORMULARIO REGISTRO ----------------------
class RegisterForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(1,150)])
    email = StringField('Correo', validators=[DataRequired(), Email(), Length(1,150)])
    phone = StringField(
        'Número de celular',
        validators=[
            DataRequired(),
            Regexp(r'^[0-9]{10}$', message="Debe ser un número válido de 10 dígitos.")
        ]
    )
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(6,128)])
    submit = SubmitField('Registrar')


# ---------------------- LOGIN ----------------------
class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')


# ---------------------- EJERCICIO ----------------------
class ExerciseForm(FlaskForm):
    nombre = StringField('Ejercicio', validators=[DataRequired(), Length(1,150)])
    series = IntegerField('Series', validators=[Optional()])
    repeticiones = StringField('Repeticiones', validators=[Optional(), Length(0,50)])
    peso = StringField('Peso', validators=[Optional(), Length(0,50)])
    dia = StringField('Día', validators=[Optional(), Length(0,30)])
    notas = TextAreaField('Notas', validators=[Optional(), Length(0,500)])


# ---------------------- RUTINA EDIT SIMPLE ----------------------
class RoutineForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(1,120)])
    descripcion = TextAreaField('Descripción general', validators=[Optional(), Length(0,2000)])
    submit = SubmitField('Guardar rutina')


# ---------------------- RUTINA + EJERCICIOS ----------------------
class RoutineWithExercisesForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(1,120)])
    descripcion = TextAreaField('Descripción general', validators=[Optional(), Length(0,2000)])
    submit = SubmitField('Guardar rutina y ejercicios')
