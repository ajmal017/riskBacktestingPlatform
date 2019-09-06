from app.models import Post,User

from app import app, db,lm , celery 
import os
import pymongo
#print User.login_check('test','test')
def loadMongoSetting():
    """载入MongoDB数据库的配置"""
    fileName = 'VT_setting.json'
    path = os.path.abspath(os.path.dirname(__file__)) 
    fileName = os.path.join(path, fileName)  
    
    try:
        f = file(fileName)
        setting = json.load(f)
        host = setting['mongoHost']
        port = setting['mongoPort']
    except:
        host = '10.3.135.33'
        port = 57012
    return host, port
#posts = db.session.query(Post).filter(Post.title =='111').one()
#posts =Post.query.filter_by(id='3333').first()
#para= posts
host, port = loadMongoSetting() 
dbClient = pymongo.MongoClient(host, port)
dbClient.admin.authenticate("htquant", "htgwf@2018", mechanism='SCRAM-SHA-1')
db=dbClient.get_database('USERDATA_DB')
account=db.get_collection('3333')
var=[]
col='3333'
col_vardf=col+'vardf'
account_vardf=db.get_collection(col_vardf) 
for i in account_vardf.find():
	i.pop('_id') 
	var.append(i) 
import pandas as pd 
vardf=pd.DataFrame(var)
#import time 
#startdate= para.splitlines()[7]
#lastdate=para.splitlines()[9]
#startDate = time.strptime(startdate, "%Y-%m-%d")
#endDate =  time.strptime(lastdate, "%Y-%m-%d")	
print vardf
