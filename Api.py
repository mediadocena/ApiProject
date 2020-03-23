from flask import *
from models.User import User
from flask_hashing import Hashing
from bson.json_util import loads, dumps
app = Flask(__name__)
hashing = Hashing(app)
#Error Handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.route('/Main')
def main():
    nam = [{
        'number':1,
        'name':'Nombre1',
        'age':24,
        'city':'Sevilla'
    },
    {
        'number':2,
        'name':'Nombre2',
        'age':22,
        'city':'Sevilla'
    },
    ]
    return render_template('MainTemplate.html', name=nam)
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
@app.route('/user' ,methods=['POST','GET','PUT','DELETE'])
def user():
    #POST
    if request.method == 'POST':
        password = hashing.hash_value(request.form['password'], salt='abcd')
        user = User(request.form['username'],password,request.form['mail'],request.form['rol'])
        return 'Response: '+ user.saveToDB()
    #GET
    elif request.method == 'GET':
        user = User()
        res = user.getAll()
        return res
    #PUT
    elif request.method == 'PUT':
        data = request.form['user']
        user = User()
        res = user.Update(data)
        return res
    
    #DELETE
    elif request.method == 'DELETE':
        #DODEL
        pass    
    else:
        return '{"status":404 ,"error":"Method Not Found"}'
#LOGIN
@app.route('/login' ,methods=['POST'])
def login():
    username = request.json['mail']
    password = request.json['password']
    password = hashing.hash_value(password, salt ='abcd')
    h = User().findLogin(username,password)
    if h == False:
        return '{"status":404 ,"error":"User-Password pair not found"}'
    else: 
        for pas in h:
            p = pas['password']
        if password == p:
            return dumps(h)
        else:
            return '{"status":404 ,"error":"Invalid Login"}'
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
            f.save('ApiProject/public/files/' + name+ext)
        except:
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