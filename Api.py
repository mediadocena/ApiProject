from flask import *
from models.User import User
from flask_hashing import Hashing
from bson.json_util import loads, dumps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity,create_refresh_token
)
from datetime import datetime  
from datetime import timedelta 
from ast import literal_eval 
from flask_mail import *
from models.Portfolio import Portfolio
import sys

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='proyectofinalmail@gmail.com',
    MAIL_PASSWORD='tujbjlnapolrwqad'
)
hashing = Hashing(app)
# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'jwtls132526nbcs44465873nasl'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 864000
jwt = JWTManager(app)

#Error Handler
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"msg": "Not Found"}), 404

@app.route('/Main')
def main():
    return render_template('MainTemplate.html')
#Endpoints and Methods
"""
@app.route("/")
def redirect():
    return main()
@app.route("/prueba")
def prueba():
    return '<h1>Prueba</h1>'
"""
#Generar nuevos token
@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def Refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200
#Usuarios
@app.route('/user' ,methods=['POST','GET','PUT'])
@app.route('/user/<ident>',methods=['DELETE'])
@jwt_required
def user(ident=''):
    current_user = get_jwt_identity()
    if current_user is None:
        return jsonify({"msg": "Missing token"}), 400
    #POST
    if request.method == 'POST':
        mail = Mail(app)
        mai = request.json['mail']
        password = hashing.hash_value(request.json['password'], salt='abcd')
        user = User(request.json['username'],password,mai,request.json['rol'])
        if user.existsMail is True:
            msg = Message(subject="Confirmación de cuenta",
                    body='Gracias por registrarte en la página, para completar tu cuenta, pincha en el enlace:<a href="localhost:4200/Confirm/'+mai+'">Confirmar</a>',
                    sender='proyectofinalmail@gmail.com',
                    recipients=[mai])
            mail.send(msg)
            return 'Response: '+ user.saveToDB()
        else:
            return jsonify({"msg": "Mail already exists"}), 400
    #GET
    elif request.method == 'GET':
        user = User()
        res = user.getAll()
        return res
    #PUT
    elif request.method == 'PUT':
        name = request.json['name']
        password = request.json['password']
        mail = request.json['mail']
        rol = request.json['rol']
        iden = request.json['_id']
        icon = request.json['icon']
        user = User()
        res = user.Update(iden,name,password,mail,rol,icon)
        return res
    #DELETE
    elif request.method == 'DELETE':
        user = User()
        res = user.Delete(escape(ident))
        return res
    else:
        return jsonify({"error":"Method Not Found"}), 404
        
#LOGIN
@app.route('/login' ,methods=['POST'])
def login():
    #Si no hay documento JSON:
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    username = request.json['mail']
    password = request.json['password']
    #Si no hay usuario/contraseña:
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    
    password = hashing.hash_value(password, salt ='abcd')
    h = User().findLogin(username,password)
    if h == False:
        return jsonify({"msg": "Bad username or password"}), 401
    else: 
        date = datetime.now()
        date = date + timedelta(seconds=864000)
        # Identity can be any data that is json serializable
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        h = literal_eval(h)
        _id = h['_id']
        name = h['name']
        mail = h['mail']
        rol = h['rol']
        verified = h['verified']
        icon = ''
        if 'icon' in h:
            icon = h['icon']
        return jsonify(
            access_token=access_token,refresh_token=refresh_token,_id=_id,name=name,mail=mail,
            rol=rol,icon=icon,exp=date.strftime("%m/%d/%Y, %H:%M:%S")), 200

@app.route('/upload', methods=['POST'])
def Upload():
    if request.method == 'POST':
        f = ''
        try:
            f = request.files['file']
            if '.png' in f.filename:
                ext = '.png'
            elif '.jpg' in f.filename:
                ext = '.jpg'
            elif '.jpeg' in f.filename:
                ext = '.jpeg'
            elif '.mp3' in f.filename:
                ext = '.mp3'  
            f.save('./public/files/' + f.filename + ext)
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '{"status" : 500 , "error":"Upload error"}'
    return 'http://127.0.0.1:5000/download/'+f.filename
    
@app.route('/download/<name>',methods=['GET'])
def download(name):
    if request.method == 'GET':
        print(escape(name))
        return send_file('public/files/'+escape(name), mimetype='image')

@app.route('/portfolio',methods=['POST','PUT','GET'])
@app.route('/portfolio/<iden>',methods=['DELETE'])
@jwt_required
def portfolio(iden=''):
    port = Portfolio()
    if request.method == 'GET':
        return port.GetAll()
    elif request.method == 'POST':
        filename = Upload()
        port = Portfolio(request.form['titulo'],filename,request.form['text'],request.form['author'])
        return port.Post()
    elif request.method == 'PUT':
        return port.Update(request.json['id'],request.json['titulo'],request.json['file'],request.json['titulo'],request.json['text'],request.json['author'],request.json['coments'],request.json['points'])
    elif request.method == 'DELETE':
        return port.Delete(escape(iden))
    return jsonify({"msg":"Route Not Found"},400)

#Run app
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(debug=True)