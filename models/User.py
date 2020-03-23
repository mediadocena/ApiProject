from pymongo import *
from const import Const
from flask import jsonify
from bson.json_util import loads, dumps
from models import Post
class User:
    #Class constructor
    def __init__(self, nam='', passwor='', mai='', role='',post=[]):
        #Conexión a mongodb
        client = MongoClient(Const.URL)
        db = client.Project
        self.conn = db.users
        self.name=nam
        self.password = passwor
        self.mail = mai
        self.rol = role
        self.post = post
    #Insert a new User to Mongo
    def saveToDB(self):
        good = True
        try:
            self.conn.insert_one({'name':self.name,'password':self.password,'mail':self.mail,'rol':self.rol,'post':self.post})
        except:
            good = False
        if good:
            return '200'
        else:
            return '500'
    #Get a user from mongo by ID
    def getByIdFromDB(self,iden):
        sel = None
        try:
            sel = self.conn.select.find_one({'_id':iden})
        except:
            return '500'
        return sel
    #Login Mehtod
    def findLogin(self, username, password):
        try:
            sel = list(self.conn.find({'name':username,'password':password}))
            print('Login Data:',sel)
            if sel == []:
                return False
            else:
                return sel
        except:
            return '500'
    #Get all users
    def getAll(self):
        res = None
        try:
            res = list(self.conn.find({}))
        except:
            return '500'
        return dumps(res)
    #Update user
    def Update(self,user):
        try:
            res = self.conn.update_one({'_id':user['_id']},{{'name':user['name'],'password':user['password'],'mail':user['mail'],'rol':user['rol'],'post':user['post']}})
        except:
            return '500'
        return '200' 