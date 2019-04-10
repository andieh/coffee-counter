from config import Config
import urllib2
import time

# minimum time between two events: (seconds)
MINIMUM_TIME_DELTA = 30

class CoffeeConnection:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		# add test if target is reachable
		self.base = "http://{}:{}/".format(ip, port)
                self.history = {}

	def call(self, address):
		target = "{}{}".format(self.base, address)
		print "calling wget on {}".format(target)

		response = urllib2.urlopen(target)
		code = response.code
		if code != 200:
			print "failed to get response from coffee page, code was {}".format(res)

	def add(self, what, uid):
                ts = time.time()
                if uid in self.history and ts - self.history[uid] < MINIMUM_TIME_DELTA:
                        print "min time delta not reached!"
                        self.history[uid] = ts
                        return
                        
                self.history[uid] = ts

		wid = Config.EVENT_TYPES.index(what)
		address = "new?who={}&what={}".format(uid, wid)
		self.call(address)			

	def add_coffee(self, uid):
		self.add("coffee", uid)
		
	def add_pack(self, uid):
		self.add("pack", uid)

	def add_clean(self, uid):
		self.add("clean", uid)

if __name__ == "__main__":
	con = CoffeeConnection("localhost", 5000)
	uid = "asdfasdf"

	print "add a coffee"
	con.add_coffee(uid)

	print "add a bag of beans"
	con.add_pack(uid)

	print "add cleaning"
	con.add_clean(uid)	
