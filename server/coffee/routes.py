from coffee import coffee, engine, session
from coffee.models import User, Event
from flask import request
import datetime
from sqlalchemy import func, desc

EVENT_TYPES = [None, "coffee", "pack", "clean"]

@coffee.route("/", methods=["POST", "GET"])
@coffee.route("/index")
def index():

	if request.method == 'POST':
		if "uid" in request.form and "name" in request.form:
			session.query(User).filter(User.id==request.form["uid"]).update({"username":request.form["name"]})
			session.commit()

	ret = "<!DOCTYPE html><html><body>"
	events = session.query(Event).order_by(desc(Event.timestamp)).limit(10).all()
	ret += "Coffee history:<br><hr>"
	ret += "<table>"
	for ev in events:
		ret += "<tr>"
		username = ev.User.username
		uid = ev.User.id
		if username is None:
			username = "<form action='?' method='POST'><input type='hidden' name='uid' value='{}'><input type='text' name='name' value='please set'><input type='submit' value='set'></form>".format(uid)
		event = EVENT_TYPES[ev.what]
		ts = datetime.datetime.fromtimestamp(ev.timestamp).strftime('%Y-%m-%d %H:%M:%S')
		ret += "<td>[{}]</td><td>{}:</td><td>{}</td>".format(ts, username, event)
		ret += "</tr>"
	ret += "</table><hr>"

	ret += "Stats:<br><hr><table>"
	ret += "<tr><td>name</td><td>cleanings</td><td>bags</td><td>coffees</td></tr>"
	coffees = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(1)).group_by(Event.user_id).all()
	bags = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(2)).group_by(Event.user_id).all()
	cleans = session.query(Event, func.count(Event.what).label("count")).filter(Event.what.is_(3)).group_by(Event.user_id).all()
	for (event, c_cnt) in coffees:
		username = event.User.username
		uid = event.user_id
		u_bags = filter(lambda x: x[0].User.id == uid, bags)
		b_cnt = u_bags[0][1] if len(u_bags) else 0
		u_cleans = filter(lambda x: x[0].User.id == uid, cleans)
		cl_cnt = u_cleans[0][1] if len(u_cleans) else 0
		ret += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(username, cl_cnt, b_cnt, c_cnt)
	ret += "</table><hr>"
	ret += "</body></html>"
	return ret

@coffee.route("/new-coffee", methods=["GET"])
def new_coffee():

	if not "who" in request.args:
		return "dein ernst?"

	uid = request.args.get("who")

	# check for user
	u = session.query(User).filter(User.id.is_(uid)).all()
	if not len(u):
		print "create new user with id {}".format(uid)
		u = User(id=uid)
		session.add(u)
		
	# new coffee event
	e = Event(what=1, user_id=uid)
	session.add(e)

	# commit db
	session.commit()
	
	return "hallo du typ"
	
