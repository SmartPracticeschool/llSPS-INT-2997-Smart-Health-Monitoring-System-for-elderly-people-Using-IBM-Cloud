import time
import sys
import ibmiotf.application
import ibmiotf.device
import random
import requests
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
#This whole code is written to send random sensor values to the IBM IoT Platform using python code.
organization = "9qi5tr"
deviceType = "Arduino_UNO"
deviceId = "rajatgarg23"
authMethod = "token"
authToken = "rajatgarg23"

client = Cloudant("8a283a5c-ef0c-4041-b98c-9d078da7c109-bluemix", "4bdb994d74e2e47f887503f11c4d01113fbcb5440ed38938eeb5e0748430f4ec", url="https://8a283a5c-ef0c-4041-b98c-9d078da7c109-bluemix:4bdb994d74e2e47f887503f11c4d01113fbcb5440ed38938eeb5e0748430f4ec@8a283a5c-ef0c-4041-b98c-9d078da7c109-bluemix.cloudantnosqldb.appdomain.cloud")
client.connect()
database_name = "health_status_database1"
my_database = client.create_database(database_name)

if my_database.exists():
   print(f"'{database_name}' successfully created.")
   
def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data)#Commands
        

try:
    deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
    deviceCli = ibmiotf.device.Client(deviceOptions)
    
except Exception as e:
    print("Caught exception connecting device: %s" % str(e))
    sys.exit()

deviceCli.connect()

while True:
        # Generating randon temperature values and pulse rates to imitate a real sensor.
        pul=random.randint(75, 150)
        temp =random.randint(35, 40)
        #Send Temperature & Humidity to IBM Watson
        data = { 'Temperature' : temp, 'Pulse': pul }
        def myOnPublishCallback():
            print ("Published Temperature = %s C" % temp, "Pulse = %s/min" % pul, "to IBM Watson")
        if temp>=39 or pul>=140:
           r = requests.get('https://www.fast2sms.com/dev/bulk?authorization=cCvHOrINxf9ihdwUZR8TMgqu6p3K4zbyGsQa1eEWmJLDntXlP50hHUf7noyksJcMatWgwv8Ape4dLz59&sender_id=FSTSMS&message=Check%20your%20health%20status%20immediately&language=english&route=p&numbers=8755183933')
           # To send warning notification.
           # The contact no. of patient's doctor or loved ones can also be added, so that they also get notified.
           print(r.status_code)
        success = deviceCli.publishEvent("Health_Status", "json", data, qos=0, on_publish=myOnPublishCallback)
        if not success:
            print("Not connected to IoTF")
        time.sleep(2)
        
        deviceCli.commandCallback = myCommandCallback

        record={"Body Temperature":"%s C" % temp,"Pulse Rate":"%s/min" % pul}
        new_document = my_database.create_document(record)

if new_document.exists():
     print("Document successfully created.")        

result_collection = Result(my_database.all_docs,include_docs=True)
print(f"Retrieved minimal document:\n{result_collection[0]}\n")

# Disconnect the device and application from the cloud
deviceCli.disconnect()

