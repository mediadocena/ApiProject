from pymongo import *
from const import Const
class User():
    def __init__(self,nam,passwor,mai,role):
        #Conexión a mongodb
        client = MongoClient(Const.URL)
        db = client.Project
        self.conn = db.users
        self.name=nam
        self.password = passwor
        self.mail = mai
        self.rol = role

    def __init__(self):
        pass

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
    def getFromDB(self,iden):
        good = True
        sel = None
        try:
            sel = self.conn.select.find_one({'_id':iden})
        except:
            return '400'
        return sel