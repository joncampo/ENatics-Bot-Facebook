#!/usr/bin/env python
import requests
import json
import time
import sys
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder

from PIL import Image
from shutil import copyfile

# Disable all warning messages since we're dealing with a
# self-signed certificate on cmx
requests.packages.urllib3.disable_warnings()
'''
#################################################################################################################################################################
ENatics is a beta project about Software Defined Networking, and created by Jon Warner Campo. For any issues or concerns, you may email him at joncampo@cisco.com.
See Terms of Service - https://arcane-spire-45844.herokuapp.com/terms
See Privacy Policy - https://arcane-spire-45844.herokuapp.com/privacy
#################################################################################################################################################################
'''


###########################################################################
def cmx_map_download(CMX_BASE_URL,CMX_Auth,cmx_map_download):
    #api = "/network-device"
    image_exists=os.path.isfile('temp/'+cmx_map_download)

    if image_exists is True:
        #copy to map.png
        print ("Image exists!")
        copyfile('temp/'+cmx_map_download,'temp/map.png')
        return True

    else:
        print ("Image does not exist!")
        FULL_URL = "https://"+CMX_BASE_URL+"/api/config/v1/maps/imagesource/"+cmx_map_download
        headers = {"Authorization": CMX_Auth}     
        result = requests.get(FULL_URL, headers=headers, verify=False).content
        with open('temp/map.png', 'wb') as handler:
            handler.write(result)

        if result:
            copyfile('temp/map.png', 'temp/'+cmx_map_download)
            return True
            
        else:
            return False


def cmx_edit_map(calc_x,calc_y,bundle):
 
    if bundle == 0:

        img1 = Image.open('temp/map.png')
        if img1.mode != "RGB":
            img1=img1.convert('RGB')
            
        pixel_img1 = img1.load()

        pin = Image.open('temp/pin.png')

        img2 = img1.copy()

        position = (int(calc_x), int(calc_y))
        img2.paste(pin, position, pin)

        img2.save('temp/map2.png')
        img1.close()
        pin.close()
        img2.close()
        return True

    elif bundle == 1:

        img1 = Image.open('temp/map.png')
        if img1.mode != "RGB":
            img1=img1.convert('RGB')

        pixel_img1 = img1.load()

        pin = Image.open('temp/pin.png')

        img2 = img1.copy()

        num=0
        while num < len(calc_x):
            position = (int(calc_x[num]), int(calc_y[num]))
            img2.paste(pin, position, pin)
            num=num+1
        img2.save('temp/map2.png')
        img1.close()
        pin.close()
        img2.close()
        return True

    elif bundle == 2:

        img1 = Image.open('temp/map.png')
        if img1.mode != "RGB":
            img1=img1.convert('RGB')
            
        pixel_img1 = img1.load()

        pin = Image.open('temp/pin-green.png')

        img2 = img1.copy()

        position = (int(calc_x), int(calc_y))
        img2.paste(pin, position, pin)

        img2.save('temp/map2.png')
        img1.close()
        pin.close()
        img2.close()

        return True
        
    else:
        return False


def cmx_list_client(cmx_url,cmx_auth):

    FULL_URL =  "https://"+cmx_url+"/api/location/v2/clients/active"
    headers = {"Authorization": cmx_auth}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()


    num=1
    line_item=[]
    dictionary_item={}
    for i in result:
     item= (str(num)+". "+str(i))

     dictionary_item.update({str(num):str(i)})
     #line_item.update(dictionary_item)
     #line_item.append(inside_item)
     line_item.append(item)

     num = num + 1

    if result:
        return line_item, dictionary_item

        
    else:
        return "Map Not Available"

def cmx_list_floors(cmx_url,cmx_auth):
    #api = "/network-device"

    #FULL_URL = "https://"+BASE_URL+"/api/config/v1/maps"
    FULL_URL =  "https://"+cmx_url+"/api/config/v1/maps/floor/list"
    headers = {"Authorization": cmx_auth}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()
    #print (json.dumps(response, indent = 4, separators = (",",":")))
    #print (response)

    num=1
    line_item=[]
    dictionary_item={}
    for i in result:
     item= (str(num)+". "+str(i))

     dictionary_item.update({str(num):str(i)})
     #line_item.update(dictionary_item)
     #line_item.append(inside_item)
     line_item.append(item)
     num = num + 1

    if result:
        return line_item, dictionary_item

        
    else:
        return "Floor Not Available"

def get_floor_id(cmx_url,cmx_auth,floor):
    #api = "/network-device"

    #FULL_URL = "https://"+BASE_URL+"/api/config/v1/maps"
    FULL_URL =  "https://"+cmx_url+"/api/config/v1/maps/info/"+floor
    headers = {"Authorization": cmx_auth}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()

    #print (json.dumps(response, indent = 4, separators = (",",":")))
    #print (response)

    floor_id=result["aesUid"]

    if result:
        return True, floor_id

        
    else:
        return False, False

def cmx_collect_client(cmx_url,cmx_auth, floor_id):
    #api = "/network-device"

    #FULL_URL = "https://"+BASE_URL+"/api/config/v1/maps"
    FULL_URL =  "https://"+cmx_url+"/api/location/v2/clients"
    headers = {"Authorization": cmx_auth}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()
    #print (json.dumps(response, indent = 4, separators = (",",":")))
    #print (response)

    line_item=[]
    calc=0
    bundle=1
    #print(result)

    calc_x=[]
    calc_y=[]
    num=1
    for i in result:
        print (num)
        num=num+1
        #print (i["mapInfo"]["mapHierarchyString"])
        #print (floor)
        cmx_user_location_id=i["mapInfo"]["floorRefId"]
        print ("cmx user id:",cmx_user_location_id)
        print ("floor_id:",floor_id)
        if int(cmx_user_location_id) == int(floor_id):
            print("match")
            if calc == 0:
                map_name=i["mapInfo"]["image"]["imageName"]
                print ("Map Name: "+map_name)
                map_dimension_x=i["mapInfo"]["floorDimension"]["width"]
                print("Map Dimension(width/x): ",map_dimension_x)
                map_dimension_y=i["mapInfo"]["floorDimension"]["length"]    
                print("Map Dimension(length/height/y): ",map_dimension_y)

                map_image_x=i["mapInfo"]["image"]["width"]
                print("Map Image Pixel (width/x): ",map_image_x)
                map_image_y=i["mapInfo"]["image"]["height"]
                print("Map Image Pixel (length/height/y): ",map_image_y)
                print ("Downloading Map...")
                cmx_map=cmx_map_download(cmx_url,cmx_auth,map_name)
                calc=1


            #print (i["macAddress"])
            #line_item.append(i["macAddress"])
            #print ("\n")
            user_coordinate_x=i["mapCoordinate"]["x"]
            #print ("User Coordinate(width/x): ",user_coordinate_x)
            user_coordinate_y=i["mapCoordinate"]["y"]
            #print ("User Coordinate(length/height/y): ",user_coordinate_y)
            calculated_x= (int(map_image_x)/int(map_dimension_x))*int(user_coordinate_x)
            calculated_y= (int(map_image_y)/int(map_dimension_y))*int(user_coordinate_y)
            #print ("Calculated x:",calculated_x)
            #print("Calculated y:",calculated_y)
            calc_x.append(int(calculated_x))
            calc_y.append(int(calculated_y))

    if calc == 1:
        #cmx_edit=cmx_edit_map(calc_x,calc_y,bundle)
        return True, calc_x,calc_y
   
    else:
        return False, False


def cmx_client_info(CMX_BASE_URL,CMX_Auth,cmx_client):
    #api = "/network-device"

    #FULL_URL = "https://"+BASE_URL+"/api/config/v1/maps"
    FULL_URL = "https://"+CMX_BASE_URL+"/api/location/v1/clients/"+cmx_client
    headers = {"Authorization": CMX_Auth}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()
    #print (json.dumps(response, indent = 4, separators = (",",":")))
    #print (response)
    cmx_user_location=result["mapInfo"]["floorRefId"]
    print ("Location: "+cmx_user_location)

    map_name=result["mapInfo"]["image"]["imageName"]
    print ("Map Name: "+map_name)
    
    map_dimension_x=result["mapInfo"]["floorDimension"]["width"]
    print("Map Dimension(width/x): ",map_dimension_x)
    map_dimension_y=result["mapInfo"]["floorDimension"]["length"]    
    print("Map Dimension(length/height/y): ",map_dimension_y)

    map_image_x=result["mapInfo"]["image"]["width"]
    print("Map Image Pixel (width/x): ",map_image_x)
    map_image_y=result["mapInfo"]["image"]["height"]
    print("Map Image Pixel (length/height/y): ",map_image_y)

    user_coordinate_x=result["mapCoordinate"]["x"]
    print ("User Coordinate(width/x): ",user_coordinate_x)
    user_coordinate_y=result["mapCoordinate"]["y"]
    print ("User Coordinate(length/height/y): ",user_coordinate_y)


    calculated_x= (int(map_image_x)/int(map_dimension_x))*int(user_coordinate_x)
    calculated_y= (int(map_image_y)/int(map_dimension_y))*int(user_coordinate_y)
    print (calculated_x)
    print(calculated_y)

    if result:
        cmx_map=cmx_map_download(CMX_BASE_URL,CMX_Auth,map_name)
    
    else:
        return False

    if cmx_map is True:
        bundle=0
        cmx_edit=cmx_edit_map(calculated_x,calculated_y,bundle)
       
    else:
        return False

    if cmx_edit is True:
        return True, cmx_user_location
    else:
        return False, False


def cmx_collect_zones(cmx_url,cmx_auth, floor):
    #api = "/network-device"

    #FULL_URL = "https://"+BASE_URL+"/api/config/v1/maps"
    FULL_URL =  "https://"+cmx_url+"/api/config/v1/maps/info/"+floor
    headers = {"Authorization": cmx_auth}
    result = requests.get(FULL_URL, headers=headers, verify=False).json()

    #print(result["zones"][1]["name"])
    #print(result["zones"][1]["zoneCoordinate"])
    bundle=2
    #if "RESTROOM" in result["zones"][1]["name"]:
    calc=0

    try: 
        a=len(result["zones"])
    except NameError:
        return False

    for i in result["zones"]:   

        if "RESTROOM" in i["name"]:
            calc=1
            map_name=result["image"]["imageName"]
            print ("Map Name: "+map_name)

            map_dimension_x=result["dimension"]["width"]
            print("Map Dimension(width/x): ",map_dimension_x)
            map_dimension_y=result["dimension"]["length"]    
            print("Map Dimension(length/height/y): ",map_dimension_y)

            map_image_x=result["image"]["width"]
            print("Map Image Pixel (width/x): ",map_image_x)
            map_image_y=result["image"]["height"]
            print("Map Image Pixel (length/height/y): ",map_image_y)
                    
            cmx_map=cmx_map_download(cmx_url,cmx_auth,map_name)
            


            for z in i["zoneCoordinate"]:
                user_coordinate_x=z["x"]
                print ("Zone Coordinate(width/x): ",user_coordinate_x)
                user_coordinate_y=z["y"]
                print ("Zone Coordinate(length/height/y): ",user_coordinate_y)
                new_calculated_x= (int(map_image_x)/int(map_dimension_x))*int(user_coordinate_x)
                new_calculated_y= (int(map_image_y)/int(map_dimension_y))*int(user_coordinate_y)

                if new_calculated_x > high_calculated_x:
                    high_calculated_x = new_calculated_x

                elif new_calculated_x < low_calculated_x:
                    low_calculated_x = new_calculated_x

                if new_calculated_y > high_calculated_y:
                    high_calculated_y = new_calculated_y

                elif new_calculated_y < low_calculated_y:
                    low_calculated_y = new_calculated_y

            ave_calculated_x=(high_calculated_x+low_calculated_x)/2
            ave_calculated_y=(high_calculated_y+low_calculated_y)/2

            if cmx_map is True:
                bundle=2
                cmx_edit=cmx_edit_map(ave_calculated_x,ave_calculated_y,bundle)
                print ("success")
                return True
           
            else:
                return False

    if calc == 0:
        return False


