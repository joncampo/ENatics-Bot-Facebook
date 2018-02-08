#!/usr/bin/python3
'''
#################################################################################################################################################################
ENatics is a beta project about Software Defined Networking, and created by Jon Warner Campo. For any issues or concerns, you may email him at joncampo@cisco.com.
See Terms of Service - https://arcane-spire-45844.herokuapp.com/terms
See Privacy Policy - https://arcane-spire-45844.herokuapp.com/privacy
#################################################################################################################################################################
'''
# Import necessary modules
from pprint import pprint
import requests
import json
import sys
import subprocess
import platform
import zipfile
import logging
import time
import os
import argparse
from shutil import copyfile
from requests_toolbelt.multipart.encoder import MultipartEncoder
from PIL import Image
from ncclient import manager
import xml.dom.minidom

from flask import Flask, request, render_template, url_for
#####################Settings

from settings import get_settings

settings=get_settings()

PAGE_ACCESS_TOKEN = settings[0]
APIC_EM_BASE_URL = settings[1]
APIC_EM_USER = settings[2]
APIC_EM_PASS = settings[3]
CMX_BASE_URL = settings[4]
CMX_Auth = settings[5]
MERAKI_BASE_URL = settings[6]
MERAKI_TOKEN = settings[7]
VERIFY_TOKEN=settings[8]
CSR1KV = settings[9]
NETCONF_PORT = settings[10]
NETCONF_USER = settings[11]
NETCONF_PASS = settings[12]
google_token = settings[13]

Spark_Base_URL = "https://api.ciscospark.com/v1"


#####################APIC-EM

from modules.sparkbot_apic_em import apic_em_getDevices, apic_em_checkStatus, apic_em_getConfig, apic_em_getDetails

#####################CMX

from modules.sparkbot_cmx import cmx_map_download, cmx_list_client, cmx_client_info, cmx_list_floors, cmx_collect_client, cmx_collect_zones, cmx_edit_map, get_floor_id

#####################meraki

from modules.sparkbot_meraki import meraki_org, meraki_network, meraki_network_devices, meraki_network_ssid

#####################netconf

from modules.sparkbot_netconf import netconf_get_interface

#####################google

from modules.sparkbot_google import googling

#####################FB send text message
def send_message(recipient_id, message_text):

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
            "quick_replies":[
		      {
		        "content_type":"text",
		        "title":"list devices",
		        "payload":"list devices"
		      },
			  {
		        "content_type":"text",
		        "title":"list users",
		        "payload":"list users"
		      },
			  {
		        "content_type":"text",
		        "title":"list floors",
		        "payload":"list floors"
		      },
			  {
		        "content_type":"text",
		        "title":"list meraki",
		        "payload":"list meraki"
		      },	  
			  {
		        "content_type":"text",
		        "title":"netconf interface",
		        "payload":"netconf interface"
		      },
		      {
		        "content_type":"text",
		        "title":"google Cisco DNA",
		        "payload":"google Cisco DNA"
		      },
		      {
		        "content_type":"text",
		        "title":"about",
		        "payload":"about"
		      },
		      {
		        "content_type":"text",
		        "title":"help",
		        "payload":"help"
		      }	  	  
		    ]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)

#####################FB send media message

def send_media(imagepath):
    
    address=''.join(('https://graph.facebook.com/v2.6/me/message_attachments?access_token=', PAGE_ACCESS_TOKEN))
    data = {'message': '{"attachment":{"type":"image", "payload":{"is_reusable":"true"}}}'}

    files = { "filedata" : (imagepath, open(imagepath, 'rb'), 'image/png') }

    r = requests.post(address, data=data,files=files).json()
    attach_id=r['attachment_id']
    print ("Attachment ID is: ",attach_id)
    return attach_id

def send_attachment_id(recipient_id, attach_id):

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
                "attachment":{
                    "type":"image", 
                    "payload":{
                        "attachment_id": attach_id
                    }
                }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    print (r)


#####################Business Logic
class global_command():
	def handle_text(senders_id,cmd):

		result = None
		cmd=cmd.lower()
		

		if 'hi' in cmd:
			#result="Hi <@personEmail:"+senders_email+">"
			result="Hi"
		elif 'hello' in cmd:
			#result="Hello <@personEmail:"+senders_email+">"
			result="Hello"
		
		elif 'thank' in cmd:
			result="Your Welcome!"

		elif 'help' in cmd:
			result="Please see list of commands below:\n\n\n" \
			"\"list devices\" - shows devices managed by APIC-EM and has options for configuration and device details\n\n" \
			"\"list users\" - shows active users and option for location of user on map managed by CMX Location Analytics\n\n" \
			"\"list floors\" - shows all the floors managed by CMX Location Analytics and has 2 options: location of all the users in each floor and zones (restroom)\n\n" \
			"\"list meraki\" - shows meraki networks and has 2 options: devices inside a network and SSIDs\n\n" \
			"\"netconf interface - shows the netconf yang model of a cisco interface\n\n" \
			"\"google <Cisco search item>\" - ENatics will search the Cisco.com site for links and references of search item\n\n" \
			"\"about\" - information about the ENatics Bot\n\n"
			send_to_page=send_attachment_id(senders_id, '148937319101918')


		elif 'about' in cmd:
			result="Hello I'm ENatics! I'm here to help you manage your network easily by tapping the full potential of all the APIs inside your network! I'm currently on version 1 \n\nI'm created by Jon Warner Campo of Cisco GVE and you can reach him at joncampo@cisco.com. Your feedback is most welcome. \n\nThank you and I hope you appreciate my service! "\
			"See Terms of Service - https://arcane-spire-45844.herokuapp.com/terms\n"\
			"See Privacy Policy - https://arcane-spire-45844.herokuapp.com/privacy"

		elif 'network status' in cmd or 'list devices' in cmd or 'list device' in cmd:
			send_message(senders_id, "Got it! Please wait...")
			#spark_send_message(BOT_SPARK_TOKEN, room_id, "Got it <@personEmail:"+senders_email+">. Please wait.")
			ticket=apic_em_checkStatus(APIC_EM_BASE_URL,APIC_EM_USER,APIC_EM_PASS)
			
			if ticket[0]:
				global_command.apic_ticket=ticket[1]
				global_command.raw_result=apic_em_getDevices(APIC_EM_BASE_URL,global_command.apic_ticket)
				welcome_text="Hi Please see your requested Network Status Summary (hostname-model-status):\n"
				ending_text="\n\n\nType \"config #\" to get config (ex. config 1)\n\nType \"details #\" to get devices details (ex. details 1)"
				result=welcome_text+"\n".join(str(x) for x in global_command.raw_result[0])+ending_text

			else:
				result="\n\nFailed to Connect to APIC-EM \n\n"

		elif 'config' in cmd:
			config_text=cmd.split()
			var_num=len(config_text)-1

			try: 
				config_num=config_text[var_num]
				place_num = int(config_num) - 1
				int(global_command.raw_result[2])
			except:
				result="\n\nError found! Please retry sending the command\n\n"
				return result

			if int(place_num) >= 0 and int(place_num) < int(global_command.raw_result[2]):
				send_message(senders_id, "Got it! Please wait...")
				device_id=global_command.raw_result[1][int(place_num)][str(config_num)]
				config=apic_em_getConfig(APIC_EM_BASE_URL,global_command.apic_ticket,device_id)
				config_split=config.split("\n\n\n\n\n\n\n\n")
				num=0
				while num < len(config_split):
					print (config_split[num])
					send_message(senders_id, config_split[num])
					num=num+1
				result="End of config"

			else:
				result="\n\nPlease choose a correct number within list\n\n"
		
		elif 'details' in cmd or 'detail' in cmd:
			config_text=cmd.split()
			var_num=len(config_text)-1
			try: 
				config_num=config_text[var_num]
				place_num = int(config_num) - 1
				int(global_command.raw_result[2])
			except:
				result="\n\nError found! Please retry sending the command\n\n"
				return result

			if int(place_num) >= 0 and int(place_num) < int(global_command.raw_result[2]):
				send_message(senders_id, "Got it! Please wait...")
				device_id=global_command.raw_result[1][int(place_num)][str(config_num)]
				result=apic_em_getDetails(APIC_EM_BASE_URL,global_command.apic_ticket,device_id)
			else:
				result="\n\nPlease choose a correct number within list\n\n"
		
		elif 'list wireless devices' in cmd or 'list wireless' in cmd or 'list wireless users' in cmd or 'list users' in cmd or 'list user' in cmd:

			global_command.raw_cmx_list_users=cmx_list_client(CMX_BASE_URL,CMX_Auth)
			#result=cmx_list_users
			#print (raw_cmx_list_users)
			welcome_text="Hi Please see your requested Wireless Devices:\n"
			ending_text="\n\n\nType locate user # to get user location details (ex. locate user 1)"
			result=welcome_text+"\n".join(str(x) for x in global_command.raw_cmx_list_users[0])+ending_text

		elif 'list floors' in cmd or 'list floor' in cmd:

			global_command.raw_cmx_list_floors=cmx_list_floors(CMX_BASE_URL,CMX_Auth)
			#result=cmx_list_users
			#print (raw_cmx_list_floors)
			welcome_text="Hi Please see your requested list of floors:\n"
			ending_text="\n\n\nType \"floor # users\" to get location of users in a floor (ex. floor 1 users)\n\nType \"floor # restroom\" to get location of users in a floor"
			result=welcome_text+"\n".join(str(x) for x in global_command.raw_cmx_list_floors[0])+ending_text
		
		elif 'locate user' in cmd or 'locate device' in cmd:
			config_text=cmd.split()
			var_num=len(config_text)-1
			config_num=config_text[var_num]

			if "user" in config_num:
				result="\n\nPlease choose a correct number within list\n\n"
				return result

			try: 
				total_users=len(global_command.raw_cmx_list_users[1])
			except:
				result="\n\nError found! Please retry sending the command\n\n"
				return result

			if int(config_num) >= 1 and int(config_num) <= total_users:
				cmx_user=global_command.raw_cmx_list_users[1][str(config_num)]
				send_message(senders_id, "Got it! Please wait...")
				#print (cmx_user)
				cmx_client_details=cmx_client_info(CMX_BASE_URL,CMX_Auth,cmx_user)

				if cmx_client_details[0] is True:
					content_filename="temp/map2.png"
					try:
						upload_id=send_media(content_filename)
						send_to_page=send_attachment_id(senders_id,upload_id)
						print ("upload successful!")
						result="User "+cmx_user+"(Red Pin) is found!"
					except:
						result="Error Uploading Map"

			else:
				result="\n\nPlease choose a correct number within list\n\n"



		elif 'floor' in cmd:
			config_text=cmd.split()
			#print ("config")
			#print (config_text[1])
			var_num=len(config_text)-2
			var_num2=len(config_text)-1
			#if type(config_text[1]) == int:
			config_command=config_text[var_num2]
			config_num=config_text[var_num]
			#elif type(config_text[2]) == int:
			#	config_num=config_text[2]
			if "floor" in config_num:
				result="\n\nPlease choose a correct number within list\n\n"
				return result
			try: 
				total_users=len(global_command.raw_cmx_list_floors[1])
				send_message(senders_id, "Got it! Please wait...")
			except:
				result="\n\nError found! Please retry sending the command\n\n"
				return result

			if "restroom" in config_command or "restrooms" in config_command:
				if int(config_num) >= 1 and int(config_num) <= total_users:
					floor=global_command.raw_cmx_list_floors[1][str(config_num)]

					floor_normalized=(floor.replace(">","/"))
					cmx_floor_clients=cmx_collect_zones(CMX_BASE_URL,CMX_Auth,floor_normalized)
					if cmx_floor_clients is True:
						content_filename="temp/map2.png"
						try:
							upload_id=send_media(content_filename)
							send_to_page=send_attachment_id(senders_id,upload_id)
							print ("upload successful!")
							result="Restroom(s) (GREEN BOX) Found!"
						except:
							result="Error Uploading Map"
						
					else:
						result="\n\nSorry No restroom in floor!\n\n"
				else:
					result="\n\nPlease choose a correct number within list\n\n"

			elif "users" in config_command or "user" in config_command:	
				
				if int(config_num) >= 1 and int(config_num) <= len(global_command.raw_cmx_list_floors[1]):
					floor=global_command.raw_cmx_list_floors[1][str(config_num)]				
					send_message(senders_id, "Locating users and Downloading Map. Please wait...")

					floor_normalized=(floor.replace(">","/"))
					floor_id=get_floor_id(CMX_BASE_URL,CMX_Auth,floor_normalized)

					if floor_id[0] is True:
						print ("processing ",floor_id[1])
						cmx_floor_clients=cmx_collect_client(CMX_BASE_URL,CMX_Auth,floor_id[1])

						if cmx_floor_clients[0] is True:
							print("editing maps")
							users_x=cmx_floor_clients[1]
							users_y=cmx_floor_clients[2]
							total=len(users_x)
							#print (len(users_x),"user(s) detected!")
							send_message(senders_id, "Processing "+str(total)+" users on map! Please wait...")

							cmx_edit=cmx_edit_map(users_x,users_y,bundle=1)
							print ("Uploading to FB")
							content_filename="temp/map2.png"
							try:
								upload_id=send_media(content_filename)
								send_to_page=send_attachment_id(senders_id,upload_id)
								print ("upload successful!")
								result="Number of Active Users (Red Pin) on \n\n"+floor+": "+str(total)
							except:
								result="Error Uploading Map"
									
						else:
							result="\n\nSorry No users found!\n\n"
					else:
						result="\n\nError on Maps!\n\n"
				else:
					result="\n\nPlease choose a correct number within list\n\n"


		elif 'list meraki network' in cmd or 'list meraki networks' in cmd or 'list meraki' in cmd:
			try:
				mrki_org=meraki_org(MERAKI_BASE_URL,MERAKI_TOKEN)
			except:
				result="Please check your Meraki token"
				return result

			mrki_org_id=str(mrki_org[0])
			mrki_org_name=mrki_org[1]
			print (mrki_org_id)
			global_command.raw_mrki_ntw=meraki_network(MERAKI_BASE_URL,MERAKI_TOKEN,mrki_org_id)
			welcome_text="Hi please see list of Meraki Network(s) under Organization **"+mrki_org_name+"**:\n"
			ending_text1="\n\nType \"meraki # devices\" to get list of Meraki Devices under chosen network. (ex. meraki 1 devices)"
			ending_text2="\n\nType \"meraki # ssid\" to get list of SSIDs under chosen network. (ex. meraki 1 ssid)"
			result=welcome_text+"\n".join(str(x) for x in global_command.raw_mrki_ntw[0])+ending_text1+ending_text2

		elif 'meraki' in cmd:
			config_text=cmd.split()
			#print ("config")
			#print (config_text[1])
			var_num1=len(config_text)-1
			config_command=config_text[var_num1]

			var_num2=len(config_text)-2
			config_num=config_text[var_num2]

			if "meraki" in config_num:
				result="\n\nPlease choose a correct number within list\n\n"
				return result

			try: 
				total_users=len(global_command.raw_mrki_ntw[1])
			except:
				result="\n\nError found! Please retry sending the command\n\n"
				return result

			if "device" in config_command or "devices" in config_command:
				if int(config_num) >= 1 and int(config_num) <= total_users:
					send_message(senders_id, "Got it! Please wait...")
					meraki_network_id_chosen=global_command.raw_mrki_ntw[1][config_num]
					welcome_text="Please see list of Meraki Devices under Network ID **"+meraki_network_id_chosen+"**:\n\n"
					result=welcome_text+meraki_network_devices(MERAKI_BASE_URL,MERAKI_TOKEN,meraki_network_id_chosen)
				else:
					result="\n\nPlease choose a correct number within list\n\n"
			
			elif "ssid" in config_command or "ssids" in config_command:
				if int(config_num) >= 1 and int(config_num) <= total_users:
					send_message(senders_id, "Got it! Please wait...")
					meraki_network_id_chosen=global_command.raw_mrki_ntw[1][config_num]
					result="End of SSID List"
					config=meraki_network_ssid(MERAKI_BASE_URL,MERAKI_TOKEN,meraki_network_id_chosen)
				
					config_split=config.split("number")
					num=0
					while num < len(config_split):
						print (config_split[num])
						send_message(senders_id, config_split[num])
						num=num+1
					result="End of config"


				else:
					result="\n\nPlease choose a correct number within list\n\n"

		elif 'netconf interface' in cmd or 'yang interface' in cmd:

			send_message(senders_id, "Got it! Please wait...")
			netconf_result_raw=netconf_get_interface(CSR1KV, NETCONF_PORT, NETCONF_USER, NETCONF_PASS)
			netconf_result=(xml.dom.minidom.parseString(netconf_result_raw.xml).toprettyxml())

			netconf_result_split=netconf_result.split("</interface>")
			num=0
			while num < len(netconf_result_split):
				print (netconf_result_split[num])
				send_message(senders_id, netconf_result_split[num])
				num=num+1

			result="End of config"


		elif 'reference' in cmd or 'google' in cmd:
			send_message(senders_id, "Got it! Please wait...")
			config_text=cmd.split()
			del config_text[0]
			if config_text is None:
				result="Please provide a search term! ex. google catalyst 9000"
				return result
			else:
				search_string=" ".join(config_text)
			
			google_result=googling(google_token,search_string)
			print(google_result)
			send_message(senders_id, "Hi Please see your requested references for "+search_string)
			total_result=len(google_result)
			num=0
			while num < total_result:
				send_message(senders_id, google_result[num])
				num=num+1

			result="End of result!\n\n To search more, just type google \"cisco search item\" (ex. google Catalyst 9000)"


		if result == None:
			result = "I did not understand your request. Please type *help* to see what I can do"

		return result

#####################App - that waits for get or post
app = Flask(__name__)
@app.route('/', methods=['POST'])
def fb_webhook():

   # endpoint for processing incoming messaging events

    data = request.get_json()
    print(data) # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
    	
        for entry in data["entry"]:
            page_id=entry["id"]
            for messaging_event in entry["messaging"]:
                
                if messaging_event.get("message"):  # someone sent us a message
                    msg=None
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if sender_id != page_id:
                        msg = global_command.handle_text(sender_id,message_text)
                        if msg != None:
                            send_message(sender_id, msg)
                    else:
                        pass
                
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
		
    return "ok", 200


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        #if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/terms', methods=['GET'])
def terms():
	terms_service = open('legal/terms_and_conditions.txt', 'r') 
	terms=terms_service.read() 
	print ("Terms of Service")

	message = "<html>%s</html>" % terms

	return message, 200

@app.route('/privacy', methods=['GET'])
def privacy():
	privacy_policy = open('legal/privacy.txt', 'r') 
	privacy_pol=privacy_policy.read() 
	print ("privacy_pol")

	message = "<html>%s</html>" % privacy_pol

	return message, 200



#####################Main Function


def main():
	app.run(debug=True)

#####################Main
if __name__ == "__main__":

	main()