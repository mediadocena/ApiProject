from flask import *
from models.User import User
from flask_hashing import Hashing
app = Flask(__name__)
hashing = Hashing(app)
#Error Handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

#Endpoints and Methods
"""
@app.route("/")
def redirect():
    return main()
@app.route("/prueba")
def prueba():
    return '<h1>Prueba</h1>'
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
        #DOPUT
        pass
    #DELETE
    elif request.method == 'DELETE':
        #DODEL
        pass    
    else:
        return '{"status":404 ,"error":"Method Not Found"}'
#LOGIN
@app.route('/login' ,methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    password = hashing.hash_value(password, salt ='abcd')
    h = User().findLogin(username,password)
    if h == False:
        return '{"status":404 ,"error":"User-Password pair not found"}'
    else: 
        for pas in h:
            h = pas['password']
        if password == h:
            return '{"status":200}'
        else:
            return '{"status":404 ,"error":"Invalid Login"}'
#Run app
if __name__ == '__main__':
    app.run(debug=True)