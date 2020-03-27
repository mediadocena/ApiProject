from pymongo import *
from bson.json_util import loads, dumps
from const import Const
import sys
class Portfolio():
    def __init__(self,title='Undefined',file='Unknown',text='...',author='Undefined',coments=''):
        client = MongoClient(Const.URL)
        db = client.Project
        self.conn = db.users
        self.title=title
        self.file=file
        self.text=text
        self.author=author
        self.coments=coments

    def Post(self):
        try:
            sel = self.conn.insert_one({'titulo':self.titulo,'archivo':self.archivo,'texto':self.texto,'autor':self.author,'coments':self.coments})
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
        return '200'

    def GetAll(self):
        try:
            res = list(self.conn.find({}))
        except:
            return '500'
        return dumps(res)

    def Delete(self,iden):
        try:
            res = self.conn.delete_one({'_id':ObjectId(iden)})
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
        return '200'
    
    def Update(self,port):
        try:
            res = self.conn.update_one({'_id':port['_id']},{{'archivo':port['file'],'titulo':port['titulo'],
            'texto':port['texto'],'autor':port['author'],'coments':port['coments']}})
        except:
            return '500'
        return '200' 