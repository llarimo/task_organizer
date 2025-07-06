from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

#I TÁ RESTFUL TÁ SO PRA VCS MORREREM DE INVEJA

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tarefas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(500))
    prioridade = db.Column(db.String(20), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    concluida = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "prioridade": self.prioridade,
            "categoria": self.categoria,
            "concluida": self.concluida
        }
    
with app.app_context():
    db.create_all()


@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    prioridade = request.args.get("prioridade")
    categoria = request.args.get("categoria")

    query = Tarefa.query
    if prioridade:
        query = query.filter_by(prioridade=prioridade.lower())
    if categoria:
        query = query.filter(Tarefa.categoria.ilike(f"%{categoria}%"))
    tarefas = query.all()
    return jsonify([t.to_dict() for t in tarefas]), 200

@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    for campo in ["nome", "descricao", "prioridade", "categoria"]:
        if campo not in dados:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400

    tarefa = Tarefa(
        nome=dados["nome"],
        descricao=dados["descricao"],
        prioridade=dados["prioridade"].lower(),
        categoria=dados["categoria"].lower()
    )
    db.session.add(tarefa)
    db.session.commit()
    return jsonify(tarefa.to_dict()), 201

@app.route("/tarefas/<int:id>/concluir", methods=["PUT"])
def concluir_tarefa(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada"}), 404
    tarefa.concluida = True
    db.session.commit()
    return jsonify(tarefa.to_dict()), 200

@app.route("/tarefas/<int:id>", methods=["GET"])
def obter_tarefa(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada"}), 404
    return jsonify(tarefa.to_dict()), 200

@app.route("/tarefas/<int:id>", methods=["DELETE"])
def deletar_tarefa(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada"}), 404
    db.session.delete(tarefa)
    db.session.commit()
    return jsonify({"msg": "Tarefa deletada"}), 200


@app.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada"}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    for campo in ["nome", "descricao", "prioridade", "categoria", "concluida"]:
        if campo in dados:
            setattr(tarefa, campo, dados[campo])

    db.session.commit()
    return jsonify(tarefa.to_dict()), 200

if __name__ == "__main__":
    app.run(debug=True)