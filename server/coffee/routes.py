from coffee import coffee, engine, session, Config
from coffee.models import User, Event
from flask import request, send_file, render_template
import datetime, time
from sqlalchemy import func, desc
import drawing
import os
import random

def calculate_coffee_price():
    # prices
    # calculation is based on two things:
    # for the prices, take all coffees and bags used / buyed until the current month
    # to avoid changing prices after each coffee.
    current_date = datetime.datetime.fromtimestamp(time.time())
    line = time.mktime((current_date.year, current_date.month, 1, 0, 0, 1, 0, 0, 0))
    
    # all coffees and bags consumed until beginning of current month
    coffees_all = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(1)).filter(Event.timestamp < line).group_by(Event.user_id).all()
    bags_all = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(2)).filter(Event.timestamp < line).group_by(Event.user_id).all()   
    cffs = sum([x[1] for x in coffees_all])
    pcks = sum([x[1] for x in bags_all])

    # calculate "price" per coffee
    ppc = pcks / float(cffs) if cffs else 0

    return ppc
    
@coffee.route("/get-number", methods=["GET"])
def image():
    if not "nr" in request.args:
        # todo 
        return None

    Num = drawing.Numbers(30)
    img = Num.cache_number(request.args.get("nr"), Config.CACHE_FOLDER)

    return send_file(img, mimetype='image/jpeg')

@coffee.route("/", methods=["POST", "GET"])
@coffee.route("/index")
def index():
    ret = "<!DOCTYPE html><html><body>"
    
    if request.method == 'POST' and "uid" in request.form:
        uid = request.form["uid"]
        
        # add a new name to a specific uid token
        if "name" in request.form:
            session.query(User).filter(User.id==uid).update({"username":request.form["name"]})
            session.commit()
            ret += "added new name for token {}".format(uid)

        # randomly add some data for historical purposes
        if "update" in request.form:
            if request.form["update"] not in Config.EVENT_TYPES:
                ret += "unknown event type"
            else:
                amount = int(request.form["amount"])
                ev_type = Config.EVENT_TYPES.index(request.form["update"])
                for i in range(amount):
                    ts = time.time() - 60*(60*24*30+i)
                    ev = Event(user_id=uid, timestamp=ts, what=ev_type)
                    session.add(ev)
                session.commit()
                ret += "added {} event types with type {}".format(amount, ev_type)
        
        ret +="<hr>"


    # history
    events = session.query(Event).order_by(desc(Event.timestamp)).limit(10).all()
    ret += "History:<hr>"
    ret += "<table>"
    for ev in events:
        ret += "<tr>"
        username = ev.User.username
        uid = ev.User.id
        if username is None:
            username = "<form action='?' method='POST'>"
            username += "<input type='hidden' name='uid' value='{}'>".format(uid)
            username += "<input type='text' name='name' value='please set'>"
            username += "<input type='submit' value='set'></form>"
        event = Config.EVENT_TYPES[ev.what]
        ts = datetime.datetime.fromtimestamp(ev.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        ret += "<td>[{}]</td><td>{}:</td><td>{}</td>".format(ts, username, event)
        ret += "</tr>"
    ret += "</table><hr>"


    # prices
    # calculation is based on two things:
    # for the prices, take all coffees and bags used / buyed until the current month
    # to avoid changing prices after each coffee.
    current_date = datetime.datetime.fromtimestamp(time.time())
    line = time.mktime((current_date.year, current_date.month, 1, 0, 0, 1, 0, 0, 0))
    
    ret += "Calculations:<hr>"
    # all coffees
    coffees_all = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(1))
    coffees_calc = coffees_all.filter(Event.timestamp < line).group_by(Event.user_id).all()
    coffees = coffees_all.filter(Event.timestamp >= line).group_by(Event.user_id).all()

    bags_all = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(2))
    bags_calc = bags_all.filter(Event.timestamp < line).group_by(Event.user_id).all()
    bags = bags_all.filter(Event.timestamp >= line).group_by(Event.user_id).all()

    cleans = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(3)).group_by(Event.user_id).all()
    cffs = sum([x[1] for x in coffees_calc])
    pcks = sum([x[1] for x in bags_calc])
    clns = sum([x[1] for x in cleans])

    ret += "{} coffees brewed in history<br>".format(cffs)
    ret += "{} packs of beans used<br>".format(pcks)
    ret += "{} cleanings performed<br>".format(clns)

    # calculate "price" per coffee
    ppc = pcks / float(cffs) if cffs else 1
    ret += "leads to {} packs per coffee!".format(ppc)
    ret += "<hr>"

    # statistics 

    ret += "Stats:<hr><table border='1'>"
    ret += "<tr><td>name</td><td>cleanings</td><td>bags</td><td>Sum</td><td>coffees</td><td></td></tr>"
    for (event, c_cnt) in coffees:
        username = event.User.username
        uid = event.user_id
        u_bags = filter(lambda x: x[0].User.id == uid, bags_calc)
        b_cnt = u_bags[0][1] if len(u_bags) else 0
        u_coffee = filter(lambda x: x[0].User.id == uid, coffees_calc)
        c_cnt_calc = u_coffee[0][1] if len(u_coffee) else 0
        rb_cnt = ppc * c_cnt_calc # this is the real number of bags used by the consumer
        sb_cnt = b_cnt - rb_cnt # whats his dept?
        u_cleans = filter(lambda x: x[0].User.id == uid, cleans)
        cl_cnt = u_cleans[0][1] if len(u_cleans) else 0
    
        ret += "<tr><td>{}</td>".format(username)
        ret += "<td>{}</td>".format(cl_cnt)
        ret += "<td>{}</td>".format(b_cnt)
        ret += "<td>{:0.2f}</td>".format(sb_cnt)
        ret += "<td>{}</td>".format(c_cnt)
        ret += "<td><img src='get-number?nr={}'></td>".format(c_cnt)
        ret += "</tr>"
        if Config.ADMIN:
            ret += "<tr><td></td><td colspan='4'><form action='?' method='post'>add "
            ret += "<input type='hidden' name='uid' value='{}'>".format(uid)
            ret += "<input type='text' name='amount' value='0'>"
            ret += "<input type='submit' name='update' value='coffee'>"
            ret += "<input type='submit' name='update' value='clean'>"
            ret += "<input type='submit' name='update' value='pack'>"
            ret += "</form></td>"
            ret += "</tr>"

    ret += "</table><hr>"
    ret += "</body></html>"
    return ret

@coffee.route("/new", methods=["GET"])
def new_coffee():

    if not "who" in request.args or not "what" in request.args:
        return "wrong arguments?"

    # sanity checks
    uid = request.args.get("who")
    try:
        what = int(request.args.get("what"))
    except:
        return "failed to parse what"
    if what >= len(Config.EVENT_TYPES):
        return "unknown event type"

    # check for user
    u = session.query(User).filter(User.id.is_(uid)).all()
    if not len(u):
        print "create new user with id {}".format(uid)
        u = User(id=uid)
        session.add(u)
		
    # new coffee event
    t = time.time()
    e = Event(what=what, timestamp=t, user_id=uid)
    session.add(e)

    # is this needed?
    c_file = os.path.join(Config.CACHE_FOLDER, "message.txt")
    with open(c_file, "w") as f:
        f.write("{},{}".format(uid, Config.EVENT_TYPES[what]))
    # commit db
    session.commit()

    return "" # empty message, good message
	
@coffee.route("/show")
def show():
    ppc = calculate_coffee_price()

    # get data
    # first of all, get current date
    current_date = datetime.datetime.fromtimestamp(time.time())
    line = time.mktime((current_date.year, current_date.month, 1, 0, 0, 1, 0, 0, 0))
    coffees_all = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(1))
    coffees_calc = coffees_all.filter(Event.timestamp < line).group_by(Event.user_id).all()
    coffees = coffees_all.filter(Event.timestamp >= line).group_by(Event.user_id).all()
    bags_all = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(2))
    bags_calc = bags_all.filter(Event.timestamp < line).group_by(Event.user_id).all()
    bags = bags_all.filter(Event.timestamp >= line).group_by(Event.user_id).all()
    cleans = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(3)).group_by(Event.user_id).all()
    cffs = sum([x[1] for x in coffees_calc])
    #print "cffs used for calc: ", cffs
    pcks = sum([x[1] for x in bags_calc])
    #print "packs bought: ", pcks
    clns = sum([x[1] for x in cleans])
    #print clns, " cleanings"

    # get all users
    all_users = session.query(User).order_by(desc(User.username)).all()
    
    users = {}
    #for (event, c_cnt) in coffees:
    for user in all_users:
        username = user.username
        uid = user.id
        
        u_coffee = filter(lambda x: x[0].User.id == uid, coffees)
        c_cnt = u_coffee[0][1] if len(u_coffee) else 0
        u_bags = filter(lambda x: x[0].User.id == uid, bags_calc)
        b_cnt = u_bags[0][1] if len(u_bags) else 0
        u_coffee = filter(lambda x: x[0].User.id == uid, coffees_calc)
        c_cnt_calc = u_coffee[0][1] if len(u_coffee) else 0
        rb_cnt = ppc * c_cnt_calc # this is the real number of bags used by the consumer
        sb_cnt = b_cnt - rb_cnt # whats his dept?
        u_cleans = filter(lambda x: x[0].User.id == uid, cleans)
        cl_cnt = u_cleans[0][1] if len(u_cleans) else 0

        users[uid] = {}
        users[uid]["username"] = username
        users[uid]["coffee"] = c_cnt
        users[uid]["coffee_total"] = c_cnt_calc
        users[uid]["balance"] = sb_cnt
        users[uid]["packs"] = b_cnt
        users[uid]["cleans"] = cl_cnt

    # something happend?
    # ugly, put this into the database
    c_file = os.path.join(Config.CACHE_FOLDER, "message.txt")
    message = None
    if os.path.exists(c_file):
        with open(c_file, "r") as f:
            c = f.read().split("\n")
            if len(c) > 0:
                m = c[0].split(",")
                if len(m) == 2:
                    message = {}
                    try:
                        name = users[m[0]]["username"]
                        message["username"] = name if name is not None else "unknown"
                        message["what"] = m[1]
                    except:
                        pass
        os.remove(c_file)

    return render_template("overview.html", users=users, message=message, random=int(random.random()*1e12))
