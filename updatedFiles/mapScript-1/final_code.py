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

filename = 'interpreter.json'
API_KEY = "yzxo7kcqvxe75s81gh97g1qlq5g8v5mt"
node_to_crd = dict()

def authDatabase(DB_name, col_name):
	client = MongoClient("localhost", 27017)
	db = client[DB_name]
	col1 = db[col_name]
	
	return col1

def get_coordinates(lat, lng, radius):

	# http://www.overpass-api.de/api/interpreter?data=[out:json];way(around:500, 28.527574, 77.224038)[%22highway%22];(._;%3E;);out;
	r = requests.get("http://www.overpass-api.de/api/interpreter?data=[out:json];way(around:" + str(radius) + "," + str(lat) + "," + str(lng) + ")[%22highway%22];(._;%3E;);out;", allow_redirects=True)

	open(filename, 'wb').write(r.content)

	json_data = open(filename)
	return json.load(json_data)

def init_database():
	points = authDatabase("BTP", "Points")
	roads = authDatabase("BTP", "Roads")

	points.remove()
	roads.remove()

	return points,roads

def check_level(foo):
	return foo == 'primary_link' or foo == 'tertiary_link' or foo == 'service' or foo == 'trunk' or foo == 'primary' or foo == 'secondary_link' or foo == 'tertiary' or foo == 'secondary'

def add_to_database(data, points, roads):
	count = 0

	for k in data["elements"]:
		if k['type'] == 'node':
			points.insert_one(k)
		elif k['type'] == 'way':
			foo = k['tags']['highway']
			if check_level(foo):
				count += 1
				roads.insert_one(k)

	print "number of roads found = ", count

	return count

def convert_to_coordinates(nodes,points):
	coordinate_arr = []

	for i in nodes:
		arr = []
		flag = 0

		if i not in node_to_crd:
			for j in points.find():
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

	return coordinate_arr

def change_format(arr):
	return str(arr[1])+','+str(arr[0])

def get_speed_arr(points, nodes):

	curr_time = int(time.time())+1000 # +1000 since traffic data is always future values
	i = 0

	coordinate_arr = convert_to_coordinates(nodes,points)
	speed_arr = []

	new_coordinate_arr = []


	for crd in coordinate_arr:

		i+=1
		if i == len(coordinate_arr):
			break
		# "https://apis.mapmyindia.com/advancedmaps/v1/yzxo7kcqvxe75s81gh97g1qlq5g8v5mt/distance?center=28.5410967,77.231977&pts=28.5409031,77.2348124&with_traffic=1"
		r = requests.get("https://apis.mapmyindia.com/advancedmaps/v1/" + API_KEY + "/distance?center=" +  change_format(crd) + "&pts=" + change_format(coordinate_arr[-1]) + "&with_traffic=1")

		dist = r.json()['results'][0]['length']
		duration = r.json()['results'][0]['duration']

		speed = 1.0*(dist*18)/ (duration*5)

		print "coordinates: ",  "speed: ", speed

		speed_arr.append(speed)

	return  coordinate_arr,speed_arr



def find_speeds(points, roads):

	final_arr = []

	for road in roads.find():
		coordinate_arr,speed_arr = get_speed_arr(points, road['nodes']) # [ lat, lng, speed ]

		for z in range(0,len(speed_arr)):
			temp = []
			temp.append(coordinate_arr[z][0])
			temp.append(coordinate_arr[z][1])
			temp.append(coordinate_arr[z+1][0])
			temp.append(coordinate_arr[z+1][1])
			temp.append(speed_arr[z])
			final_arr.append(temp)

	return final_arr


def main1(lat, lng, radius):
	#trial purpose
	# lat = 28.527574
	# lng = 77.224038
	# radius = 500

	# lat,lng,radius = get_input()

	print 'in main'
	data = get_coordinates(lat, lng, radius)
	points,roads = init_database()


	count = add_to_database(data,points,roads)

	final_arr = find_speeds(points,roads)

	return final_arr


# main()