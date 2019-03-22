import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	# Database Options
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Plot Configuration
	# folder for cached number plots
	#CACHE_FOLDER = "/home/andieh/src/coffee-counter/server/tmp/"
	CACHE_FOLDER = "D:\\arduino\\coffee-counter\\tmp"
	# create random start and endpoints for the lines to plot
	# this looks more "natural"
	RANDOMNESS = True

	