from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import check_password_hash,generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(app)

login_manager_app = LoginManager(app)

class Cirugia(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key= True)
    titulo = db.Column(db.String(150))
    estado = db.Column(db.Boolean, default=False)
    idusuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Foreign key para relacionar con el user

class Usuario(db.Model,UserMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key = True)
    nombreusuario =db.Column(db.String(100))
    contrasenia =db.Column(db.String(100))
    nombrecompleto =db.Column(db.String(100))
    cirugias = db.relationship('Cirugia', backref='Usuario', lazy=True)  # Relationship para ver todos

    def __init__(self, nombreusuario, contrasenia, nombrecompleto="") -> None:
        self.nombreusuario = nombreusuario
        self.contrasenia = generate_password_hash(contrasenia)
        self.nombrecompleto = nombrecompleto

    @classmethod
    def check_password(self, hashed_password, contrasenia):
        return check_password_hash(hashed_password, contrasenia)


with app.app_context():
    db.create_all()
    administrador = Usuario.query.filter_by(nombreusuario="admin@admin.com").first()
    if not administrador:
        print("Administrador no encontrado, creando administrador...")
        administrador = Usuario(nombreusuario="admin@admin.com", contrasenia="admin2025", nombrecompleto="Nicole Garzón")
        db.session.add(administrador)
        db.session.commit()
        print("Administrador creado: nombre usuario='admin@admin.com', contrasenia='admin2025'")




@login_manager_app.user_loader
def load_user(idusuario):
    return Usuario.query.get(int(idusuario))


@app.route("/add", methods=['POST'])
@login_required
def add():
    lista_cirugias = Cirugia.query.filter_by(idusuario=current_user.id).all()
    titulo = request.form.get('titulo')
    if titulo.strip() == '':
        mensaje='Error no ha ingresado prioridad'
        return render_template('home.html', cirugias=lista_cirugias, error=mensaje, nombreusuario= current_user)

    new_cirugia= Cirugia(titulo=titulo, idusuario=current_user.id)
    db.session.add(new_cirugia)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/update/<int:cirugia_id>")
@login_required
def update(cirugia_id):
    cirugia = Cirugia.query.filter_by(id=cirugia_id).first()
    cirugia.estado = not cirugia.estado
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/delete/<int:cirugia_id>")
@login_required
def delete(cirugia_id):
    cirugia = Cirugia.query.filter_by(id=cirugia_id).first()
    db.session.delete(cirugia)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/")
@login_required
def home():
    lista_cirugias = Cirugia.query.filter_by(idusuario=current_user.id).all()  # Get only the current user's todos
    return render_template('home.html', cirugias=lista_cirugias, nombreusuario= current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    acceso = None
    if request.method == 'POST':
        nombreusuario=(request.form['usuario'])
        contrasenia=(request.form['contrasenia'])
        usuario = Usuario.query.filter_by(nombreusuario=nombreusuario).first()
        if usuario and Usuario.check_password(usuario.contrasenia, contrasenia):
            login_user(usuario)
            acceso=True
            return redirect(url_for('home'))
        else:
            acceso=False 
    return render_template('login.html', sesion_iniciada=acceso)


@app.route("/logout")
def logout():
    nombreusuario = current_user.nombrecompleto  # Guarda el nombre completo del usuario antes de cerrar la sesión
    logout_user()  # Cierra la sesión del usuario actual
    return render_template('logout.html', nombrecompleto= nombreusuario)  # Pasa el nombre del usuario a la plantilla



def status_401(error):
    return redirect(url_for("login"))

def status_404(error):
    return render_template("error404.html")

if __name__== "__main__":
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True, port=5001)