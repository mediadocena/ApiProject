from flask import *
from models.User import User
from flask_hashing import Hashing
from bson.json_util import loads, dumps
from flask_jwt_extended import *
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
blacklist = set()
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

# Endpoint for revoking the current users access token
@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200
@app.route('/Confirm/<_id>',methods=['GET'])
def Confirm(_id):
    return User().Confirm(escape(_id))
def sendMail(mai,username,password):
    user = User().findLogin(mai,password)
    _id = json.loads(user)
    _id = _id['_id']
    _id = _id['$oid']
    mail = Mail(app)
    msg = Message(subject="Confirmación de cuenta",
                        sender='proyectofinalmail@gmail.com',
                        recipients = [mai])
    link = 'http://localhost:4200/verify/'+_id
    msg.body = f'Gracias por registrarte en la página, para completar tu cuenta,pincha en el enlace: {link}'
    mail.send(msg)
    return '200'
#Usuarios
@app.route('/postuser',methods=['POST'])
def postuser():
        mai = request.json['mail']
        sendmail = False
        password = hashing.hash_value(request.json['password'], salt='abcd')
        user = User(request.json['username'],password,mai,request.json['rol'],icon=request.json['icono'])
        if user.existsMail(mai) == False:
            user.saveToDB() 
            return sendMail(mai,request.json['username'],password)
        else:
            print("msg: Mail already exists")
            return jsonify({"msg": "Mail already exists"}), 400

@app.route('/user' ,methods=['GET','PUT'])
@app.route('/user/<ident>',methods=['DELETE'])
@jwt_required
def user(ident=''):
    current_user = get_jwt_identity()
    if current_user is None:
        return jsonify({"msg": "Missing token"}), 400
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
        category = request.json['category']
        banner = request.json['banner']
        user = User()
        res = user.Update(iden,name,password,mail,rol,icon,category,banner)
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
        category = h['category']
        banner = h['banner']
        icon = h['icon']
        return jsonify(
            access_token=access_token,refresh_token=refresh_token,_id=_id,name=name,mail=mail,
            rol=rol,icon=icon,verified=verified,category=category,banner=banner,
            exp=date.strftime("%m %d %Y %H:%M:%S GMT+0200")
            ), 200

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
            f.save('./public/files/' + f.filename)
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
@app.route('/userportfolio/<_id>',methods=['GET'])
@jwt_required
def UserPortfolioID(_id):
    port = Portfolio()
    return port.GetByUserId(escape(_id))
@app.route('/getportfolio/<_id>',methods=['GET'])
@jwt_required
def GetPortfolio(_id):
    port = Portfolio()
    return port.GetById(escape(_id))

@app.route('/portfolio',methods=['POST','PUT','GET'])
@app.route('/portfolio/<iden>',methods=['DELETE'])
def portfolio(iden=''): 
    port = Portfolio()
    if request.method == 'GET':
        return port.GetAll()
    elif request.method == 'POST':
        filename = Upload()
        port = Portfolio(
            title=request.form['titulo'],
            file=filename,
            text=request.form['text'],
            author=request.form['author'],
            category=request.form['category'],
            tags = list(str(request.form['tags']).split(',')))
        print(str(request.form['tags']).split(','))
        return port.Post()
    elif request.method == 'PUT':
        iden = request.json['_id']
        return port.Update(iden['$oid'],request.json['archivo'],request.json['titulo'],
        request.json['texto'],request.json['autor'],request.json['coments'],
        request.json['points'],request.json['category'],request.json['tags'])
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