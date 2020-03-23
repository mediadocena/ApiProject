from pymongo import *
from bson.json_util import loads, dumps
from const import Const
class Post():
    def __init__(self,title='Undefined',file='Unknown',text='...',author='Undefined',coments=''):
        client = MongoClient(Const.URL)
        db = client.Project
        self.conn = db.users
        self.title=title
        self.file=file
        self.text=text
        self.author=author
        self.coments=coments