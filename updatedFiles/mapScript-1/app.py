import pymongo
import json
import os
from bson.json_util import dumps
from final_code import main1
from flask import Flask, jsonify, make_response, render_template, request, url_for, redirect, session, flash
from pymongo import MongoClient
import ast
from database import station_house_officer, receiver, query, result
import threading
from subprocess import Popen, PIPE
from datetime import datetime

client = MongoClient("localhost", 27017)
db = client["BTP"]
col1 = db["userInformation"]


app = Flask(__name__, template_folder='templates/')


def calculateTime():
	# print(datetime.datetime.now())
	return datetime.now()


#MAIN
@app.route('/', methods=['GET','POST'])
def mainRoute():
	if not session.get('logged_in'):
		return redirect(url_for("login"))
	else:
		return redirect(url_for("dashboard"))

#LOGIN
@app.route('/login', methods = ['POST', 'GET'])
def login():
	if not session.get('logged_in'):
		return render_template("index.html")
	else:
		return redirect(url_for("dashboard"))

@app.route('/checkLogin', methods = ['POST', 'GET'])
def check():
	if request.method == 'POST':
		result = request.form
		userName = request.form.get('userName')
		password = request.form.get('password')
		print(userName,password)
		SHOInfo = checkLogin(userName,password)

		if (SHOInfo == 0):
			print "WRONG"
			flash("Wrong Password")
			return redirect(url_for("login"))

		else:

			print "CORRECT"
			session['logged_in'] = True
			session['curr_sho'] = SHOInfo
			# return render_template("result.html")
			return redirect(url_for("dashboard"))


def checkLogin(userName,password):

	result = json.loads(dumps(list(db.userInformation.find())))
	for singleUser in result:
		if singleUser["id"] == userName and singleUser["pass"] == password:
			return singleUser
	return 0


def updateSHO(shoId):
	result = json.loads(dumps(list(db.userInformation.find())))
	for singleUser in result:
		if singleUser["id"] == shoId:
			print "lassan"
			
			updatedQueries = []
			for i in range (len(singleUser["queries"])):
				etTemp = datetime.strptime(singleUser["queries"][i]["end_time"],"%Y-%m-%dT%H:%M")
				if etTemp > calculateTime() and singleUser["queries"][i]["frequency"] != "1":
					singleUser["queries"][i]["completed"] = False
				else:
					print "wowowowo"
					singleUser["queries"][i]["completed"] = True
				# updatedQueries.append(i)		
			# singleUser["queries"] = updatedQueries

			# print singleUser

			session['curr_sho'] = singleUser


#LOGOUT
@app.route('/logout', methods = ['POST', 'GET'])
def logout():
	session['logged_in'] = False
	return redirect(url_for("login"))


#DASHBOARD
@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():
	if not session.get('logged_in'):
		return redirect(url_for("login"))
	else:
		# SHOInfo = eval(SHOInfo)
		SHOInfo = session.get('curr_sho')
		updateSHO(SHOInfo["id"])
		SHOInfo = session.get('curr_sho')
		
		# print SHOInfo

		SHOInfo = json.dumps(SHOInfo)
		return render_template("dashboard.html", uInfo = SHOInfo)


#ALL QUERIES
@app.route('/allquery')
def allquery():
	if not session.get('logged_in'):
		return redirect(url_for("login"))
	else:
		SHOInfo = session.get('curr_sho')
		updateSHO(SHOInfo["id"])
		SHOInfo = session.get('curr_sho')
		SHOInfo = json.dumps(SHOInfo)
		return render_template("allQueries.html", uInfo= SHOInfo)
	

#CREATE QUERY PAGE
@app.route('/create')
def createQuery():
	if not session.get('logged_in'):
		return redirect(url_for("login"))
	else:
		SHOInfo = session.get('curr_sho')
		updateSHO(SHOInfo["id"])
		SHOInfo = session.get('curr_sho')

		SHOInfo = json.dumps(SHOInfo)
		return render_template("createQuery.html", uInfo = SHOInfo)

def helpRunQuery(queryName, lat, lng, radius, level, receiver, frequency, endTime, shoId):
	newQuery = query(queryName, lat, lng, radius, level, receiver, frequency, endTime)
	db.userInformation.update({ "id" : shoId }, { "$push": { "queries" : newQuery.get_object_json() } })
	newQuery.runQuery(shoId)

#METHOD TO IMPLEMENT QUERY
@app.route('/queryCreated', methods = ['POST', 'GET'])
def queryCreated():
	if request.method == 'POST':

		result1 = request.form

		queryName = request.form.get('queryName')
		lat = request.form.get('lat')
		lng = request.form.get('long')
		radius = request.form.get('radius1')
		receiver = request.form.get('receiver')
		frequency = request.form.get('frequency')
		endTime = request.form.get('finishTime')
		level = request.form.get('level')
		
		#RUN QUERY

		# print "testExp"

		# print queryName

		SHOInfo = session.get('curr_sho')
		updateSHO(SHOInfo["id"])
		SHOInfo = session.get('curr_sho')
		# SHOInfo = eval(SHOInfo)
	
		thread1 = threading.Thread(target = helpRunQuery, args = (queryName, lat, lng, radius, level, receiver, frequency, endTime, SHOInfo["id"],))
		thread1.start()

		# process = Popen(['python', 'runQuery.py', queryName, lat, lng, radius, level, receiver, frequency, endTime, SHOInfo["id"]], stdout=PIPE, stderr=PIPE)
		# stdout, stderr = process.communicate()
		# print stdout


		# newQuery.runQuery(SHOInfo["id"])
		

		# print newQuery.get_object_json()




	return redirect(url_for("dashboard"))



#MODIFY QUERY PAGE
@app.route('/modify/<i>')
def modifyQuery(i):
	if not session.get('logged_in'):
		return redirect(url_for("login"))
	else:
		SHOInfo = session.get('curr_sho')
		updateSHO(SHOInfo["id"])
		SHOInfo = session.get('curr_sho')
		SHOInfo = json.dumps(SHOInfo)
		print(i)
		return render_template("modifyQuery.html", uInfo = SHOInfo, data=i)


@app.route('/queryModified', methods=['POST', 'GET'])
def query_modified():
	if not session.get('logged_in'):
		return redirect(url_for("login"))
	else:
		if request.method == 'POST':
			result1 = request.form
			queryName = request.form.get('queryName')
			lat = request.form.get('lat')
			lng = request.form.get('long')
			radius = request.form.get('radius1')
			receiver = request.form.get('receiver')
			frequency = request.form.get('frequency')
			endTime = request.form.get('finishTime')
			road_level = request.form.get('road_level')
			if (road_level == "HighWays"):
				level = 1
			elif (road_level == "MainRoads"):
				level = 2
			elif (road_level == "Streets"):
				level = 3
			
			
			SHOInfo = session.get('curr_sho')
			updateSHO(SHOInfo["id"])
			SHOInfo = session.get('curr_sho')
			# SHOInfo = json.dumps(SHOInfo)

			# db.userInformation.update({ "id" : SHOInfo["id"] }, { "$set": { "queries" : newQuery.get_object_json() } })
			# db.userInformation.update({ "id" : SHOInfo["id"] }, { "$set": { "queries" : newQuery.get_object_json() } })
			# db.userInformation.update({ "id" : SHOInfo["id"] }, { "$set": { "queries" : newQuery.get_object_json() } })


			result1 = json.loads(dumps(list(db.userInformation.find())))
			
			queryVal = 0
			queriesFin = 0

			for singleUser in result1:
				if singleUser["id"] == SHOInfo["id"]:
					print "shoid found"
					queries = singleUser["queries"]
					for singleQuery in queries:
						if singleQuery["query_name"] == queryName:
							print "query found"
							queryVal = singleQuery
							queriesFin = queries

			if queryVal==0:
				print "Q NOT FOUND"
				return 0



			for j in range(0,len(queriesFin)):
				if queriesFin[j]["query_name"] == queryVal["query_name"]:
					queriesFin[j]["receiver"] = receiver;
					queriesFin[j]["end_time"] = endTime;
					queriesFin[j]["frequency"] = frequency;

				# queryVal["results"].append(newResult.get_object_json())


			db.userInformation.update({ "id" : SHOInfo["id"] }, { "$set": { "queries" : queriesFin } })

	return redirect(url_for("dashboard"))


@app.route('/queryMap', methods=['POST', 'GET'])
def active_query_map():
	if not session.get('logged_in'):
		return redirect(url_for("login"))
	else:
		SHOInfo = session.get('curr_sho')
		updateSHO(SHOInfo["id"])
		SHOInfo = session.get('curr_sho')

		SHOInfo = json.dumps(SHOInfo)
		return render_template("allQueryMap.html", uInfo = SHOInfo)



# @app.route('/dashboard',methods = ['POST', 'GET'])
# def dashboard():
# 	return render_template("login.html")


# #INSERT QUERY 
# @app.route('/insertMaps', methods=['GET','POST'])
# def render_static():
# 	return render_template('staticMaps2.html')



# lat = 0
# lng = 0
# radius = 0

# @app.route('/result',methods = ['POST', 'GET'])
# def result():
# 	if request.method == 'POST':
# 		result = request.form
# 		print result
# 		lat = request.form.get('lat')
# 		log = request.form.get('long')
# 		radius = request.form.get('radius1')
# 		level = request.form.get('level')# 		uId = request.form.get('name1')
# 		get_bottlenecks(lat,log,radius, level, uId)

# 	return render_template("result.html")

# @app.after_request
# def add_header(r):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     r.headers["Pragma"] = "no-cache"
#     r.headers["Expires"] = "0"
#     r.headers['Cache-Control'] = 'public, max-age=0'
#     return r


if __name__ == '__main__':
	app.secret_key = os.urandom(12)
	app.run(host= '0.0.0.0')









# main(27,77,100)