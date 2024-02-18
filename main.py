import json
import requests
import time
from datetime import datetime
import subprocess
import os
from configuration import meshtastic_channel_index, discord_webhook, discord_error_webhook
import meshtastic
import meshtastic.serial_interface


try:    
    interface = meshtastic.serial_interface.SerialInterface()
except:
    interface = False
aircraft_db = ""
with open(f"{os.getenv('HOME')}/adsbMilTracker/aircraft.json") as aircraft:
    aircraft_db = json.loads(aircraft.read())
flag_dict = {
            "1" : "Military Aircraft Received!",
            "2" : "Aircraft Marked 'Interesting' Received!",
            "4" : "PIA Aircraft Received!",
            "8" : "LADD Aircraft Received!"
        }
already_seen = ["AE0406"]
daily_hex = []
sent_daily = False
def mil_plane_found(plane,hex):
    
    try:
        send_message = requests.post(discord_webhook, json={"embeds" : [
        {
            "title" : "MILITARY PLANE RECEPTION CONFIRMED",
            "description" : f'''
            ... HEX -> {hex}...
            ...REG -> {plane["registration"]}...
            ...SHORTNAME -> {plane["shortName"]}...
            ...MODEL -> {plane["name"]}...
            ...END RECEPTION MESSAGE...
        ''',
            "color" : "6750003"
        }
    ]})

        
        reg = plane["registration"]
        short = plane["shortName"]
        name = plane["name"].replace(" ", "")
                    
        message = f"MIL..AIRCRAFT..RECEIVED..->..HEX:..{seen},..MODEL..->..{name}...END..MESSAGE..."
        if interface:
            interface.sendText(message, channelIndex=meshtastic_channel_index)
            time.sleep(1)
    except:
        if interface:
            reg = plane["registration"]
            short = plane["shortName"]
            name = plane["name"]

            message = f"MIL..AIRCRAFT..LOST..->..HEX:..{seen},..MODEL..->..{name}...END..MESSAGE..."
            interface.sendText(message, channelIndex=meshtastic_channel_index)
            time.sleep(1)
errors_since_last_success = 0
while True:
    
    try:
        
        try:
            json_data = requests.get("http://localhost/tar1090/data/aircraft.json").json()
            print(json_data)
        except:
            continue
        
        hex_list = [item["hex"].upper() for item in json_data["aircraft"] ]

        for airframe in json_data["aircraft"]:
            hasFlags = False
            hasEmergency = False
            hasLat = False
            try:
                if airframe['dbFlags']:
                    hasFlags = True
            except:
                None 
            try:
                if airframe["emergency"]:
                    hasEmergency = True
            except:
                None
            try:
                if airframe["lat"]:
                    hasLat = True
            except:
                None
            
            # if hasFlags:
            #     print(flag_dict[str(airframe['dbFlags'])])
            
            # if hasEmergency:
            #     if airframe['emergency'] != "none":
            #         print("airframe emergency")
            
            # if not hasFlags and not hasEmergency:
            #     print("no weird aircraft")
            if hasLat:
                
                if type(float(airframe["lat"])) != float:
                    
                    try:
                        plane = aircraft_db[airframe["hex"].upper()]
                        if plane["code"] == "10":
                        
                            if not airframe["hex"].upper() in already_seen:
                                mil_plane_found(plane, airframe["hex"].upper())
                                already_seen.append(airframe["hex"].upper())
                                if airframe["hex"].upper() not in daily_hex:
                                    daily_hex.append(airframe["hex"].upper())

                            
                        
                    except Exception as e:
                        None
            else:
                try:
                        
                        plane = aircraft_db[airframe["hex"].upper()]
                        if plane["code"] == "10":
                            if not airframe["hex"].upper() in already_seen:
                                mil_plane_found(plane, airframe["hex"].upper())
                                already_seen.append(airframe["hex"].upper())
                                if airframe["hex"].upper() not in daily_hex:
                                    daily_hex.append(airframe["hex"].upper())

                            
                        
                except Exception as e:
                    None
        
        for seen in already_seen:
            if seen not in hex_list:
                plane = aircraft_db[seen]
                already_seen.remove(seen)
                message =""
                try:
                    send_message = requests.post(discord_webhook, json={'content' : message,"embeds" : [
        {
            "title" : "MILITARY PLANE RECEPTION LOST",
            "description" : f'''
            ... HEX -> {seen}...
            ...REG -> {plane["registration"]}...
            ...SHORTNAME -> {plane["shortName"]}...
            ...MODEL -> {plane["name"]}...
            ...END RECEPTION MESSAGE...
        ''',
            "color" : "16711680"
        }
    ]})
                    reg = plane["registration"]
                    short = plane["shortName"]
                    name = plane["name"].replace(" ", "")
                    
                    message = f"MIL..AIRCRAFT..LOST..->..HEX:..{seen},..MODEL..->..{name}...END..MESSAGE..."
                    if interface:
                        interface.sendText(message, channelIndex=2)
                        time.sleep(1)
                    # 
                    # interface.sendText(f'HEX -> {seen}', channelIndex=2)
                    # time.sleep(0.5)
                    # interface.sendText(f'REG -> {reg}', channelIndex=2)
                    # time.sleep(0.5)
                    # interface.sendText(f'SHORTNAME -> {short}', channelIndex=2)
                    # time.sleep(0.5)
                    # interface.sendText(f'.MODEL -> {name}', channelIndex=2)
                    # time.sleep(0.5)
                    
                    
                except:
                    reg = plane["registration"]
                    short = plane["shortName"]
                    name = plane["name"]
                    
                    message = f"MIL..AIRCRAFT..LOST..->..HEX:..{seen},..MODEL..->..{name}...END..MESSAGE..."
                    if interface:
                        interface.sendText(message, channelIndex=2)
                        time.sleep(1)

        time.sleep(5)
        if datetime.now().strftime("%H:%M") == "22:00" and not sent_daily:
            send_message = requests.post(discord_webhook, json={"embeds" : [
                {
                    "title" : "DAILY MILITARY PLANE COUNT",
                    "description" : f'''
                    There were {len(daily_hex)} unique military aircraft seen today.
                ''',
                    "color" : "6750003"
                }
                   ]})
            daily_hex = []
            sent_daily = True
        errors_since_last_success = 0
        
        if datetime.now().strftime("%H:%M") != "22:00" and sent_daily:
            sent_daily == False
    except Exception as e:
        error_msg = f"""
        ...AN ERROR OCCURRED WITHIN THE ADSBTRACKER ON UBUNTUSERVER...
        ERROR: {e}
        """
        requests.post(discord_error_webhook, json={"content" : error_msg})
        errors_since_last_success += 1
        if errors_since_last_success >= 11:
            subprocess.run(["systemctl", "stop", "adsbtracker"])
            requests.post(discord_error_webhook, json={"content" : """
            
            CRITICAL ERROR HAS OCCURRED. PROGRAM HAS BEEN STOPPED AND WILL NEED TO MANUALLY BE RESTARTED.
            
            """})
            
    
