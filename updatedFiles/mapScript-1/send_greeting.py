from selenium import webdriver
from time import sleep
import pandas as pd




def filter_contacts(filename):
    all_contacts = pd.read_csv(filename)
    all_contacts = all_contacts[["Name", "Given Name"]]
    # print("Type Given name if you wish to include them in your Diwali Spam list.")
    # print("To break, Enter x")
    # print("To keep it same as the given name(the one after -), press f")
    wishing_contacts = dict()
    for index, row in all_contacts.iterrows():
        print(str(row['Name'])+"  -  "+str(row['Given Name']))
        # y = input()
        # if y == 'x':
        #     break
        # if y == 'f':
        #     wishing_contacts[str(row['Name'])] = str(row['Given Name'])
        # elif y != '':
        #     wishing_contacts[str(row['Name'])] = y
        wishing_contacts[str(row['Name'])] = "SampleText"
    return wishing_contacts



def irritatePeopleStart(queryName,uId):

    iterations=1

    for z in range(0,iterations):

        for key, value in wishingContacts.items():

            print (key, value)

            if (key == uId):

                pre_msg = "Results for query - "
                message = queryName

                input_box = driver.find_element_by_css_selector("input[type='text']")
                input_box.click()
                input_box.send_keys(key)
                sleep(1)
                userbox = driver.find_element_by_css_selector("span[title='"+key+"']")
                userbox.click()
                inputbox = driver.find_element_by_css_selector("div[data-tab='1']")
                inputbox.click()
                inputbox.send_keys(pre_msg+message)
                send_button = driver.find_element_by_css_selector("span[data-icon='send']")
                send_button.click()
                sleep(1)




def irritatePeople(long1,lat1,long2,lat2,speed,uId):

    iterations=1

    for z in range(0,iterations):

        for key, value in wishingContacts.items():

            print (key, value)

            if (key == uId):

                pre_msg = "https://www.google.com/maps/dir/"
                message = str(lat1) + "," + str(long1) + "/" + str(lat2) + "," + str(long2) + "\n\n"
                post_msg = "Traffic Level = " + str(speed) + "."
                input_box = driver.find_element_by_css_selector("input[type='text']")
                input_box.click()
                input_box.send_keys(key)
                sleep(1)
                userbox = driver.find_element_by_css_selector("span[title='"+key+"']")
                userbox.click()
                inputbox = driver.find_element_by_css_selector("div[data-tab='1']")
                inputbox.click()
                inputbox.send_keys(pre_msg+message+post_msg)
                send_button = driver.find_element_by_css_selector("span[data-icon='send']")
                send_button.click()
                sleep(1)



wishingContacts = filter_contacts("google.csv")
driver = webdriver.Chrome('/Users/varnitjain/Desktop/mapScript-1/chromedriver')
driver.get('https://web.whatsapp.com')
sleep(2)
contacts = dict()

# https://www.google.com/maps/dir/28.551061,77.257859/28.558974,77.273544

# Traffic Level - 10
# Sarojini Marg to Okhla Phase 3




