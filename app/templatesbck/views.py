# encoding: UTF-8
from flask import render_template,flash,url_for,session,redirect,request,g ,jsonify
from app import app, db,lm , celery 
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Post,User
from app.forms import LoginForm,EditForm,PostForm,SignUpForm,ChangeForm,SearchForm
from datetime import datetime
import os
import random
import time
import path
import json
import datetime 
from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine
from vnpy.trader.app.ctaStrategy.strategy.strategyDemo import strategyDemo
from vnpy.trader.app.ctaStrategy.strategy.strategyHedge import strategyHedge
from datetime import datetime
import pymongo
from threading import Thread
from queue import Queue
import xlrd
import pandas as pd
queue = Queue()
@lm.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()	

@app.route('/',methods=['GET'])
@app.route('/index', methods = ['GET'])
@app.route('/index/<int:page>', methods = ['GET'])
@login_required
def index(page = 1):

	posts=Post.query.filter_by(user_id= current_user.id).order_by(db.desc(Post.time)).paginate(page,3, False)
		
	return render_template('index.html',title='Home',user = current_user,posts = posts)

@app.route('/user/<username>')
@login_required
def user(username,page = 1):
	user = User.query.filter_by(username = username).first()
	posts=Post.query.filter_by(user_id = user.id).order_by(db.desc(Post.time)).paginate(page,3, False)
	return render_template('user.html',user = user,posts = posts)

def drawLine(title,df,col):
    from pyecharts import Line
    line=Line(title)
    dates=df.index
    for name in df.columns:
	    line.add(name,dates,df.loc[:,name])
    #paramFilename='examples/WebTrader/app/templates/'+title +'.html'
    #path=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    #path=os.path.join(path,paramFilename)    	
    path=u'E:/vnpy-master/vnpy-master/examples/WebTrader/app/templates/'+title +'.html'      
    if os.path.exists(path):
        os.remove(path)
    line.render(path)

def drawBar(title,df):
    from pyecharts import Bar
    bar=Bar(title)
    dates=df.index
    #paramFilename='examples/WebTrader/app/templates/'+title +'.html'
    #path=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    #path=os.path.join(path,paramFilename)    	
    path=u'E:/vnpy-master/vnpy-master/examples/WebTrader/app/templates/'+title +'.html'  
    if os.path.exists(path):
        os.remove(path)          
    for name in df.columns:
        bar.add(name,dates,df.loc[:,name])
	bar.render(path)	
@app.route('/search_history_result/<col>',methods=['GET','POST'])
@login_required
def search_history_result(col):
	post = Post.query.filter_by(id=col).first()
	query=post.title
	col=query
	host, port = loadMongoSetting()
	dbClient = pymongo.MongoClient(host, port)
	dbClient.admin.authenticate("htquant", "htgwf@2018", mechanism='SCRAM-SHA-1')
	db=dbClient.get_database('USERDATA_DB')
	account=db.get_collection(col)
	
	var=[]
	col_vardf=col+'vardf'
	account_vardf=db.get_collection(col_vardf)
	for i in account_vardf.find():
		i.pop('_id')
		var.append(i)
	vardf=pd.DataFrame(var)
	drawBar("Var",vardf)
	
	num=[]
	col_numdf=col+'numdf'
	account_numdf=db.get_collection(col_numdf)
	for i in account_numdf.find():
		i.pop('_id')
		num.append(i)
	numdf=pd.DataFrame(num)
	drawBar("ContractVol",numdf)
	
	nv=[]
	col_nvdf=col+'nvdf'
	account_nvdf=db.get_collection(col_nvdf)
	for i in account_nvdf.find():
		i.pop('_id')
		nv.append(i)
	nvdf=pd.DataFrame(nv)
	drawLine("NetValue",nvdf,col)
	ptnv={'var':var}
	
	margin=[]
	col_margindf=col+'margindf'
	account_margindf=db.get_collection(col_margindf)
	for i in account_margindf.find():
		i.pop('_id')
		margin.append(i)
	margindf=pd.DataFrame(margin)   
	drawLine("Margin",margindf,col)
	
	u=[]
	col_hedgeResult = col + 'HedgeResult'
	account_HedgeResultdf=db.get_collection(col_hedgeResult)
	for i in account_HedgeResultdf.find():
		u.append([i["OPT"],i["Unhedged"],i["Unit"]])
	return render_template('search_history_result.html',u=u,ptnv=ptnv)
	
@app.route('/<index>/detail',methods=['GET','POST'])
@login_required
def detail(index):
	post = Post.query.filter_by(id=index).first()
	query=post.title
	if request.method == 'POST':
		if request.form['Post']=='Post':		
			return redirect(url_for('search_history_result',col=query))	
	elif request.method == 'GET':
		return render_template('detail.html',title='Detail',post = post)

		
#@app.route('/write',methods=['GET','POST'])
#@login_required
#def write():
	#form = PostForm()
	#if form.validate_on_submit():
		#post = Post(title=form.title.data,content = form.content.data,user_id = current_user.id)
		#db.session.add(post)
		#db.session.commit()
		#flash('Your post is now live!')
		#return redirect(url_for('index'))
	#return render_template('write.html',title='Write',form=form)



@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.login_check(request.form.get('username'),request.form.get('password'))
		if user:
			login_user(user)
			user.last_seen = datetime.now()
			try:
				db.session.add(user)
				db.session.commit()
			except:
				flash("The Database error!")
				return redirect('/login')
			flash('Your name: ' + request.form.get('username'))
			flash('remember me? ' + str(request.form.get('remember_me')))
			return redirect(url_for("index"))
		else:
			flash('Login failed, username or password error!')
			return redirect('/login')
	return render_template('login.html',form=form)

@app.route('/sign-up',methods=['GET','POST'])
def sign_up():
	form = SignUpForm()
	user = User()
	if form.validate_on_submit():
		user_name = request.form.get('username')
		user_password = request.form.get('password')
		register_check = User.query.filter(db.and_(User.username == user_name, User.password == user_password)).first()
		if register_check:
			return redirect('/sign-up')
		if len(user_name) and len(user_password):
			user.username = user_name
			user.password = user_password
		try:
			db.session.add(user)
			db.session.commit()
		except:
			return redirect('/sign-up')
		return redirect('/index')
	return render_template("sign_up.html",form=form)
		

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))




@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.username)
	if form.validate_on_submit():
		g.user.username = form.username.data
		g.user.brokerID = form.brokerID.data
		g.user.mdAddress = form.mdAddress.data
		g.user.tdAddress = form.tdAddress.data
		g.user.userID = form.userID.data
		g.user.password = form.password.data
		db.session.add(g.user)
		db.session.commit()
		param = {}
		param['brokerID'] = form.brokerID.data
		param['mdAddress'] = g.user.mdAddress 
		param['tdAddress'] = g.user.tdAddress 
		param['userID'] = g.user.userID 
		param['password'] = g.user.password 
		print param
		writeCTP_connect_json(param)
		flash(u'您的修改已经保存')
		return redirect(url_for('edit'))
	        	
	form.username.data = g.user.username

	#form.about_me.data = g.user.about_me
	return render_template('edit.html',form = form)

@app.route('/delete/<post_id>',methods = ['POST'])
@login_required
def delete(post_id):
	post = Post.query.filter_by(id = post_id).first()
	db.session.delete(post)
	db.session.commit()
	flash("delete post successful!")
	return redirect(url_for('user',username=g.user.username))


@app.route('/edit/<post_id>',methods = ['GET'])
@login_required
def editpost(post_id):
	form = ChangeForm()
	post = Post.query.filter_by(id = post_id).first()
	form.title.data = post.title
	form.content.data = post.content
	return render_template('change.html',form = form,post_id=post.id)

@app.route('/change/<post_id>',methods = ['POST'])
@login_required
def change(post_id):
	form = ChangeForm()
	post = Post.query.filter_by(id = post_id).first()
	if form.validate_on_submit():
		post.title = form.title.data
		print(post.title,post.content)
		post.content = form.content.data
		db.session.add(post)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user',username=g.user.username))
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
@app.route('/paramInput',methods=['GET','POST'])
@login_required
def paramInput():
	form = PostForm() 
	if form.validate_on_submit(): 
		print "title1: ",form.title.data , request.form.get('starttime'),request.form.get('code'),request.form.get('direction') #request.form.get('direction') 
		code = request.form.get('code')
		section2 = request.form.get('section2')
		spotID = section2[1:9]
		direction = request.form.get('direction')
		if direction == u'持有多头':
			direction =  u'LongHedging'
		else:
			direction =  u'ShortHedging'
		volume = form.title.data
		startdate = request.form.get('starttime') 
		enddate = request.form.get('endtime') 
		strategystartDate = request.form.get('strategystartDate') 
		period = form.content.data
		strategyName = request.form.get('strategyName') 
		strategyChoice = request.form.get('strategyChoice') 
		#导入用户数据库	
		param = {}
		code = code.encode('unicode-escape').decode('string_escape')
		code = code.split('.')[0]
		param['symbol'] = code
		param['spotID'] = spotID
		param['Qs'] = volume 
		param['period'] = period 
		param['direction'] = direction
		param['datastartdate'] = startdate # 数据日期
		param['startdate'] = strategystartDate # 策略日期
		param['enddate'] = enddate 
                param['strategyName'] = strategyName
		param['strategyChoice'] = strategyChoice
	        writeJson(param)
			
		total= strategyName	
		contents="策略命名："+strategyName+"策略选择："+strategyChoice +"合约代码："+code+"\n现货数量："+volume+"\nspotID："+spotID+"\n调仓周期："+period+"\n对冲方向：" \
		          +direction+"\n数据加载日期："+startdate+"\n策略开始日期："+strategystartDate+"\n结束日期："+enddate
		post=Post(title=total,content = contents,user_id = current_user.id)
		db.session.add(post)
		db.session.commit()		
		print "finishing save data!!!!"
		flash(u'您的修改已经保存')
	return render_template('paramInput.html',title='paramInput',form=form)
# Celery configuration
@celery.task(bind=True) 
#def long_task(self):
def long_task(self):
    """Background task that runs a long function with progress reports."""
    # 毫无意义的随机状态信息 但是web上显示不出来,不知道为什么
    #verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    #adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    #noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    #message = ''
    #开启线程监听回测日期
    #queue = Queue()
    import datetime
    date_ = paramDate()
    startdate= date_['datastartdate']
    lastdate=date_['enddate']    
    startDate = time.strptime(startdate, "%Y-%m-%d")
    endDate =  time.strptime(lastdate, "%Y-%m-%d")	
    
    date1=datetime.datetime(startDate[0],startDate[1],startDate[2])

    date2=datetime.datetime(endDate[0],endDate[1],endDate[2])	
    total = (date2 - date1).days    
    ##s1 = Student(startdate= date_['startdate'],lastdate=date_['enddate'], queue=queue)
    #s1 = Student(startdate='20170101' ,lastdate='20171230', queue=queue)
    #s1.start()    
    #开启回测实例线程 
    c = Thread(target=producer)
    c.start()    
    # 监听
    message = 'hold on'    
    while True:
	msg = queue.get()
	if msg == "finish":
		return {'current': 100, 'total': 100, 'status': 'Task completed!',
		       'result': 42}	
	else :
	    dt =  time.strptime(msg, "%Y-%m-%d")
	    date3 = datetime.datetime(dt[0],dt[1],dt[2])
	    i = (date3 - date1).days	
            self.update_state(state='PROGRESS',
                            meta={'current': i, 'total': total,
                                  'status': message})   
	    print i ,total 
	    time.sleep(1)
	#if i == 99:
	    #print(u"{}：finish！".format(lastdate))
	    #return {'current': 100, 'total': 100, 'status': 'Task completed!',
	            #'result': 42} 
        #if dt == time.strptime(lastdate,"%Y-%m-%d"):
	    #print(u"{}：finish！".format(lastdate))
	    #return {'current': 100, 'total': 100, 'status': 'Task completed!',
                   #'result': 42}
				   

    
# 生产者：回测线程	     
def producer():
    #开启回测实例线程 该线程推送把回测的datetime数据推送到queue  
    engine = BacktestingEngine(queue=queue) 
    #..........实现回测.......    
    # 读取策略参数字典，为下一步读取合约做准备
    engine.readParam_Setting()
    # 设置回测日期
    date_ = paramDate()
    datastartdate= date_['datastartdate']
    lastdate=date_['enddate']       
    engine.setStartDate(datastartdate, 0)
    engine.setEndDate(lastdate)
    #engine.setStartDate('20170103', 0)
    #engine.setEndDate('20170213')    
    # 设置手续费
    engine.setRate(0.3 / 10000)  # 万0.3
    # 在引擎中创建策略对象
    #engine.initStrategy(strategyDemo, {})   
    engine.initStrategy(strategyHedge, {})
    # 读取参数
    symbol = date_['symbol']
    symbolList = []
    symbol = symbol.encode('unicode-escape').decode('string_escape')
    symbolList.append(symbol.split('.')[0])    
    
    #symbolList = ['HC']
    
    engine.setDatabase(symbolList)
    # 设置初始仓位
    engine.setInitialPos(0)
    engine.loadDailyHistoryData()	
    engine.hedgeResult()
	
    host,port=loadMongoSetting()
    dbClient = pymongo.MongoClient(host, port)
    dbClient.admin.authenticate("htquant", "htgwf@2018", mechanism='SCRAM-SHA-1')
    db=dbClient.get_database('USERDATA_DB')

    
    #回测结果	
    col=db[symbol+' '+datastartdate+' '+lastdate]	
    data=xlrd.open_workbook(r'E:\vnpy-master\vnpy-master\examples\WebTrader\resultsDF.xlsx')
    table=data.sheets()[0]
    rowstag=table.row_values(0)
    nrows=table.nrows
    returnData={}
    for i in range(1,nrows):
        returnData[i]=json.dumps(dict(zip(rowstag,table.row_values(i))))
        returnData[i]=json.loads(returnData[i])
        col.insert(returnData[i])
    #nvdf表单
    col_nvdf=db[symbol+' '+datastartdate+' '+lastdate+'nvdf']
    data=xlrd.open_workbook(r'E:\vnpy-master\vnpy-master\examples\WebTrader\nvDF.xlsx')
    table=data.sheets()[0]
    rowstag=table.row_values(0)
    nrows=table.nrows
    returnData={}
    for i in range(1,nrows):
        returnData[i]=json.dumps(dict(zip(rowstag,table.row_values(i))))
        returnData[i]=json.loads(returnData[i])
        col_nvdf.insert(returnData[i])

	#vardf表单
    col_vardf=db[symbol+' '+datastartdate+' '+lastdate+'vardf']
    data=xlrd.open_workbook(r'E:\vnpy-master\vnpy-master\examples\WebTrader\varDF.xlsx')
    table=data.sheets()[0]
    rowstag=table.row_values(0)
    nrows=table.nrows
    returnData={}
    for i in range(1,nrows):
        returnData[i]=json.dumps(dict(zip(rowstag,table.row_values(i))))
        returnData[i]=json.loads(returnData[i])
        col_vardf.insert(returnData[i])

	#numdf表单
    col_numdf=db[symbol+' '+datastartdate+' '+lastdate+'numdf']
    data=xlrd.open_workbook(r'E:\vnpy-master\vnpy-master\examples\WebTrader\numDF.xlsx')
    table=data.sheets()[0]
    rowstag=table.row_values(0)
    nrows=table.nrows
    returnData={}
    for i in range(1,nrows):
        returnData[i]=json.dumps(dict(zip(rowstag,table.row_values(i))))
        returnData[i]=json.loads(returnData[i])
        col_numdf.insert(returnData[i])

	#margindf表单
    col_margindf=db[symbol+' '+datastartdate+' '+lastdate+'margindf']
    data=xlrd.open_workbook(r'E:\vnpy-master\vnpy-master\examples\WebTrader\marginDF.xlsx')
    table=data.sheets()[0]
    rowstag=table.row_values(0)
    nrows=table.nrows
    returnData={}
    for i in range(1,nrows):
        returnData[i]=json.dumps(dict(zip(rowstag,table.row_values(i))))
        returnData[i]=json.loads(returnData[i])
        col_margindf.insert(returnData[i])    
	
	#HedgeResult
    col_margindf=db[symbol+' '+datastartdate+' '+lastdate+'HedgeResult']
    data=xlrd.open_workbook(r'E:\vnpy-master\vnpy-master\examples\WebTrader\HedgeResult.xlsx')
    table=data.sheets()[0]
    rowstag=table.row_values(0)
    nrows=table.nrows
    returnData={}
    for i in range(1,nrows):
        returnData[i]=json.dumps(dict(zip(rowstag,table.row_values(i))))
        returnData[i]=json.loads(returnData[i])
        col_margindf.insert(returnData[i])   
    # 全部生成完毕，推送queue 完成信息
    msg = 'finish'
    queue.put(msg)
    
    	

@app.route('/longtask', methods=['GET','POST'])
def longtask(): 
    task = long_task.apply_async() 
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}    


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
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
#-----------------------------
def loadDailyHistoryData(query):
        """按照交易日分批载入历史数据,然后回放数据"""
        host, port = loadMongoSetting()
        dbClient = pymongo.MongoClient(host, port)
        dbClient.admin.authenticate("htquant", "htgwf@2018", mechanism='SCRAM-SHA-1')
        db=dbClient.get_database('SPOT_DB')
        account=db.get_collection('I')
        u=[]
        for i in account.find({"Variety":query}):
            u.append([i["ID"],i["Variety"],i["Grade"],i["Region"],i["Price"],i["Date"]])
        return u
@app.route('/searchResult/<query>',methods=['GET','POST'])
@login_required
def searchResult(query):	
	u=loadDailyHistoryData(query) 
	return render_template('searchResult.html',u=u)     
@app.route('/search',methods=['GET','POST'])
@login_required
def search():  
	form = SearchForm()
	if request.method == 'POST':
		return redirect(url_for('searchResult',collection=request.form.get('collection'),query=request.form.get('code'),region=request.form.get('region')))
	return render_template('search.html', title='Search', form=form)      
#---------------------------------------------------------
#@app.route('/trader')
@login_required
def trader():
   
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data,content = form.content.data,user_id = current_user.id)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('index'))
	return send_file('./templates/trader.html')
#---------------------------------------------------		
def paramDate():  
    paramFilename='vnpy/trader/app/ctaStrategy/strategy/strategyHedge_Param_Setting.json'
    path=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    path=os.path.join(path,paramFilename)
    #加载策略变量
    with open(path) as f:
	    param = json.load(f)
    return param 
            
def writeJson(param):            
    paramFilename='vnpy/trader/app/ctaStrategy/strategy/strategyHedge_Param_Setting.json'
    path=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    path=os.path.join(path,paramFilename)
    with open(path, 'w') as f :
	json.dump(param,f)

def writeCTP_connect_json(param):            

    path="E:/vnpy-master/vnpy-master/examples/WebTrader/CTP_connect.json"
    with open(path, 'w') as f :
	json.dump(param,f)

	
@app.route('/HedgeForm',methods=['GET','POST'])
@login_required
def HedgeForm():
	import flask_excel    
	import pandas as pd 
	paramFilename='vnpy/trader/app/ctaStrategy/HedgeResult.csv'
	path=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
	path=os.path.join(path,paramFilename)
	import numpy as np
	
	HedgeResult = pd.read_csv(path)
	u = np.array(HedgeResult)	
	#for index , detail in u.items():
		#u.append([detail[0],detail[1],detail[2],detail[3]])#,detail[4],detail[5],detail[6],detail[7]])   
	return render_template('HedgeFromResult.html',u=u)
#-------------------------------------------
"""监听线程"""
class Student(Thread):
    def __init__(self, startdate, lastdate, queue):
        import datetime 
        super(Student,self).__init__()
        self.lastdate = lastdate
        self.queue = queue
	startDate = time.strptime(startdate, "%Y%m%d")
	endDate =  time.strptime(lastdate, "%Y%m%d")	

        date1=datetime.datetime(startDate[0],startDate[1],startDate[2])

        date2=datetime.datetime(endDate[0],endDate[1],endDate[2])	
	total = (date2 - date1).days
    def run(self):
        while True:
            #  监听回测程序
            msg = self.queue.get()
	    #i = endDate - datetime.strptime(msg, "%Y-%m-%d") 
	    dt =  time.strptime(msg, "%Y-%m-%d")
	    date3 = datetime.datetime(dt[0],dt[1],dt[2])
	    i = (date2 - date3).days
	    self.update_state(state='PROGRESS',
	                    meta={'current': i, 'total': total,
	                          'status': message})
	    print "days : " ,i
	    #time.sleep(1)    
            # 到日期返回结束信息
            if msg == self.lastdate:
                print(u"{}：finish！".format(self.lastdate))
		return {'current': 100, 'total': 100, 'status': 'Task completed!',
			'result': 42}	        
	
