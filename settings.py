#!/usr/bin/env python

import requests
import os
import sys
import json
import base64
'''
#################################################################################################################################################################
ENatics is a beta project about Software Defined Networking, and created by Jon Warner Campo. For any issues or concerns, you may email him at joncampo@cisco.com.
See Terms of Service - https://arcane-spire-45844.herokuapp.com/terms
See Privacy Policy - https://arcane-spire-45844.herokuapp.com/privacy
#################################################################################################################################################################
'''
def get_settings():
    """
    builds the needed HTTP headers for Spark
    In:
        token: Spark Auth Token (str)
    Out:
        HTTP Header (dict)
    """
    ###token of sparkbot ENatics
    #token=os.environ["sparkbot_token"]
    fb_token=""

    APIC_EM_BASE_URL = ''
    APIC_EM_USER = ''
    APIC_EM_PASS = ''

    CMX_BASE_URL = ''
    
    CMX_User = ''
    CMX_Pass = ''

    ####Don't edit#######
    raw_encoded = base64.b64encode(bytes(CMX_User+":"+CMX_Pass,'utf-8'))
    encoded=raw_encoded.decode("utf-8")
    CMX_Auth = 'Basic '+encoded
    ####Don't edit#######

    MERAKI_BASE_URL = 'dashboard.meraki.com'
    #MERAKI_TOKEN = os.environ["meraki_token"]
    MERAKI_TOKEN=""

    fb_verify_pass=""

    CSR1KV=''
    NETCONF_PORT=10000
    # use the user credentials for your CSR1000V device
    NETCONF_USER = ''
    NETCONF_PASS = ''

    google_token=""

    return fb_token, APIC_EM_BASE_URL, APIC_EM_USER, APIC_EM_PASS, CMX_BASE_URL, CMX_Auth, MERAKI_BASE_URL, MERAKI_TOKEN, fb_verify_pass, CSR1KV, NETCONF_PORT, NETCONF_USER, NETCONF_PASS, google_token