from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy(app)

class Cirugia(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key= True)
    titulo = db.Column(db.String(150))
    estado = db.Column(db.Boolean)


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    lista_cirugias = Cirugia.query.all()
    return render_template("home.html", cirugias=lista_cirugias)

@app.route("/add", methods=['POST'])
def add():
    lista_cirugias = Cirugia.query.all()
    titulo = request.form.get('titulo')
    if titulo.strip() == '':
        mensaje='Error no ha ingresado prioridad'
        return render_template('home.html', cirugias=lista_cirugias, error=mensaje)

    new_cirugia= Cirugia(titulo=titulo, estado=False)
    db.session.add(new_cirugia)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/update/<int:cirugia_id>")
def update(cirugia_id):
    cirugia = Cirugia.query.filter_by(id=cirugia_id).first()
    cirugia.estado = not cirugia.estado
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/delete/<int:cirugia_id>")
def delete(cirugia_id):
    cirugia = Cirugia.query.filter_by(id=cirugia_id).first()
    db.session.delete(cirugia)
    db.session.commit()
    return redirect(url_for('home'))

if __name__== "__main__":
    app.run(debug=True)