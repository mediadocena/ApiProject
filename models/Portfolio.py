from pymongo import *
from bson.json_util import loads, dumps
from const import Const
import sys
from bson.objectid import ObjectId
class Portfolio():
    def __init__(self,title='Undefined',file='Unknown',text='...',author='Undefined',
    coments='',points='',category='',tags='',totalpoints=''):
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
        self.tags = tags
        self.totalpoints=totalpoints

    def Post(self):
        try:
            sel = self.conn.insert_one({'titulo':self.title,'archivo':self.file,
            'texto':self.text,'autor':self.author,'coments':self.coments,
            'points':self.points,'category':self.category,'tags':self.tags,'totalpoints':self.totalpoints})
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
    
    def Update(self,iden,fil,titulo,texto,author,coments,points,category,tags):
        try:
            totalpoints = 0 
            for point in points:
                totalpoints += int(point['rate'])
            self.conn.update_one({'_id':ObjectId(iden)},{"$set":{'titulo':titulo,'archivo':fil,
            'texto':texto,'autor':author,'coments': coments,'points':points,'category':category,'tags':tags,
            'totalpoints':totalpoints}})
            print('3')
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
        return '200' 

    def GetById(self,iden):
        try:
            res = self.conn.find_one({'_id':ObjectId(iden)})
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
        return dumps(res)
    def GetByUserId(self,iden):
        try:
            res = list(self.conn.find({'autor':iden}))
        except:
            return '500'
        return dumps(res)
