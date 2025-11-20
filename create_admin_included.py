from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    db.create_all()

    email = "andresherrera0893@gmail.com"

    if not User.query.filter_by(email=email).first():
        u = User(nombre="Andres Herrera", email=email, role='admin')
        u.password = "24deagosto"
        db.session.add(u)
        db.session.commit()
        print("Admin creado:", email)
    else:
        print("Admin ya existe:", email)
