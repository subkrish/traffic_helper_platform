import json
from pymongo import MongoClient
import pymongo
import time 
from btpBackendManagement import get_bottlenecks
from bson.json_util import dumps
from datetime import datetime
import sys

client = MongoClient("localhost", 27017)
db = client["BTP"]
col1 = db["userInformation"]


class station_house_officer:
	
	sho_id = 0
	sho_name = "Tanmay"
	sho_password = "abc"
	queries = []
	receivers = []

	def __init__(self, _sho_id, _sho_name , _sho_password):
		self.sho_id = _sho_id
		self.sho_name = _sho_name
		self.sho_password = _sho_password
		self.receivers.append(receiver(_sho_id))

	def add_query(self, _query_name, _lat, _lng, _r, _level,_rec_name, _frequency, _endtime):
		q = query(_query_name, _lat, _lng, _r, _level,_rec_name, _frequency, _endtime)

		self.queries.append(q)

	def add_receiver(self, _name):
		self.receivers.append(receiver(_name))

	def get_object_json(self):
		obj = dict()

		obj['id'] = self.sho_id
		obj['name'] = self.sho_name
		obj['pass'] = self.sho_password

		obj['queries'] = []
		obj['receivers'] = []

		for i in self.queries:
			obj['queries'].append(i.get_object_json())

		for i in self.receivers:
			obj['receivers'].append(i.get_object_json())


		return obj

class receiver:
	rec_name = "abc"
	# rec_phoneno = "+911234567890"

	def __init__(self, name):
		self.rec_name = name
		# self.rec_phoneno = phoneno

	def get_object_json(self):
		obj = dict()

		obj['name'] = self.rec_name
		# obj['phoneno'] = self.rec_phoneno

		return obj

class query:
	query_name = "query1"
	lat = 28.123
	lng = 77.123
	r = 1000
	level = 2
	completed = False

	receiver = receiver("abc")
	frequency = 10 #every 10 min
	end_time = 0
	results = []



	def __init__(self, _query_name, _lat, _lng, _r, _level,_rec_name, _frequency, _endtime):
		self.query_name = _query_name
		self.lat = _lat
		self.lng = _lng
		self.r = _r
		self.level = _level
		self.receiver = receiver(_rec_name)
		self.frequency = _frequency
		self.results=[]
		self.end_time = _endtime


	# def thelperRun(self, shoId):
	# 	thread1 = threading.Thread(target = self.runQuery(), args = (shoid,))
	# 	thread1.start()

	def calculateTime(self):
		# print(datetime.datetime.now())
		return datetime.now()

	def runQuery(self, shoId):

		while(1):

			print shoId
			
			result1 = json.loads(dumps(list(db.userInformation.find())))

			# print result1

			queryVal = 0
			queriesFin = 0

			for singleUser in result1:
				if singleUser["id"] == shoId:
					print "shoid found"
					queries = singleUser["queries"]
					for singleQuery in queries:
						if singleQuery["query_name"] == self.query_name:
							print "query found"
							queryVal = singleQuery
							queriesFin = queries

			if queryVal==0:
				print "Q NOT FOUND"
				return 0 


			allResults = get_bottlenecks(queryVal["lat"],queryVal["long"],queryVal["radius"],queryVal["level"],queryVal["receiver"], shoId, queryVal["query_name"])

			# f= open("","w+")

			for i in allResults:

				newResult = result(i[0][0],i[0][1],i[1][0],i[1][1],i[2],self.query_name)
				self.results.append(newResult)
				db.userInformation.update({ "id" : shoId }, { "$push": { "results" : newResult.get_object_json() } })


				# for j in range(0,len(queriesFin)):
				# 	if queriesFin[j]["query_name"] == queryVal["query_name"]:
				# 		queriesFin[j]["results"].append(newResult.get_object_json())




				# db.userInformation.update({ "id" : shoId }, { "$set": { "queries" : queriesFin } })


			# break

			print ("We're in the SleepTime now")
			sys.stdout.flush()
			if self.frequency == "1":
				db.userInformation.update({"id":shoId}, { "$set" : {  "completed" : True }  } )
				print ("We're in the EndQuery now")
				break
			elif self.frequency == "2":
				time.sleep(2*60)
			elif self.frequency == "3":
				time.sleep(30*60)
			elif self.frequency == "4":
				time.sleep(60*60)
			elif self.frequency == "5":
				time.sleep(120*60)
			elif self.frequency == "6":
				time.sleep(24*60*60)
			print ("We're out of the SleepTime now")


			endTimeTemp = datetime.strptime(self.end_time,"%Y-%m-%dT%H:%M")

			if self.calculateTime() > endTimeTemp:
				db.userInformation.update({"id":shoId}, { "$set" : {  "completed" : True }  } )
				print ("We're in the EndQuery now")
				break


		#GET VALUES FROM DB
		#RUN QUERY - results to DB,WHATSAPP
		#CHECK FINISH
		#DELETE QUERY VALUES FROM DB


	# def add_result(self, _lat1, _lng1, _lat2, _lng2, _speed):
	# 	r = result(_lat1, _lng1, _lat2, _lng2, _speed, calculateTime())
	# 	self.results.append(r)

	def get_object_json(self):
		obj = dict()

		obj['query_name'] = self.query_name
		obj['lat'] = self.lat
		obj['long'] = self.lng
		obj['radius'] = self.r
		obj['level'] = self.level
		obj['completed'] = self.completed
		obj['receiver'] = self.receiver.rec_name
		obj['frequency'] = self.frequency
		obj['end_time'] = self.end_time


		obj['results'] = []

		for i in self.results:
			obj['results'].append(i.get_object_json())

		return obj

class result:
	lat1 = 28.123
	lng1 = 77.123

	lat2 = 28.123
	lng2 = 77.123

	speed = 30.77

	timestamp = "15:45:45"
	link = "www.something.com"

	qName = ""

	def calculateTime(self):
		# print(datetime.datetime.now())
		return datetime.now()


	def __init__ (self, _lat1, _lng1, _lat2, _lng2, _speed, _qName):
		self.lat1 = _lat1
		self.lng1 = _lng1

		self.lat2 = _lat2
		self.lng2 = _lng2

		self.speed = _speed
		self.timestamp = self.calculateTime()

		pre_msg = "https://www.google.com/maps/dir/"
		message = str(_lat1) + "," + str(_lng1) + "/" + str(_lat2) + "," + str(_lng2)

		self.link = pre_msg+message

		self.qName = _qName


	def get_object_json(self):
		obj = dict()

		obj['lat1'] = self.lat1
		obj['long1'] = self.lng1

		obj['lat2'] = self.lat2
		obj['long2'] = self.lng2

		obj['speed'] = self.speed
		obj['timestamp'] = str(self.timestamp)

		obj['link'] = self.link

		obj['qName'] = self.qName

		return obj










