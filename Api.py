from flask import *
from models.User import User
from flask_hashing import Hashing
from bson.json_util import loads, dumps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from datetime import datetime  
from datetime import timedelta 
from ast import literal_eval 
from flask_mail import *
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
        msg = Message("Hello",
                  sender='proyectofinalmail@gmail.com',
                  recipients=["mediadocena13@gmail.com"])#CORREO DE PRUEBA CAMBIAR POR VARIABLE MAIL
        mail.send(msg)
        return 'Response: '+ user.saveToDB()
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
        user = User()
        res = user.Update(iden,name,password,mail,rol)
        return res
    #DELETE
    elif request.method == 'DELETE':
        user = User()
        res = user.Delete(escape(ident))
        return res
    else:
        return '{"status":404 ,"error":"Method Not Found"}'
        
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
        h = literal_eval(h)
        _id = h['_id']
        name = h['name']
        mail = h['mail']
        rol = h['rol']
        return jsonify(
            access_token=access_token,_id=_id,name=name,mail=mail,
            rol=rol,exp=date.strftime("%m/%d/%Y, %H:%M:%S")), 200

@app.route('/upload', methods=['POST'])
def Upload():
    if request.method == 'POST':
        try:
            f = request.files['file']
            name = request.form['name']
            if '.png' in f.filename:
                ext = '.png'
            elif '.jpg' in f.filename:
                ext = '.jpg'
            elif '.jpeg' in f.filename:
                ext = '.jpeg'
            elif '.mp3' in f.filename:
                ext = '.mp3'  
            print(name+ext)
            f.save('./public/files/' + name+ext)
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '{"status" : 500 , "error":"Upload error"}'
    return '{"status":200}'
    
@app.route('/download/<name>',methods=['GET'])
def download(name):
    if request.method == 'GET':
        print(escape(name))
        return send_file('public/files/'+escape(name), mimetype='image')

#Run app
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(debug=True)