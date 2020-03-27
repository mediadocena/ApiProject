from pymongo import *
from const import Const
from flask import jsonify
from bson.json_util import loads, dumps
from bson.objectid import ObjectId

import sys
class User:
    #Class constructor
    def __init__(self, nam='', passwor='', mai='', role=''):
        #Conexión a mongodb
        client = MongoClient(Const.URL)
        db = client.Project
        self.conn = db.users
        self.name=nam
        self.password = passwor
        self.mail = mai
        self.rol = role
    #Insert a new User to Mongo
    def saveToDB(self):
        good = True
        try:
            self.conn.insert_one({'name':self.name,'password':self.password,'mail':self.mail,'rol':self.rol})
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
            sel = self.conn.select.find_one({'_id':iden},{'password':0})
        except:
            return '500'
        return sel
    #Login Mehtod
    def findLogin(self, mail,password):
        try:
            sel = self.conn.find_one({'mail':mail,'password':password},{'password':0})
            print('Login Data:',sel)
            if sel == []:
                return False
            else:
                return dumps(sel)
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
    #Get all users
    def getAll(self):
        res = None
        try:
            res = list(self.conn.find({},{'password':0}))
        except:
            return '500'
        return dumps(res)
    #Update user
    def Update(self,iden,name,password,mail,rol):
        try:
            self.conn.update_one({'_id':ObjectId(iden)},{"$set": {'name':name,'password':password,'mail':mail,'rol':rol}})
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
        return '200' 

    def Delete(self,iden):
        try:
            res = self.conn.delete_one({'_id':ObjectId(iden)})
            print(res)
            print(iden)
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
        return '200'