# encoding: UTF-8

import os
import sys
import pymongo
# 将根目录路径添加到环境变量中
#paramFilename='examples/WebTrader/app/templates/NetValue' +'.html'
#path=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
#path=os.path.join(path,paramFilename)    
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
host, port = loadMongoSetting()
dbClient = pymongo.MongoClient(host, port)
dbClient.admin.authenticate("htquant", "htgwf@2018", mechanism='SCRAM-SHA-1')
db=dbClient.get_database('USERDATA_DB')
col= 'I2014-10-06 2015-02-06'
account=db.get_collection(col)
u=[]
var=[]
col_vardf=col+'vardf'
account_vardf=db.get_collection(col_vardf)
for i in account.find():
	print  u.append([i["OPT"],i["Unhedged"],i["Unit"]])
