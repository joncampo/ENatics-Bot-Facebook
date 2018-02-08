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
def apic_em_checkStatus(BASE_URL,APIC_EM_USER,APIC_EM_PASS):
    FULL_URL = 'https://'+BASE_URL+'/api/v1/ticket'
    headers = {
                'content-type': 'application/json'
            }

    payload = {
                'username': APIC_EM_USER,
                'password': APIC_EM_PASS
            }

    status = requests.post(FULL_URL, headers=headers, json=payload, verify=False, timeout=5.0)
    #content = requests.post(FULL_URL, headers=headers, json=payload, verify=False, timeout=5.0).json()
    
    if status.ok:
        return [status.ok, status.json().get('response')["serviceTicket"]]
    else:
        return [status.ok, None]

########################################################################

def apic_em_getDevices(BASE_URL, ticket):
    #api = "/network-device"
    FULL_URL = "https://"+BASE_URL+"/api/v1/network-device"
    headers = {"Content-Type":"application/json", "X-Auth-Token": ticket}
    response = requests.get(FULL_URL, headers=headers, verify=False).json()
    #print (json.dumps(response, indent = 4, separators = (",",":")))
    #print (response)
    
    num = 1
    description_item=[]
    line_item=[]
    
    #print (response["response"])
    for i in response["response"]:

        if i["errorCode"] == 'null' or i["errorCode"] is None:
            dev_status="Ok"
        else:
            dev_status="Not ok"

        if ".com" in i["hostname"]:
            new_hostname = i["hostname"].replace(".com", "")
        else:
            new_hostname=i["hostname"]

        #line_item.append(str(num)+". **"+i["hostname"]+"** - "+i["platformId"]+" - "+dev_status)
        #line_item={str(num)+". **"+i["hostname"]+"** - "+i["platformId"]+" - "+dev_status:str(i["id"])}
        #inside_item={i["hostname"]:i["id"]}
        item=str(num)+". "+new_hostname+" - "+i["platformId"]+" - "+str(dev_status)
        inside_item={str(num):str(i["id"])}
        
        description_item.append(item)
        line_item.append(inside_item)
        
        num = num + 1
    return description_item,line_item, num

###########################################################################


def apic_em_getConfig(BASE_URL,ticket,id):
    #api = "/network-device"

    FULL_URL = "https://"+BASE_URL+"/api/v1/network-device/"+id+"/config"
    headers = {"Content-Type":"application/json", "X-Auth-Token": ticket}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()
    #print (json.dumps(response, indent = 4, separators = (",",":")))
    #print (response)
   
    if "response" in result:
        config=(result["response"].replace("\n!","\n"))
        #config=json.dumps(config, indent = 0, separators = ("\n","\n"))
        return config
        
    else:
        return "Configration Not Available"
        
    #config=repr(response["response"]) --> this will print \n in a given string
    
    #print (config)
    

###########################################################################


def apic_em_getDetails(BASE_URL,ticket,id):
    #api = "/network-device"

    FULL_URL = "https://"+BASE_URL+"/api/v1/network-device/"+id
    headers = {"Content-Type":"application/json", "X-Auth-Token": ticket}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()
    #print (json.dumps(response, indent = 4, separators = (",",":")))
    #print (response)
   
    if "response" in result:
        config=json.dumps(result["response"], indent = 4, separators = (",",":"))
        return config
        
    else:
        return "Device Details Not Available"
    #config=repr(response["response"]) --> this will print \n in a given string
    
    #print (config)