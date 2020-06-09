from pymongo import *
from bson.json_util import loads, dumps
from const import Const
import sys
from bson.objectid import ObjectId
from operator import itemgetter
class Portfolio():
    def __init__(self,title='Undefined',file='Unknown',text='...',author='Undefined',authorname='',
    coments=[],points='',category='',tags='',totalpoints='',totalcoments='',mediapoints=''):
        client = MongoClient(Const.URL)
        db = client.Project
        self.conn = db.portfolio
        self.title=title
        self.file=file
        self.text=text
        self.author=author
        self.authorname=authorname
        self.coments=coments
        self.points = points
        self.category=category
        self.tags = tags
        self.totalpoints=totalpoints
        self.mediapoints=mediapoints
        self.totalcoments=totalcoments

    def Post(self):
        try:
            sel = self.conn.insert_one({'titulo':self.title,'titulo_lower':self.title.lower(),'archivo':self.file,
            'texto':self.text,'autor':self.author,'authorname':self.authorname,'authorname_lower':self.authorname.lower(),'coments':self.coments,
            'points':self.points,'category':self.category,'tags':self.tags,'totalpoints':self.totalpoints,
            'totalcoments':self.totalcoments,'mediapoints':0})
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
    
    def Update(self,iden,fil,titulo,texto,author,authorname,coments,points,category,tags):
        try:
            totalpoints = 0 
            totalcoments = 0
            mediapoints = 0
            for point in points:
                totalpoints += int(point['rate'])
            for com in coments:
                totalcoments = totalcoments+1
            if totalpoints is not 0:
                mediapoints = totalpoints/len(list(points))
            else:
                mediapoints = 0
            self.conn.update_one({'_id':ObjectId(iden)},{"$set":{'titulo':titulo,'titulo_lower':titulo.lower(),'archivo':fil,
            'texto':texto,'autor':author,'coments': coments,'authorname':authorname,'authorname_lower':authorname.lower(),'points':points,'category':category,'tags':tags,
            'totalpoints':totalpoints,
            'totalcoments':totalcoments,
            'mediapoints':mediapoints}})
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
            return '500'
        return '200' 

    def UpdateUsername(self,newname,oldname):
        self.conn.update_many({'authorname':oldname},{'$set':{'authorname':newname,'authorname_lower':newname.lower()}})

        return 200
    def UpdateComentAuthor(self,newname,oldname):
        control = False
        count = 0
        while control == False:
            x = self.conn.update_many({'coments.'+str(count)+'.name':oldname},{'$set':{'coments.'+str(count)+'.name':newname}})
            if x == None:
                control = True
            count = count + 1
        return 200
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
    def Search(self,args,filt):
        res = list(self.conn.find({filt:args}))
        return dumps(res)
    def MejorValorados(self):
        mejorvaloracion = []
        res = list(self.conn.find({}))
        res = sorted(res, key=itemgetter('mediapoints'), reverse=True)
        mejorvaloracion = res[0:9]
        print(mejorvaloracion)
        return dumps(mejorvaloracion)
    def GetByCategory(self,category):
        res = list(self.conn.find({'category':category}))
        print(dumps(res))
        return dumps(res)