Prerequisites:-

1. Python Libraries: 
	- pymongo
	- flask
	- selenium

2. Location of the chrome driver:
Please change the absolute location of the chromedriver in line 91 of send_greetings.py


3. Install the mongodb server on your system

4. Setup google contacts
	- Download Google Contacts in a separate CSV (please stick to the format mentioned in the current CSV
	- The contact names/unique IDs should match the IDs mentioned on the website exactly.



To Run the Server:-

1. Run the mongodb server on a terminal 
	> sudo mongod

2. Open a seperate terminal window and run the flask server
	> python app.py

3. A window will pop up which requires you to perform a one-time login to your whatsapp account 
	> use your phone to login

4. The server is setup and ready to serve at localhost:5000
	> It can be accessed anywhere within the local network


