import sys
from database import result
from pymongo import MongoClient
from datetime import datetime
import threading
import time

client = MongoClient("localhost", 27017)
db = client["BTP"]
col1 = db["userInformation"]

result1 = result(0,1,2,3,4,"1")

print (result1.get_object_json())


db.userInformation.update({ "id" : "a" }, { "$set": { "queries.$[0].results" : result1.get_object_json() } })


# print result1.get_object_json()



# db.userInformation.update({"id.queries": "a"}, {"$push": 

# 	{

# 	"queries[0].result1s":   --> PLACE

# 	result1.get_object_json()  --> WHAT

# 	} 

# })


# def calculateTime():
# 	print ("1")
# 	time.sleep(10)
# 	print ("2")

# thread1 = threading.Thread(target = calculateTime)
# thread1.start()






