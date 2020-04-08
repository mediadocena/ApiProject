from pymongo import *
from bson.json_util import loads, dumps
from const import Const
import sys
class Portfolio():
    def __init__(self,title='Undefined',file='Unknown',text='...',author='Undefined',coments='',points='',category=''):
        client = MongoClient(Const.URL)
        db = client.Project
        self.conn = db.portfolio
        self.title=title
        self.file=file
        self.text=text
        self.author=author
        self.coments=coments
        self.points = points
        self.category=category

    def Post(self):
        try:
            sel = self.conn.insert_one({'titulo':self.title,'archivo':self.file,
            'texto':self.text,'autor':self.author,'coments':self.coments,'points':self.points,'category':self.category})
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
    
    def Update(self,iden,file,titulo,texto,author,coments,points,category):
        try:
            res = self.conn.update_one({'_id':ObjectId(iden)},{{'archivo':file,'titulo':titulo,
            'texto':texto,'autor':author,'coments': coments,'points':points,'category':category}})
        except:
            return '500'
        return '200' 

    def GetById(self,iden):
        try:
            res = self.conn.find_one({'_id':ObjectId(iden)})
        except:
            return '500'
        return dumps(res)
