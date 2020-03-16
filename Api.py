from flask import *
from models.User import User
app = Flask(__name__)

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
@app.route('/user',methods=['POST'])
@app.route('/user/<id>' ,methods=['GET','PUT','DELETE'])
def User(id):
    if request.method is 'POST':
        user = User('nombre1','pass1','mail1','user')
        return 'Response: '+user.saveToDB()
    elif request.method is 'GET':
        user = User('','','','')
        user.getFromDB(escape(id))
        pass
    elif request.method is 'PUT':
        #DOPUT
        pass
    elif request.method is 'DELETE':
        #DODEL
        pass    
    else:
        return 'NOT_FOUND : 404'
#Run app
if __name__ == '__main__':
    app.run(debug=True)