import json
import time
import os
import requests
import random
from serial_process import *

last_connection_time = time.time() # Track the last connection time
last_update_time = time.time()     # Track the last update time
posting_interval = 30             # Post data once every 20 seconds
update_interval = 10               # Update once every 10 seconds

# PM - T - RH - DEV 1
write_api_key1_1 = "RLXOENNREQZ7GFOQ"         # Replace YOUR-CHANNEL-write_api_key with your channel write API key
channel1_1_ID = "2543048"                     # Replace YOUR-channel_ID with your channel ID

# PM - T - RH - DEV 2
write_api_key2_1 = "YQEZI14UCRPQKJEC"         # Replace YOUR-CHANNEL-write_api_key with your channel write API key
channel2_1_ID = "2543052"                     # Replace YOUR-channel_ID with your channel ID

# Gas sensor - DEV 1
write_api_key1_2 = "145RUE1MKJQT4K2R"         # Replace YOUR-CHANNEL-write_api_key with your channel write API key
channel1_2_ID = "2543193"                     # Replace YOUR-channel_ID with your channel ID

# Gas sensor - DEV 2
write_api_key2_2 = "7X38Q82UJ7LX5II1"         # Replace YOUR-CHANNEL-write_api_key with your channel write API key
channel2_2_ID = "2543195"              # Replace YOUR-channel_ID with your channel ID

url1_1 = "https://api.thingspeak.com/channels/" + channel1_1_ID + "/bulk_update.json" # ThingSpeak server settings
url2_1 = "https://api.thingspeak.com/channels/" + channel2_1_ID + "/bulk_update.json" # ThingSpeak server settings
url1_2 = "https://api.thingspeak.com/channels/" + channel1_2_ID + "/bulk_update.json" # ThingSpeak server settings
url2_2 = "https://api.thingspeak.com/channels/" + channel2_2_ID + "/bulk_update.json" # ThingSpeak server settings
message_buffer1_1 = []
message_buffer2_1 = []
message_buffer1_2 = []
message_buffer2_2 = []

TOKEN = "*******"
chat_id = "******"

def mess_alarm_ch4(channel, ch4_data):
    message_CH4 = "CH4 vượt ngưỡng - " + "Thiết bị :" + str(channel) + "-- Nồng độ :" + str(ch4_data)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message_CH4}"
    print(requests.get(url).json()) # this sends the message

def httpRequest():
# Function to send the POST request to ThingSpeak channel for bulk update.
    global message_buffer1_1
    global message_buffer1_2
    global message_buffer2_1
    global message_buffer2_2

    # Channel 1_1
    bulk_data = json.dumps({'write_api_key':write_api_key1_1,'updates':message_buffer1_1}) # Format the json data buffer
    request_headers = {"User-Agent":"mw.doc.bulk-update (Raspberry Pi)","Content-Type":"application/json","Content-Length":str(len(bulk_data))}
    print(bulk_data)
# Make the request to ThingSpeak 
    try:
        print(request_headers)
        response = requests.post(url1_1,headers=request_headers,data=bulk_data)
        print (response) # A 202 indicates that the server has accepted the request
    except e:
        print(e.code) # Print the error code
    message_buffer1_1 = [] # Reinitialize the message buffer

    # Channel 1_2
    bulk_data = json.dumps({'write_api_key':write_api_key1_2,'updates':message_buffer1_2}) # Format the json data buffer
    request_headers = {"User-Agent":"mw.doc.bulk-update (Raspberry Pi)","Content-Type":"application/json","Content-Length":str(len(bulk_data))}
    print(bulk_data)
# Make the request to ThingSpeak 
    try:
        print(request_headers)
        response = requests.post(url1_2,headers=request_headers,data=bulk_data)
        print (response) # A 202 indicates that the server has accepted the request
    except e:
        print(e.code) # Print the error code
    message_buffer1_2 = [] # Reinitialize the message buffer.

    # Channel 2_1
    bulk_data = json.dumps({'write_api_key':write_api_key2_1,'updates':message_buffer2_1}) # Format the json data buffer
    request_headers = {"User-Agent":"mw.doc.bulk-update (Raspberry Pi)","Content-Type":"application/json","Content-Length":str(len(bulk_data))}
    print(bulk_data)
# Make the request to ThingSpeak 
    try:
        print(request_headers)
        response = requests.post(url2_1,headers=request_headers,data=bulk_data)
        print (response) # A 202 indicates that the server has accepted the request
    except e:
        print(e.code) # Print the error code
    message_buffer2_1 = [] # Reinitialize the message buffer

    # Channel 2_2
    bulk_data = json.dumps({'write_api_key':write_api_key2_2,'updates':message_buffer2_2}) # Format the json data buffer
    request_headers = {"User-Agent":"mw.doc.bulk-update (Raspberry Pi)","Content-Type":"application/json","Content-Length":str(len(bulk_data))}
    print(bulk_data)
# Make the request to ThingSpeak 
    try:
        print(request_headers)
        response = requests.post(url2_2,headers=request_headers,data=bulk_data)
        print (response) # A 202 indicates that the server has accepted the request
    except e:
        print(e.code) # Print the error code
    message_buffer2_2 = [] # Reinitialize the message buffer

    global last_connection_time
    last_connection_time = time.time() # Update the connection time

def getData():
    tmp_cmd_arr = b""
    tmp_cmd_arr = _serial_obj.sending_queue.get()
    dev_id,so2_val, ch4_val, pm1, pm2_5, pm10, co2_val, temp_val, rh_val, co_val, o3_val, no2_val = struct.unpack(">BHHHHHHHHHHH", tmp_cmd_arr[1:])

    return dev_id, so2_val, ch4_val, pm1, pm2_5, pm10, co2_val, temp_val, rh_val, co_val, o3_val, no2_val

def updatesJson():
    # Function to update the message buffer every 15 seconds with data. 
    # And then call the httpRequest function every 2 minutes. 
    # This examples uses the relative timestamp as it uses the "delta_t" parameter.
    # If your device has a real-time clock, you can also provide the absolute timestamp 
    # using the "created_at" parameter.

    global last_update_time
    message1 = {}
    message2 = {}
    message1['delta_t'] = int(round(time.time() - last_update_time))
    message2['delta_t'] = int(round(time.time() - last_update_time))
    dev_id, so2_val, ch4_val, pm1, pm2_5, pm10, co2_val, temp_val, rh_val, co_val, o3_val, no2_val = getData()
    message1['field1'] = pm1
    message1['field2'] = pm2_5
    message1['field3'] = pm10
    message1['field4'] = (temp_val - 500) * 0.1
    message1['field5'] = rh_val

    message2['field1'] = co_val * 0.1
    message2['field2'] = no2_val * 0.01
    message2['field3'] = so2_val * 0.1
    message2['field4'] = o3_val * 0.01
    message2['field5'] = ch4_val
    message2['field6'] = co2_val

    print(dev_id)
    if (dev_id) == 1:
        global message_buffer1_1
        global message_buffer1_2
        message_buffer1_1.append(message1)
        message_buffer1_2.append(message2)
        print(message_buffer1_1)
        print(message_buffer1_2)
    elif dev_id == b'\x02':
        global message_buffer2_1
        global message_buffer2_2
        message_buffer2_1.append(message1)
        message_buffer2_2.append(message2)

    last_update_time = time.time()
    if(ch4_val > 500):
        mess_alarm_ch4(dev_id, ch4_val)
            
if __name__ == "__main__":  # To ensure that this is run directly and does not run when imported
    logging.basicConfig(level=logging.DEBUG)
    _serial_obj = serial_process(com_port='COM28')
    _serial_obj.start()
    try :
        while True:
            # If posting interval time has crossed  update the ThingSpeak channel with your data
            if (time.time() - last_connection_time) >= posting_interval:
                httpRequest()
                mess_alarm_ch4(1, 100)
            # # If update interval time has crossed 15 seconds update the message buffer with data
            # if (time.time() - last_update_time) >= update_interval:
            #     updatesJson()
            if _serial_obj.sending_queue.empty() is False:
                updatesJson()

    except KeyboardInterrupt as e:
        _serial_obj.stop()
        print("Ok ok, quitting")
        sys.exit(1)

