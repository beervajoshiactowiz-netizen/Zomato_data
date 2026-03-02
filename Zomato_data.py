import json,re
from datetime import datetime
import mysql.connector
from Zomato_database import send_to_db
from Zomato_model import ZomatoRestaurant
#empty dictonary to store the data
new={}

#load json file
def input_file(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        return data

#process the json data
def parser(d):
    section_info=d["page_data"]["sections"]["SECTION_BASIC_INFO"]
    section_contact=d["page_data"]["sections"]["SECTION_RES_CONTACT"]
    section_header=d["page_data"]["sections"]["SECTION_RES_HEADER_DETAILS"]["LOCALITY"]
    new["restaurant_id"]=section_info["res_id"]     #get restaurant id

    new["restaurant_name"] = section_info["name"]     #get restaurant name

    new["restaurant_url"] = section_header["url"]     #get restaurant url

    new["restaurant_contact"]=[section_contact["phoneDetails"]["phoneStr"]]     #get contact no.

    #get license no.
    lic=d["page_data"]["order"]["menuList"]["fssaiInfo"]["text"]
    match=re.search(r"\d+",lic)
    new["fssai_licence_number"]=[match.group()]

    #get address
    new["address_info"]={}
    new["address_info"]["full_address"]=section_contact["address"]
    new["address_info"]["city"]=section_contact["city_name"]
    new["address_info"]["pincode"] = section_contact["zipcode"]
    region = section_header["text"].split(",")[0]
    new["address_info"]["region"] = region

    try:
        new["address_info"]["state"] = section_contact["state"]
    except KeyError:
        new["address_info"]["state"] = None

    #get cuisines
    #initialise empty list
    new["cuisines"]=[]

    cuisine=d["page_data"]["sections"]["SECTION_RES_HEADER_DETAILS"]["CUISINES"]
    for i in range(len(cuisine)):
        new["cuisines"].append({"name":cuisine[i]["name"],"url":cuisine[i]["url"]})


    #get timings
    new["timings"]={}
    timing=d["page_data"]["sections"]["SECTION_BASIC_INFO"]["timing"]["customised_timings"]["opening_hours"][0]["timing"]
    days=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

    parts=[t.strip() for t in timing.split()]
    open_time=parts[0]
    close_time=parts[2]

    if open_time in ["12Noon","12noon","Noon"]:
        open_time="12pm"

    for day in days:
        new["timings"][day]={
            "open":open_time,
            "close":close_time
        }


    #empty list for menus
    new["menu_categories"]=[]
    #menus path
    menus=d["page_data"]["order"]["menuList"]["menus"]
    for i in range(len(menus)):
        #categories path
        categories=menus[i]["menu"]["categories"]
        for j in range(len(categories)):
            categories_name=categories[j]["category"]["name"]

            #filling blank values by its menu name
            if not categories_name:
                categories_name=menus[i]["menu"]["name"]
            else:
                categories_name=categories_name
            category_entry = {
                "category_name": categories_name,
                "items": []
            }

            #items path
            items_d=categories[j]["category"]["items"]
            for k in range(len(items_d)):
                item = items_d[k]["item"]
                if item["dietary_slugs"][0]=="veg":
                    is_veg=True
                else:
                    is_veg=False
                item_entry={
                    "item_id": item.get("id"),
                    "item_name": item.get("name"),
                    "item_slug":item.get("tag_slugs"),
                    "item_description": item.get("desc"),
                    "is_veg": is_veg
                }

                category_entry["items"].append(item_entry)
            #append the data in empty list
            new["menu_categories"].append(category_entry)
    return new


file=input("enter file name: ")
d=input_file(file)
extracted=parser(d)
validated_data=ZomatoRestaurant(**extracted)
validated_dict=validated_data.model_dump()
send_to_db(validated_dict)