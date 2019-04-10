import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	# Database Options
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Admin mode to add more functionality.
	ADMIN = True

	# Plot Configuration
	# folder for cached number plots
	#CACHE_FOLDER = "/home/andieh/src/coffee-counter/server/tmp/"
	#CACHE_FOLDER = "D:\\arduino\\coffee-counter\\tmp"
        CACHE_FOLDER = "/home/pi/RFID/coffee-counter/tmp"
	# create random start and endpoints for the lines to plot
	# this looks more "natural"
	RANDOMNESS = True

	# event types which are available. 
	# todo: clean this up, None is shit and this is not generic enough
	EVENT_TYPES = [None, "coffee", "pack", "clean"]
