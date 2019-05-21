import json
import time
import csv
from pymongo import MongoClient
import requests
import StringIO
from flask import Flask
from flask import jsonify
from flask import make_response
import json
import send_greeting
import numpy as np
import datetime

API_KEY = "yzxo7kcqvxe75s81gh97g1qlq5g8v5mt"
# API_KEY = "pnvbw6wt2xlusals79yc9vgtx4kqojkq"
# API_KEY = "jusovlj23qmlub52pjjkfrzx5r59cx5u"


threshold = 20


def convert_to_meters(foo):
	if (foo.split(' ')[-1] == 'm'):
		return float(foo.split(' ')[0])

	elif (foo.split(' ')[-1] == 'km'):
		return float(foo.split(' ')[0])*1000
	
	else:
		return "error"


def convert_to_seconds(foo):
	if (len(foo.split(' ')) == 4):
		minutes = int(foo[0])*60 + int(foo[3])
		seconds = minutes*60
		return seconds

	elif (len(foo.split(' ')) == 2):
		# print len(foo)
		# print foo[1]
		# print foo[2]
		minutes = int(foo.split(' ')[0])
		seconds = minutes*60
		return seconds
	else:
		seconds = "error"
		return seconds


def change_format(arr):
	return str(arr[1])+','+str(arr[0])

def change_format2(arr):
	return str(arr[0])+','+str(arr[1])

# Takes the nodes and searches for its corrosponding coordinate
def convert_to_coordinates(nodes,points):
	coordinate_arr = []

	node_to_crd = dict()

	for i in nodes:
		arr = []
		flag = 0

		if i not in node_to_crd:
			for j in points:
				if i == j['id']:
					arr.append(j['lon'])
					arr.append(j['lat'])

					flag = 1
					break

		else:
			flag = 1
			arr = node_to_crd[i]
			arr.append(arr['lon'])
			arr.append(arr['lat'])
		
		if flag == 0:
			print "not able to find coordinate for this node, skipping"
		else:
			coordinate_arr.append(arr)

	# print len(coordinate_arr)
	return coordinate_arr


# Takes finds the speed for each road, between each point and the final point of the road
def get_speed_arr(points, nodes, filename):

	curr_time = int(time.time())+1000
	i = 0

	coordinate_arr = convert_to_coordinates(nodes,points)

	speed_arr = []

	new_coordinate_arr = []

	dist_arr = []
	duration_arr = []

	# print "in speed"
	for crd in coordinate_arr:

		# print "hi"
		# print change_format(crd)
		# continue

		# crd = change_format(crd)
		# print i

		i+=1
		if i == len(coordinate_arr):
			break

		# r = requests.get("https://apis.mapmyindia.com/advancedmaps/v1/" + API_KEY + "/distance_matrix/driving/" +  change_format2(crd) + ";" + change_format2(coordinate_arr[-1]))


		# dist = 1
		# duration = 1

		# for z in r:
		# 	# print type(z)
		# 	# print z

		# 	response  = json.loads(z)
		# 	duration = response["results"]["durations"]
		# 	dist = response["results"]["distances"]


		# print dist[0], duration[0]


		r = requests.get("https://apis.mapmyindia.com/advancedmaps/v1/" + API_KEY + "/distance?center=" +  change_format(crd) + "&pts=" + change_format(coordinate_arr[-1]) + "&with_traffic=1")
		# r = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + change_format(crd) + "&destinations=" + change_format(coordinates[-1]) + "&key=" + API_KEY + "&departure_time=" + str(curr_time)) 
		
		# print r.json()

		dist = r.json()['results'][0]['length']
		duration = r.json()['results'][0]['duration']

		# dist = np.array(dist)[0][1]
		# duration = np.array(duration)[0][1]




		speed = 1.0*(dist*18)/ (duration*5+1)


		dist_arr.append(dist)
		duration_arr.append(duration)
		# print "coordinates: ",  "speed: ", speed

		# print filename, ": got crd " ,i,"/",len(coordinate_arr)

		speed_arr.append(speed)

	return  coordinate_arr,speed_arr, dist_arr, duration_arr

# The main driver function
def get_bottlenecks (lat,lng, radius, level, uniqueId, shoId, qName):

	# lat = 28.527574
	# lng = 77.224038
	# radius = 500
	# level = 1


	filename = shoId+qName


	print filename, ": started running query"

	r = requests.get("http://www.overpass-api.de/api/interpreter?data=[out:json];way(around:" + str(radius) + "," + str(lat) + "," + str(lng) + ")[%22highway%22];(._;%3E;);out;", allow_redirects=True)
	
	# print type(r.content)
	# open(filename, 'wb').write(r.content)
	
	# points = authDatabase("BTP", "Points")
	# roads = authDatabase("BTP", "Roads")

	# points.remove()
	# roads.remove()

	# json_data = open(filename)
	data = json.loads(r.content)



	# print "inserting"
	# bar = dict()

	# for road in roads.find():
	# 	if road['tags']['highway'] not in bar:
	# 		bar[road['tags']['highway']] = 1
	# 	else:
	# 		bar[road['tags']['highway']] += 1

	count = 0

	points = []
	roads = []

	for k in data["elements"]:
		if k['type'] == 'node':
			points.append(k)
		elif k['type'] == 'way':
			foo = k['tags']['highway']
			if level == 1:
				if foo == 'primary' or foo == 'tertiary' or foo == 'secondary' or foo == 'trunk':
					count += 1
					roads.append(k)
			elif level == 2:
				if foo == 'primary' or foo == 'tertiary' or foo == 'secondary' or foo == 'trunk' or foo == 'primary_link' or foo == 'secondary_link' or foo == 'tertiary_link' or foo == 'trunk_link' or foo == 'service':
					count += 1
					roads.append(k)
			else:
				count += 1
				roads.append(k)

			#if foo == 'primary_link' or foo == 'tertiary_link' or foo == 'service' or foo == 'trunk' or foo == 'primary' or foo == 'tertiary' or foo == 'secondary':
			#if foo == 'trunk' or foo == 'primary' or foo == 'tertiary' or foo == 'secondary':

	# print count

	ans = 0
	total = 0

	foo = 0

	# for i in points.find():
	# 	foo += len(i['geometry']['coordinates'])


	# print foo

	newFinalArr = []

	si = StringIO.StringIO()

	bottlenecks_arr = []

	iii = 0

	#This loop finds speeds for each road
	for road in roads:
		coordinate_arr,speed_arr, dist_arr, duration_arr = get_speed_arr(points, road['nodes'], filename) # [ lat, lng, speed ]
		iii += 1
		print filename, ": roads", iii ,"/", len(roads)

		num = 0
		denom = 1

		for i in range (len(speed_arr)):
			num += dist_arr[i]*speed_arr[i]
			denom += dist_arr[i]

		avg_speed = num/denom

		for i in range (len(speed_arr)):
			if speed_arr[i] < threshold:
				bottlenecks_arr.append([coordinate_arr[i],coordinate_arr[i+1],speed_arr[i]])
		
		# if avg_speed < threshold:
		# 	bottlenecks_arr.append([coordinate_arr[0], coordinate_arr[-1], avg_speed])

	# print bottlenecks_arr
	
	chain=[]

	start = [0,0]
	end = [0,0]
	isChainEnd=1
	threshold_dist=0.005
	speed=[]

	elemNu = 0

	for i in bottlenecks_arr:


		if isChainEnd:
			start = i[0]
			end = i[1]
			isChainEnd=0
			speed.append(i[2])

		else:

			dist = ((end[0]-i[0][0])**2 + (end[1]-i[0][1])**2)**0.5

			# print dist

			if dist < threshold_dist and elemNu<len(bottlenecks_arr)-1:
				end = i[1]
				speed.append(i[2])

			else:

				dist = ((start[0]-end[0])**2 + (start[1]-end[1])**2)**0.5

				# if dist>0.001:
				# 	chain.append([start,end,sum(speed)/float(len(speed))])

				chain.append([start,end,sum(speed)/float(len(speed))])

				isChainEnd=1
				speed=[]



		elemNu+=1


	# print chain

	print filename, ": sending whatsapp " + str(len(chain)) + " messeges "


	if len(chain)!=0:
		send_greeting.irritatePeopleStart(qName,uniqueId)

	for i in chain:
		try:
			send_greeting.irritatePeople(i[0][0],i[0][1],i[1][0],i[1][1],i[2],uniqueId)
		except:
			print "passing"

	print filename, ": done sending whatsapp messeges"

	return chain




		
# def members():
# 	get_bottlenecks(28.708331, 77.124551)
# 	return "Query Successful"


# def getCoordinates(lat, lng, level, uniqueId):

# 	# allString = str(latLong)

# 	# lat = allString.split(",")[0]
# 	# lng = allString.split(",")[1]

# 	p = get_bottlenecks(lat,lng,level,uniqueId)

# 	return str(p)



