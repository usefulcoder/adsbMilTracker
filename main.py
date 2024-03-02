import json
import requests
import time
import datetime
import subprocess
import os
from configuration import meshtastic_channel_index, discord_webhook, discord_error_webhook
import meshtastic
import meshtastic.serial_interface

try:    
    interface = meshtastic.serial_interface.SerialInterface()
except:
    interface = False

aircraft_db = {}

with open(f"{os.getenv('HOME')}/adsbMilTracker/aircraft.json") as aircraft_file:
    aircraft_db = json.load(aircraft_file)

flag_dict = {
    "1": "Military Aircraft Received!",
    "2": "Aircraft Marked 'Interesting' Received!",
    "4": "PIA Aircraft Received!",
    "8": "LADD Aircraft Received!"
}
already_seen = ["AE0406"]
daily_hex = []
sent_daily = False

def send_discord_message(title, description, color):
    try:
        send_message = requests.post(discord_webhook, json={"embeds": [
            {
                "title": title,
                "description": description,
                "color": color
            }
        ]})
        return True
    except Exception as e:
        print(e)
        return False

def send_interface_message(message):
    try:
        if interface:
            interface.sendText(message, channelIndex=meshtastic_channel_index)
            time.sleep(1)
    except Exception as e:
        print(e)

def mil_plane_found(plane, hex_code):
    try:
        send_discord_message("MILITARY PLANE RECEPTION CONFIRMED",
                             f'''HEX -> {hex_code}\nREG -> {plane["registration"]}\nSHORTNAME -> {plane["shortName"]}\nMODEL -> {plane["name"]}''',
                             "6750003")
        message = f'''AIRCRAFT RECEIVED\nMODEL: {plane["name"].replace(" ", "")}\nHEX: {hex_code}\nREG: {plane["registration"]}'''
        send_interface_message(message)
    except Exception as e:
        print(e)
        send_interface_message(f'''AIRCRAFT RECEIVED\nMODEL: {plane["name"]}\nHEX: {hex_code}\nREG: {plane["registration"]}''')

errors_since_last_success = 0

while True:
    try:
        try:
            json_data = requests.get("http://localhost/tar1090/data/aircraft.json").json()
        except Exception:
            continue

        hex_list = [item["hex"].upper() for item in json_data["aircraft"]]

        for airframe in json_data["aircraft"]:
            hasLat = False
            try:
                if airframe["lat"]:
                    hasLat = True
            except:
                pass

            if hasLat:
                if type(float(airframe["lat"])) != float:
                    try:
                        plane = aircraft_db[airframe["hex"].upper()]
                        if plane["code"] == "10" and airframe["hex"].upper() not in already_seen:
                            mil_plane_found(plane, airframe["hex"].upper())
                            already_seen.append(airframe["hex"].upper())
                            if airframe["hex"].upper() not in daily_hex:
                                daily_hex.append(airframe["hex"].upper())
                    except:
                        pass
            else:
                try:
                    plane = aircraft_db[airframe["hex"].upper()]
                    if plane["code"] == "10" and airframe["hex"].upper() not in already_seen:
                        mil_plane_found(plane, airframe["hex"].upper())
                        already_seen.append(airframe["hex"].upper())
                        if airframe["hex"].upper() not in daily_hex:
                            daily_hex.append(airframe["hex"].upper())
                except:
                    pass

        for seen in already_seen[:]:
            if seen not in hex_list:
                plane = aircraft_db[seen]
                already_seen.remove(seen)
                send_discord_message("MILITARY PLANE RECEPTION LOST",
                                     f'''HEX -> {seen}\nREG -> {plane["registration"]}\nSHORTNAME -> {plane["shortName"]}\nMODEL -> {plane["name"]}''',
                                     "16711680")
                if interface:
                    message = f'AIRCRAFT LOST\nMODEL: {plane["name"]}\nHEX: {seen}\nREG: {plane["registration"]}'
                    send_interface_message(message)

        time.sleep(5)

        start_time = datetime.time(22, 0, 0)
        end_time = datetime.time(22, 15, 0)
        if start_time <= datetime.datetime.now().time() <= end_time and not sent_daily:
            try:
                send_discord_message("DAILY MILITARY PLANE COUNT",
                                     f'''There were {len(daily_hex)} unique military aircraft seen today.''',
                                     "6750003")
            except:
                pass

            if interface:
                message = f"DAILY MILITARY PLANE COUNT: {len(daily_hex)}"
                send_interface_message(message)
                
            daily_hex = []
            sent_daily = True

        errors_since_last_success = 0

        if datetime.datetime.now().time() > end_time and sent_daily:
            sent_daily = False
    except Exception as e:
        error_msg = f'''AN ERROR OCCURRED WITHIN THE ADSBTRACKER ON UBUNTUSERVER\nERROR: {e}'''
        requests.post(discord_error_webhook, json={"content": error_msg})
        errors_since_last_success += 1
        if errors_since_last_success >= 11:
            subprocess.run(["systemctl", "stop", "adsbtracker"])
            requests.post(discord_error_webhook, json={"content": "CRITICAL ERROR HAS OCCURRED. PROGRAM HAS BEEN STOPPED AND WILL NEED TO MANUALLY BE RESTARTED."})
