#!/usr/bin/env python
import requests
import json
import time
import sys


FULL_URL = "https://www.googleapis.com/customsearch/v1"
'''
#################################################################################################################################################################
ENatics is a beta project about Software Defined Networking, and created by Jon Warner Campo. For any issues or concerns, you may email him at joncampo@cisco.com.
See Terms of Service - https://arcane-spire-45844.herokuapp.com/terms
See Privacy Policy - https://arcane-spire-45844.herokuapp.com/privacy
#################################################################################################################################################################
'''

########################################################################

def googling(google_key,Search_String):
    
    querystring = {"key":google_key,"cx":"009555812553138708455:fqydizp0fum","q":Search_String}

    headers = {"Content-Type":"application/json"}
    response = requests.get(FULL_URL, headers=headers, verify=False, params=querystring).json()

    #print (response["items"])

    line_item=[]
    num=1

    for i in response["items"]:
    	#print (num)
    	#print ("Title: "+i["title"])
    	#print ("Link: "+i["link"])
    	#print ("Description: "+i["pagemap"]["metatags"][0]["og:description"])
    	#print ("Document Type: "+i["pagemap"]["metatags"][0]["doctype"])
    	#print ("Content Type: "+i["pagemap"]["metatags"][0]["contenttype"])

        line_item.append("Title: "+ i["title"])
        line_item.append("Link: "+ i["link"])
        if "og:description" in i["pagemap"]["metatags"][0]:
            line_item.append("Description: "+i["pagemap"]["metatags"][0]["og:description"])
        if "doctype" in i["pagemap"]["metatags"][0]:
            line_item.append("Document Type: "+ i["pagemap"]["metatags"][0]["doctype"])
        #if "contenttype" in i["pagemap"]["metatags"][0]:
         #line_item.append("Content Type: "+ i["pagemap"]["metatags"][0]["contenttype"]+"\n")
        line_item.append("\n\n")


    return line_item

	
	
