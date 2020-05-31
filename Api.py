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
from flask_compress import Compress
import os
import sys
import ast
import base64
compress = Compress()
app = Flask(__name__)
compress.init_app(app)
hashing = Hashing(app)
defaults = ['text/html', 'text/css', 'text/xml', 'application/json',
                    'application/javascript','image/png','image/jpg','video/mp4','audio/mp3']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='proyectofinalmail@gmail.com',
    MAIL_PASSWORD='tujbjlnapolrwqad',
    COMPRESS_ALGORITHM = 'gzip',
    COMPRESS_MIMETYPES = defaults
)
# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'jwtls132526nbcs44465873nasl'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 864000
#16mb max
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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
    link = 'https://flaskproyectofinal.herokuapp.com/verify/'+_id
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
        if user.existsMail(mai) == False and user.existsUsername == False:
            user.saveToDB() 
            return sendMail(mai,request.json['username'],password)
        else:
            print("msg: Mail already exists")
            return jsonify({"msg": "Mail or username already exists"}), 400
@app.route('/changeicon',methods=['put'])
@jwt_required
def ChangeIcon():
        iden = request.json['_id']['$oid']
        icon = request.json['icon']
        user = User()
        res = user.UpdateIcon(iden,icon)
        return res

@app.route('/userById/<ident>',methods=['GET'])
def UserById(ident):
    user = User()
    data = user.GetUserByID(escape(ident))
    print(data, escape(ident))
    return data
@app.route('/user' ,methods=['GET','PUT'])
@app.route('/user/<ident>',methods=['DELETE','GET'])
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
        try:
            password = hashing.hash_value(request.json['password'], salt='abcd')
        except:
            password = ''
        mail = request.json['mail']
        rol = request.json['rol']
        iden = request.json['_id']['$oid']
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
        return jsonify(res)
    else:
        return jsonify({"error":"Method Not Found"}), 404

@app.route('/username')
def username():
    user = User()
    res = user.getUsernames()
    print(res)
    return res , 200

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
    #CONTROLAR QUE EL NOMBRE DEL ARCHIVO EXISTA O NO
    if request.method == 'POST':
        f = ''
        autor = request.form['Autor']
        postname = request.form['PostName']
        tipo = request.form['category']
        filename = ''
        control = False
        count = 0
        arr = []
    #try:
        while(control == False):
            print(count)
            f = request.files['file'+str(count)]
            if '.png' in f.filename:
                    ext = '.png'
            elif '.jpg' in f.filename:
                    ext = '.jpg'
            elif '.jpeg' in f.filename:
                    ext = '.jpeg'
            elif '.mp3' in f.filename:
                    ext = '.mp3' 
            elif '.mp4' in f.filename:
                    ext = '.mp4' 
            filename = str(count)+str(autor)+str(postname)
            if os.path.exists('public/files/'+filename):
                return jsonify({"msg":"El archivo ya existe"}),400
            
            count = count+1   
            if tipo == 'Dibujo-fotografia':
                if ext == '.png' or ext == '.jpg' or ext == '.jpeg':
                    f.save('./public/files/' + filename)
                    arr.append({'medium':'https://flaskproyectofinal.herokuapp.com/download/'+filename,'big':'https://flaskproyectofinal.herokuapp.com/download/'+filename})
                else:
                    pass
            elif tipo == 'Música':
                if ext != '.mp3':
                    pass
                else:
                    f.save('./public/files/' + filename)
                    arr.append({'title':f.filename,'link':'https://flaskproyectofinal.herokuapp.com/download/'+filename})
            elif tipo == 'Video':
                if ext != '.mp4':
                    pass
                else:
                    f.save('./public/files/' + filename)
                    arr.append({'title':f.filename,'link':'https://flaskproyectofinal.herokuapp.com/download/'+filename})
            if('file'+str(count) in request.files):
                control = False
            else:
                control = True
    #except:
    #       e = sys.exc_info()[0]
    #       print( "Error: %s" % e )
    #       return jsonify({"msg":"Archivo demasiado pesado"})
    return jsonify(arr)
@app.route('/UploadUserImg',methods=['POST'])
def UploadUserImg():
    fil = request.files['file']
    filename = request.form['filename']
    print('archivo: ',filename)
    if os.path.exists('public/files/'+filename):
        os.remove('public/files/'+filename)
    fil.save('./public/files/' + filename)
    return jsonify({"msg":"Uploaded"}),200
  
@app.route('/changeIconBase64',methods=['PUT'])
@jwt_required
def changeBase64():
    data = request.json()
    if data is None:
        return jsonify({'error': 'No json'})
    else:
        img_data = data['file']
        img_name = data['filename']
        if os.path.exists('public/files/'+img_name):
            os.remove('public/files/'+img_name)
        with open("public/files/"+img_name, "wb") as fh:
            fh.write(base64.decodebytes(img_data.encode()))
        url = 'https://flaskproyectofinal.herokuapp.com/download/'+img_name
        user = User()
        res = user.UpdateIcon(img_name,url)
    return jsonify({"msg":"OK"}), 200

@app.route('/download/<name>',methods=['GET'])
def download(name):
    if request.method == 'GET':
        print(escape(name))
        return send_file('public/files/'+escape(name), mimetype='image', cache_timeout=0)

@app.route('/delete',methods=['PUT'])
@jwt_required
def delete():
    try:
        itmarr = request.json['files']
        for itm in itmarr:
            if 'big' in itm:
                name = str(itm['big']).replace('https://flaskproyectofinal.herokuapp.com/download/','')
                print(name)
            elif 'link' in itm:
                name = str(itm['link']).replace('https://flaskproyectofinal.herokuapp.com/download/','')
                print(name)
            if os.path.exists('public/files/'+name):
                os.remove('public/files/'+escape(name))
    except:
        e = sys.exc_info()
        print( "Error: %s" % e )
        return '500'
    return jsonify({"msg":"All files deleted"}),200

@app.route('/userportfolio/<_id>',methods=['GET'])
def UserPortfolioID(_id):
    port = Portfolio()
    return port.GetByUserId(escape(_id))
@app.route('/getportfolio/<_id>',methods=['GET'])
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
        #filename = Upload()
        port = Portfolio(
            title=request.form['titulo'],
            file=ast.literal_eval(request.form['file']),
            text=request.form['text'],
            author=request.form['author'],
            authorname=request.form['authorname'],
            category=request.form['category'],
            totalpoints=0,
            totalcoments=0,
            tags = list(str(request.form['tags']).lower().split(',')))
        #print(str(request.form['tags']).split(','))
        return port.Post()
    elif request.method == 'PUT':
        iden = request.json['_id']
        return port.Update(iden['$oid'],request.json['archivo'],request.json['titulo'],
        request.json['texto'],request.json['autor'],request.json['authorname'],request.json['coments'],
        request.json['points'],request.json['category'],request.json['tags'])
    elif request.method == 'DELETE':

        return port.Delete(escape(iden))
    return jsonify({"msg":"Route Not Found"},400)

@app.route('/search',methods=['POST'])
def search():
    args = str(request.json['args']).lower()
    filt = request.json['filt']
    port = Portfolio()
    return port.Search(args,filt)

@app.route('/mostvalored',methods=['GET'])
def GetMostValored():
    port = Portfolio()
    res = port.MejorValorados()
    return res

@app.route('/category/<cat>',methods=['GET'])
def GetByCategory(cat):
    port = Portfolio()
    res = port.GetByCategory(str(escape(cat)))
    return res
#Run app
@app.after_request
def after_request(response):
    #response.headers.add('Cache-Control:','no-store')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
def dyno(self):
    while True:
        print("esperando...")
        if datetime.datetime.now().minute % 5 == 0: 
            a = requests.get("https://flaskproyectofinal.herokuapp.com/Main")
            print(a)
            time.sleep(60)
            
if __name__ == '__main__':
    app.run()
