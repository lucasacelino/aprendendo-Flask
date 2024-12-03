from flask import request, jsonify
import sqlite3
from helpers.application import app
from helpers.database import getConnect
from models.Propriedade import Propriedade


@app.route("/")
def home():
    aplicacao = {'versao': '1.0'}
    return jsonify(aplicacao), 200


@app.get("/propriedades/")
def listarPropriedadesFiltro():
    nome = request.args.get('nome')
    cidade = request.args.get('cidade')
    try:
        connection = getConnect()
        
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM tb_propriedades WHERE nome LIKE ? OR cidade LIKE ?', (nome, cidade))
        res = cursor.fetchall()
        propriedades = []
        for i in res:
            pr = {'id': i[0], 'nome': i[1], 'cidade': i[2]}
            propriedades.append(pr)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(propriedades)

            
@app.get("/propriedades")
def listarTodasPropriedades():
    try:
        connection = getConnect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tb_propriedades")
        resultSet = cursor.fetchall()
        propriedades = []
        for props in resultSet:
            id = props[0]
            nome = props[1]
            cidade = props[2]
            propriedade = Propriedade(id, nome, cidade)
            propriedades.append(propriedade.toJson())
        # propriedades = [dict(row) for row in resultSet]
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(propriedades), 200


@app.post("/propriedades")
def criarPropriedade():
    try:
        propriedadeNova = request.json
        connection = getConnect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO tb_propriedades(nome, cidade) VALUES(?, ?)", (propriedadeNova['nome'], propriedadeNova['cidade']))
        connection.commit()
        id = cursor.lastrowid
        propriedadeNova['id'] = id
    except sqlite3.Error as e:
        return jsonify({'erro': str(e)}), 500
    return jsonify(propriedadeNova), 201


def getPropriedadeId(idProp):
    try:        
        connection = getConnect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tb_propriedades WHERE id = ?", (idProp, ))
        resultSet = cursor.fetchone()
    finally:
        connection.close()
    return resultSet
    
    
@app.get("/propriedades/<int:idPropriedade>")
def dadosPropriedadesPorId(idPropriedade):
    try:
        connection = getConnect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tb_propriedades WHERE id = ?", (idPropriedade, ))
        resultSet = cursor.fetchone()
        if(resultSet is not None):
            propriedade = {'id': resultSet[0], 'nome': resultSet[1], 'cidade': resultSet[2]}
        else:
            return jsonify({'mensagem': 'propriedade não encontrada'}), 400
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(propriedade)


@app.delete("/propriedades/<int:idPropriedade>")
def deletarPropriedadePorId(idPropriedade):
    try:
        connection = getConnect()
        cursor = connection.cursor()
        resultSet = getPropriedadeId(idPropriedade)
        if(resultSet is None):
            return jsonify({'mensagem': 'Propriedade não encontrada'})
        cursor.execute("DELETE FROM tb_propriedades WHERE id = ?", (idPropriedade, ))
        connection.commit()
        return jsonify({'mensagem': 'Dado deletado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500


@app.put("/propriedades/<int:idPropriedade>")
def atualizarDadosPropriedade(idPropriedade):
    propriedadeAtualizada = request.json
    try:
        connection = getConnect()
        cursor = connection.cursor()
        resultSet = getPropriedadeId(idPropriedade)
        if(resultSet is None):
            return jsonify({'mensagem': 'Não é possível atualizar uma propriedade que não existe'})
        cursor.execute("UPDATE tb_propriedades SET nome = ?, cidade = ? WHERE id = ?", (propriedadeAtualizada['nome'], propriedadeAtualizada['cidade'], idPropriedade))
        connection.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(propriedadeAtualizada), 200


if __name__ == "__main__":
    app.run(debug=True)
