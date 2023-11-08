from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "12345678"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:12345678@localhost/aula_13_10"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Setor(db.Model):
    __tablename__ = "setor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name) -> None:
        self.name = name

class Cargo(db.Model):
    __tablename__ = "cargo"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    setor_name = db.Column(db.String(100), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey("setor.id"), nullable=False)

    setor = db.relationship("Setor", backref=db.backref("cargos"))

class Funcionarios(db.Model):
    __tablename__ = 'funcionarios'

    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    data_admissao = db.Column(db.Date, nullable=False)
    status_funcionario = db.Column(db.Boolean, nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey("setor.id"))
    cargo_id = db.Column(db.Integer, db.ForeignKey("cargo.id"))

    setor = db.relationship("Setor")
    cargo = db.relationship("Cargo")

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    setor = Setor.query.order_by(Setor.id).all()
    cargo = Cargo.query.order_by(Cargo.id).all()
    return render_template("index.html", setor=setor, cargo=cargo)

@app.route("/insert_setor", methods=["POST"])
def insert_setor():
    if request.method == "POST":
        name = request.form["nome"]
        if Setor.query.filter_by(name=name).first() is None:
            db.session.add(Setor(name=name))
            db.session.commit()
        else:
            flash("ERRO")
        return redirect(url_for("index"))


@app.route("/delete_setor/<id>", methods=["GET", "POST"])
def delete_setor(id):
    id = Setor.query.get(id)
    db.session.delete(id)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/insert_cargo", methods=["POST", "GET"])
def insert_cargo():
    name = request.form["nome"]
    setor_nome = request.form["setor_name"]
    setor = Setor.query.filter_by(name=setor_nome).first()
    existing_cargo = Cargo.query.filter_by(name=name, setor_id=setor.id).first()
    if existing_cargo is None:
        db.session.add(Cargo(name=name, setor_name=setor_nome, setor_id=setor.id))
        db.session.commit()
        return redirect(url_for("index"))
    else:
        flash("ERRO")
        return redirect(url_for("index"))


@app.route("/delete_cargo/<id>", methods=["GET", "POST"])
def delete_cargo(id):
    id = Cargo.query.get(id)
    db.session.delete(id)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/cadastro_funcionario", methods=["GET", "POST"])
def cadastro_funcionario():
    if request.method == "POST":
        
        primeiro_nome = request.form["primeiro_nome"]
        sobrenome = request.form["sobrenome"]
        data_admissao = request.form["data_admissao"]
        status_funcionario = bool(int(request.form["status_funcionario"]))
        setor_id = int(request.form["setor"])
        cargo_id = int(request.form["cargo"])

        funcionario = Funcionarios(primeiro_nome=primeiro_nome, sobrenome=sobrenome,
                                   data_admissao=data_admissao, status_funcionario=status_funcionario,
                                   setor_id=setor_id, cargo_id=cargo_id)

        db.session.add(funcionario)
        db.session.commit()

        flash("Funcionário cadastrado com sucesso!")

    setores = Setor.query.all()
    cargos = Cargo.query.all()

    return render_template("cadastro_funcionario.html", setores=setores, cargos=cargos)

@app.route("/funcionarios")
def lista_funcionarios():
    funcionarios = Funcionarios.query.all()
    return render_template("lista_funcionarios.html", funcionarios=funcionarios)


if __name__ == "__main__":
    app.run(debug=True)
