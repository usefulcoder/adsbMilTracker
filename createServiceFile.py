import os

home_folder = os.getenv("HOME")
with open(f"./adsbMilTracker.service", "a") as service_file:
    service_file.write("[Unit]")
    service_file.write("\nDescription=adsb Military Plane Tracker and Notifier")
    service_file.write("\nAfter=network.target")
    service_file.write("\n")
    service_file.write("\n[Service]")
    service_file.write("\nType=simple")
    service_file.write(f"\nExecStart=python {home_folder}/adsbMilTracker/main.py")
    service_file.write(f"\nUser={home_folder.split("/")[2]}")
    service_file.write("\nTimeoutStartSec=infinity")
    service_file.write("\n")
    service_file.write("\n[Install]")
    service_file.write("\nWantedBy=multi-user.target")