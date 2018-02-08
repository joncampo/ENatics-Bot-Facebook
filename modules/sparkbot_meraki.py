#!/usr/bin/env python
import requests
import json
import time
import sys

# Disable all warning messages since we're dealing with a
# self-signed certificate on APIC-EM
requests.packages.urllib3.disable_warnings()

'''
#################################################################################################################################################################
ENatics is a beta project about Software Defined Networking, and created by Jon Warner Campo. For any issues or concerns, you may email him at joncampo@cisco.com.
See Terms of Service - https://arcane-spire-45844.herokuapp.com/terms
See Privacy Policy - https://arcane-spire-45844.herokuapp.com/privacy
#################################################################################################################################################################
'''

########################################################################
def meraki_org(BASE_URL,MERAKI_TKN):
    FULL_URL = 'https://'+BASE_URL+'/api/v0/organizations'
    
    headers = {
                'content-type': 'application/json',
                'X-Cisco-Meraki-API-Key': MERAKI_TKN
            }



    response = requests.get(FULL_URL, headers=headers, verify=False, timeout=5.0).json()
    org_id=response[0]['id']
    org_name= response[0]['name']

    return org_id, org_name

########################################################################

def meraki_network(BASE_URL,MERAKI_TKN,MERAKI_ORG_ID):
    FULL_URL = 'https://'+BASE_URL+'/api/v0/organizations/'+MERAKI_ORG_ID+'/networks'
    
    headers = {
                'content-type': 'application/json',
                'X-Cisco-Meraki-API-Key': MERAKI_TKN
            }



    response = requests.get(FULL_URL, headers=headers, verify=False, timeout=5.0).json()  
    
    num=1
    line_item=[]
    dictionary_item={}

    for i in response:
        item=str(num)+". "+i["name"]+" - "+i["id"]+" - "+i["timeZone"]

        dictionary_item.update({str(num):str(i["id"])})
     #line_item.update(dictionary_item)
     #line_item.append(inside_item)
        line_item.append(item)
        num = num + 1

    if response:
        return line_item, dictionary_item

###########################################################################


def meraki_network_devices(BASE_URL,MERAKI_TKN,MERAKI_NTW_ID):
    FULL_URL = 'https://'+BASE_URL+'/api/v0/networks/'+MERAKI_NTW_ID+'/devices'

    headers = {
                'content-type': 'application/json',
                'X-Cisco-Meraki-API-Key': MERAKI_TKN
            }



    response = requests.get(FULL_URL, headers=headers, verify=False, timeout=5.0).json()
    
    if response:
        config=json.dumps(response, indent = 4, separators = (",",":"))
        #print (config)
        return config
    else:
        return "No Devices Detected"

    

###########################################################################


def meraki_network_ssid(BASE_URL,MERAKI_TKN,MERAKI_NTW_ID):
    FULL_URL = 'https://'+BASE_URL+'/api/v0/networks/'+MERAKI_NTW_ID+'/ssids'

    headers = {
                'content-type': 'application/json',
                'X-Cisco-Meraki-API-Key': MERAKI_TKN
            }



    response = requests.get(FULL_URL, headers=headers, verify=False, timeout=5.0).json()
    
    if response:
        config=json.dumps(response, indent = 4, separators = (",",":"))
        #print (config)
        return config
    else:
        return "No SSIDs Detected"