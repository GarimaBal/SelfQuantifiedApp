from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import datetime
import matplotlib.pyplot as plt


#start
app = Flask(__name__)
app.secret_key="thisisasecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TrackerDB.sqlite3'

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

# Models
class users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    username = db.Column(db.String, unique = True, nullable = False)
    users1 = db.relationship("user_trackers",backref = "users")

class user_trackers(db.Model):
    __tablename__ = 'user_trackers'
    tracker_id = db.Column(db.Integer, primary_key = True, autoincrement = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable = False)
    tracker_name = db.Column(db.String, nullable = False)
    tracker_type = db.Column(db.String, nullable = False)
    tracker_description = db.Column(db.String)
    tracker_settings = db.Column(db.String)
    logs = db.relationship("logs", backref = "user_trackers")

class logs(db.Model):
    __tablename__ = 'logs'
    logid = db.Column(db.Integer, primary_key = True, autoincrement = True, unique = True)
    tracker_id = db.Column(db.Integer, db.ForeignKey("user_trackers.tracker_id"), nullable = False)
    value = db.Column(db.Integer, nullable = False)
    time = db.Column(db.DateTime, nullable = False)
    notes = db.Column(db.String)
#end





@app.route("/")
def front():
  return render_template("index.html")

@app.route("/login", methods = ['GET','POST'])
def login():
  if request.method == 'POST':
    username1=request.form.get("username")    
    temp = users.query.filter_by(username = username1).first()     
    if temp is None:
      return render_template("nouser.html")
    else:
      session['username']=username1
      temp = users.query.filter_by(username = username1).first()
      user=temp.user_id
      session['userid']=user
      
      return render_template("index.html", user=user)
  return render_template("login.html")

@app.route("/logout")
def logout():
  session.pop("username", None)
  return redirect("/")

@app.route("/signup", methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
      username1=request.form.get("username")
      temp = users.query.filter_by(username = username1).first()
      if temp is None:
        user = users(username = request.form["username"])
        db.session.add(user)
        db.session.commit()
        session['username']=username1
        return render_template("login.html")
      else:
        return render_template("usernameexist.html")       

    else:
      return render_template("signup.html")

@app.route("/dashboard/<int:user_id>")
def dashboard(user_id):
  ltt={}
  user=user_id
  trackers=user_trackers.query.filter_by(user_id=user).all()
  for tracker in trackers:    
    t=logs.query.filter_by(tracker_id=tracker.tracker_id).order_by(logs.time.desc()).first()
    if t is None:
      pass
    else:
      ltt[tracker.tracker_id]=t.time  
  
  if (len(trackers)==0):
    return render_template("dashboard.html", user=user)
  else:
    return render_template("dashboard1.html", user=user, trackers=trackers, ltt=ltt)


@app.route("/createtracker/<int:user_id>", methods = ['GET','POST'])
def createtracker(user_id):
  if request.method == 'POST':
    tname=request.form.get("name")
    des=request.form.get("Description")
    ttype=request.form.get("TrackerType")
    set=request.form.get("Settings")
    user=user_id
    
    temp=user_trackers.query.filter_by(user_id=user, tracker_name=tname).all()
    
    if (len(temp)==0):
      entry = user_trackers(user_id=user, tracker_name=tname, tracker_type=ttype, tracker_description=des, tracker_settings=set)
      db.session.add(entry)
      db.session.commit()    
     
      return redirect(url_for('dashboard', user_id=user_id))
    else:
      return render_template("trackerexists.html")    
  else:
    user=user_id
    return render_template("createtracker.html",user=user)

@app.route("/user/<int:user_id>/logtracker/<int:tracker_id>", methods = ['GET','POST'])
def logtracker(user_id, tracker_id):
  user=user_id
  t=datetime.datetime.now()  
  trackid=tracker_id
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  type=temp.tracker_type
  trackername=temp.tracker_name
  if request.method == 'POST':
    
    tim=t
    val=request.form.get("Value")
    note=request.form.get("Notes")

    log=logs(tracker_id=trackid, value=val, time=tim, notes=note)
    db.session.add(log)
    db.session.commit()
    
    user_id=temp.user_id
    return redirect(url_for('logpage', tracker_id=tracker_id))

  elif request.method=="GET" and type=='numerical':   
    return render_template("lognumeric.html", t=t, track=tracker_id, user=user, trackername=trackername)
    
  elif request.method=="GET" and type=='m_choice':
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    for i in range(len(choice)):
      choices[choice[i]]=i
    return render_template("logMC.html", t=t, track=tracker_id, choices=choices, user=user, trackername=trackername)
    
  elif request.method=="GET" and type=='t_dur':   
    return render_template("logduration.html", t=t, track=tracker_id, user=user, trackername=trackername)
    
  elif request.method=="GET" and type=='bool':   
    return render_template("logbool.html", t=t, track=tracker_id, user=user, trackername=trackername)


@app.route("/user/<int:user_id>/logtracker/<int:tracker_id>/Delete", methods = ['GET'])
def deletetracker(user_id, tracker_id):
  trackid=tracker_id
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  entries=logs.query.filter_by(tracker_id=trackid).all()
  for ent in entries:
    db.session.delete(ent)
  db.session.delete(temp)
  db.session.commit()
  return redirect(url_for('dashboard', user_id=user_id))
  



@app.route("/user/<int:user_id>/logtracker/<int:tracker_id>/Edit", methods = ['GET','POST'])
def edittracker(user_id, tracker_id):
  track=user_trackers.query.filter_by(tracker_id=tracker_id).first()
  tra=tracker_id
  user=user_id
  if request.method == 'POST':
    
    tname=request.form.get("name")
    des=request.form.get("Description")
    set=request.form.get("Settings")
    db.session.query(user_trackers).filter(user_trackers.tracker_id==tra).update({user_trackers.tracker_name:tname, user_trackers.tracker_description:des, user_trackers.tracker_settings:set})
    db.session.commit()
    return redirect(url_for('dashboard', user_id=user))
      

  else:
    tname=track.tracker_name
    des=track.tracker_description
    set=track.tracker_settings
    type=track.tracker_type
    if type == 'm_choice':
      type='Multiple Choice'
    elif type=='bool':
      type='Boolean'
    elif type=='t_dur':
      type='Time Duration'
    elif type=='numerical':
      type='Numerical'
  return render_template("edittracker.html",tname=tname, des=des, set=set, type=type, tra=tra, user=user)
      
  
@app.route("/logpage/<int:tracker_id>")
def logpage(tracker_id):
  trackid=tracker_id
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  trackername=temp.tracker_name
  user=temp.user_id
  enteries=logs.query.filter_by(tracker_id=trackid).all()
  
  if temp.tracker_type=="numerical":
  
    return render_template("LogPageNum.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries)
    
  elif temp.tracker_type=="bool":
    for ent in enteries:
      if ent.value == 1:
        ent.value=True
      else:
        ent.value=False
    return render_template("LogPageBol.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries)

  elif temp.tracker_type=="t_dur":
    return render_template("LogPageTD.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries)

  elif temp.tracker_type=="m_choice":
    temp=user_trackers.query.filter_by(tracker_id=trackid).first()
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    for i in range(len(choice)):
      choices[choice[i]]=i    
    oq=list(choices.keys())
    for ent in enteries:
      ent.value=oq[ent.value]
    
    return render_template("LogPageMC.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries)

@app.route("/DeleteLog/<int:logid>", methods = ['GET'])
def deletelog(logid):
  temp=logs.query.filter_by(logid=logid).first()
  tracker_id=temp.tracker_id
  db.session.delete(temp)
  db.session.commit()
  return redirect(url_for('logpage', tracker_id=tracker_id))
  
@app.route("/EditLog/<int:logid>", methods = ['GET','POST'])
def editlog(logid):
  temp=logs.query.filter_by(logid=logid).first()
  log=temp.logid
  tracker_id=temp.tracker_id
  track=user_trackers.query.filter_by(tracker_id=tracker_id).first()
  if request.method == 'POST':
    
    no=request.form.get("Notes")
    val=request.form.get("Value")
    

    
    if val==None:
      val=temp.value
      
    db.session.query(logs).filter(logs.logid==logid).update({logs.value:val, logs.notes:no})
    db.session.commit()  
    return redirect(url_for('logpage', tracker_id=tracker_id))
 
  elif request.method=='GET' and track.tracker_type=='bool':
    tim=temp.time
    note=temp.notes
    print(note)
    
    trackername=track.tracker_name
    return render_template("editlogbool.html", log=log, note=note, tim=tim, trackername=trackername, tracker_id=tracker_id)
    
  elif request.method=='GET' and track.tracker_type=='t_dur':
    tim=temp.time
    value=temp.value
    note=temp.notes
    trackername=track.tracker_name
    return render_template("editlogTD.html", log=log, note=note, tim=tim, trackername=trackername, value=value, tracker_id=tracker_id)
    
  elif request.method=='GET' and track.tracker_type=='m_choice':
    tim=temp.time
    val=temp.value
    trackername=track.tracker_name
    note=temp.notes
    if val==None:
      val=temp.value
    temp=user_trackers.query.filter_by(tracker_id=tracker_id).first()
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    for i in range(len(choice)):
      choices[choice[i]]=i
    return render_template("editlogMC.html", choices=choices, log=log, note=note, tim=tim, trackername=trackername, tracker_id=tracker_id)
    
  elif request.method=='GET' and track.tracker_type=='numerical':
    tim=temp.time
    trackername=track.tracker_name
    value=temp.value
    note=temp.notes
    
    return render_template("editlognumerical.html", log=log, note=note, tim=tim, trackername=trackername, value=value, tracker_id=tracker_id)


@app.route("/DataPage-1week/<int:tracker_id>", methods = ['GET'])
def datapage1(tracker_id):
  timeframe="1 week"
  trackid=tracker_id
  t=datetime.datetime.now()
  weekago=t-datetime.timedelta(weeks=1)
  enteries=logs.query.filter(logs.time > weekago).filter(logs.tracker_id==trackid).all()
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  trackername=temp.tracker_name
  user=temp.user_id
  
  if temp.tracker_type == "numerical":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    print(y)
    plt.plot(x, y)
    plt.ylabel(temp.tracker_name+'Log')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageNum.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)


  elif temp.tracker_type == "t_dur":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    
    plt.plot(x, y, color="green", linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue', markersize=12)
    plt.ylabel(temp.tracker_name+'Duration')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageTD.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "m_choice":
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    dict={}
    #finalDict={}
    keys=[]
    for i in range(len(choice)):
      choices[choice[i]]=i
      keys.append(choice[i])
    
    for ent in enteries:
      ent.value=keys[ent.value]
      
    for entry in enteries:
      l=entry.value      
      if l in dict:
        print(l)
        dict[l]=dict[l]+1
        
      else:
        dict[l]=1

    names=list(dict.keys())
    values=list(dict.values())
    plt.bar(range(len(dict)), values, tick_label=names)
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    
    return render_template("DataPageMC.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "bool":
    count0=0
    count1=0
    for entry in enteries:      
      val=entry.value
      if val==1:
        count1=count1+1        
      elif val==0:
        count0=count0+1
        
    labels='True', 'False'
    sizes=[count1, count0]
    colors=['green', 'red']
    explode=(0.1, 0)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    return render_template("DataPageBool.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



@app.route("/DataPage-1month/<int:tracker_id>", methods = ['GET'])
def datapage2(tracker_id):
  timeframe="1 month"
  trackid=tracker_id
  t=datetime.datetime.now()
  weekago=t-datetime.timedelta(weeks=4)
  enteries=logs.query.filter(logs.time > weekago).filter(logs.tracker_id==trackid).all()
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  trackername=temp.tracker_name
  user=temp.user_id
  
  if temp.tracker_type == "numerical":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    print(y)
    plt.plot(x, y)
    plt.ylabel(temp.tracker_name+'Log')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageNum.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)


  elif temp.tracker_type == "t_dur":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    
    plt.plot(x, y, color="green", linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue', markersize=12)
    plt.ylabel(temp.tracker_name+'Duration')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageTD.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "m_choice":
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    dict={}
    #finalDict={}
    keys=[]
    for i in range(len(choice)):
      choices[choice[i]]=i
      keys.append(choice[i])
    
    for ent in enteries:
      ent.value=keys[ent.value]
      
    for entry in enteries:
      l=entry.value      
      if l in dict:
        print(l)
        dict[l]=dict[l]+1
        
      else:
        dict[l]=1

    names=list(dict.keys())
    values=list(dict.values())
    plt.bar(range(len(dict)), values, tick_label=names)
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    
    return render_template("DataPageMC.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "bool":
    count0=0
    count1=0
    for entry in enteries:      
      val=entry.value
      if val==1:
        count1=count1+1
        entry.value=True
      elif val==0:
        count0=count0+1
        entry.value=False
        
    labels='True', 'False'
    sizes=[count1, count0]
    colors=['green', 'red']
    explode=(0.1, 0)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    return render_template("DataPageBool.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)


@app.route("/DataPage-6month/<int:tracker_id>", methods = ['GET'])
def datapage3(tracker_id):
  timeframe="6 month"
  trackid=tracker_id
  t=datetime.datetime.now()
  weekago=t-datetime.timedelta(weeks=24)
  enteries=logs.query.filter(logs.time > weekago).filter(logs.tracker_id==trackid).all()
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  trackername=temp.tracker_name
  user=temp.user_id
  
  if temp.tracker_type == "numerical":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    print(y)
    plt.plot(x, y)
    plt.ylabel(temp.tracker_name+'Log')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageNum.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)


  elif temp.tracker_type == "t_dur":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    
    plt.plot(x, y, color="green", linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue', markersize=12)
    plt.ylabel(temp.tracker_name+'Duration')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageTD.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "m_choice":
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    dict={}
    #finalDict={}
    keys=[]
    for i in range(len(choice)):
      choices[choice[i]]=i
      keys.append(choice[i])
    
    for ent in enteries:
      ent.value=keys[ent.value]
      
    for entry in enteries:
      l=entry.value      
      if l in dict:
        print(l)
        dict[l]=dict[l]+1
        
      else:
        dict[l]=1

    names=list(dict.keys())
    values=list(dict.values())
    plt.bar(range(len(dict)), values, tick_label=names)
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    
    return render_template("DataPageMC.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "bool":
    count0=0
    count1=0
    for entry in enteries:      
      val=entry.value
      if val==1:
        count1=count1+1
        entry.value=True
      elif val==0:
        count0=count0+1
        entry.value=False
        
    labels='True', 'False'
    sizes=[count1, count0]
    colors=['green', 'red']
    explode=(0.1, 0)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    return render_template("DataPageBool.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)


@app.route("/DataPage-1year/<int:tracker_id>", methods = ['GET'])
def datapage4(tracker_id):
  timeframe="1 year"
  trackid=tracker_id
  t=datetime.datetime.now()
  weekago=t-datetime.timedelta(weeks=52)
  enteries=logs.query.filter(logs.time > weekago).filter(logs.tracker_id==trackid).all()
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  trackername=temp.tracker_name
  user=temp.user_id
  
  if temp.tracker_type == "numerical":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    print(y)
    plt.plot(x, y)
    plt.ylabel(temp.tracker_name+'Log')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageNum.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)


  elif temp.tracker_type == "t_dur":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    
    plt.plot(x, y, color="green", linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue', markersize=12)
    plt.ylabel(temp.tracker_name+'Duration')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageTD.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "m_choice":
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    dict={}
    #finalDict={}
    keys=[]
    for i in range(len(choice)):
      choices[choice[i]]=i
      keys.append(choice[i])
    
    for ent in enteries:
      ent.value=keys[ent.value]
      
    for entry in enteries:
      l=entry.value      
      if l in dict:
        print(l)
        dict[l]=dict[l]+1
        
      else:
        dict[l]=1

    names=list(dict.keys())
    values=list(dict.values())
    plt.bar(range(len(dict)), values, tick_label=names)
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    
    return render_template("DataPageMC.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "bool":
    count0=0
    count1=0
    for entry in enteries:      
      val=entry.value
      if val==1:
        count1=count1+1
        entry.value=True
      elif val==0:
        count0=count0+1
        entry.value=False
        
    labels='True', 'False'
    sizes=[count1, count0]
    colors=['green', 'red']
    explode=(0.1, 0)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    return render_template("DataPageBool.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)

@app.route("/DataPage-AllData/<int:tracker_id>", methods = ['GET'])
def datapage5(tracker_id):
  timeframe="All Time"
  trackid=tracker_id
  
  enteries=logs.query.filter(logs.tracker_id==trackid).all()
  temp=user_trackers.query.filter_by(tracker_id=trackid).first()
  trackername=temp.tracker_name
  user=temp.user_id
  
  if temp.tracker_type == "numerical":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    print(y)
    plt.plot(x, y)
    plt.ylabel(temp.tracker_name+'Log')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageNum.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)


  elif temp.tracker_type == "t_dur":
    x=[]
    y=[]
    for entry in enteries:
      x.append(entry.time)
      y.append(entry.value)
    
    plt.plot(x, y, color="green", linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue', markersize=12)
    plt.ylabel(temp.tracker_name+'Duration')
    plt.xlabel('timestamp')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")
    return render_template("DataPageTD.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)



  elif temp.tracker_type == "m_choice":
    options=temp.tracker_settings
    choice=options.split(",")
    choices={}
    dict={}
    #finalDict={}
    keys=[]
    for i in range(len(choice)):
      choices[choice[i]]=i
      keys.append(choice[i])
    
    for ent in enteries:
      ent.value=keys[ent.value]
      
    for entry in enteries:
      l=entry.value      
      if l in dict:
        print(l)
        dict[l]=dict[l]+1
        
      else:
        dict[l]=1

    names=list(dict.keys())
    values=list(dict.values())
    plt.bar(range(len(dict)), values, tick_label=names)
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    
    return render_template("DataPageMC.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)
    
  elif temp.tracker_type == "bool":
    count0=0
    count1=0
    for entry in enteries:      
      val=entry.value
      if val==1:
        count1=count1+1
        entry.value=True
      elif val==0:
        count0=count0+1
        entry.value=False
        
    labels='True', 'False'
    sizes=[count1, count0]
    colors=['green', 'red']
    explode=(0.1, 0)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title(temp.tracker_name+' Graph')
    plt.savefig("Graph")

    return render_template("DataPageBool.html", track=tracker_id, user=user, trackername=trackername, enteries=enteries, timeframe=timeframe)
    
if __name__=="__main__":
  app.run(host='0.0.0.0', debug=True)