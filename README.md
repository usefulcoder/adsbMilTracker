# Currently only works/tested with RTL SDR v3 and AirNav ADS-B Receivers

# Install Instructions

## Raspberry Pi Packages / Install

0. Plug in SDR into the Pi, and connect it to your 1090MHz antenna.

1.  Update and Upgrade Pi.
**This may take some time.**
```
sudo apt update && sudo apt upgrade
```

2. Add piaware repository\
*Credit to Wiedehopf for this script* 
```
    wget -O piaware.deb http://flightaware.com/adsb/piaware/files/packages/pool/piaware/p/piaware-support/piaware-repository_3.8.0_all.deb
```

3. DPKG piaware repo
```
    sudo dpkg -i piaware.deb
```

4. add Buster to your repo sources list
    ```
        sudo nano /etc/apt/sources.list
    ```
    - paste this on a new line in the sources.list file
    ```
    deb http://deb.debian.org/debian buster main contrib non-free
    ```

5. update your repos
```
    sudo apt update
```

6. Install dump1090-fa
    ```
    sudo apt install dump1090-fa
    ```

7. **IMPORTANT: REBOOT THE PI** 
```
    sudo reboot
```

8. After reboot, install tar1090
```
    sudo bash -c "$(wget -nv -O - https://github.com/wiedehopf/tar1090/raw/master/install.sh)"
```

9. it should now be installed. Test by going to http://YOUR_PI's_LOCAL_IP_ADDR/tar1090.
   You should see the aircraft map.


## milTracker install and setup

1. ensure that dependencies are installed on your raspberry pi:
    - This may appear to freeze or stop at times. More than likely it is working, it just takes a while to install.
    ```
    sudo apt install git python3-pip python3-full python-is-python3 && pip install meshtastic --break-system-packages
    ```

2. install the base repository that includes the program, the aircraft database, and configuration.
    ```
    cd ~
    git clone https://github.com/usefulcoder/adsbMilTracker.git
    ```

3. setup the configuration file:
    1. navigate to the new adsbMilTracker directory
        ```
        cd adsbMilTracker
        ```
    2. Edit the configuration.py
         ```
        sudo nano configuration.py
        ```
    - IF you are planning on using discord webhooks and your pi will remain connected to the internet, follow the below:
        1. Set the Discord Variables
           ```
           discord_webhook = "ENTER_YOUR_FULL_WEBHOOK_URL_HERE"
           discord_error_webhook = "ENTER_YOUR_FULL_ERROR_WEBHOOK_HERE"
           ```
        
    - Set meshtastic channel 
        ```
        meshtastic_channel_index = ENTER_CHANNEL_INDEX_NUMBER_HERE #ex -> meshastic_channel_index = 2
        ```

### **IF YOU ARE NOT USING DISCORD, YOU CAN JUST LEAVE THEM AS THEY ARE**

## Setup adsbMilTracker as a service

1. navigate to install base directory
    ```
    cd ~/adsbMilTracker
    ```
2. Give folder edit permissions and Create service file
    ```
    sudo chmod -R 777 ../adsbMilTracker && python createServiceFile.py 
    ```
3. Move service file into systemd
    ```
    sudo mv ./adsbMilTracker.service /etc/systemd/system/adsbMilTracker.service
    ```

4. Reload the service daemon
    ```
    sudo systemctl daemon-reload
    ```

5. Enable the service
    ```
    sudo systemctl enable adsbMilTracker.service && sudo systemctl start adsbMilTracker && sudo systemctl status adsbMilTracker
    ```

6. The output of the above command should show the status of the service and it should say **active(running)**

# ALL SET! If you followed the above, you should be good to go and should be actively listening for mil aircraft. The below is only for convenience on any future installs.
## EASY TO COPY CODE BLOCKS

```
sudo apt update && sudo apt upgrade && wget -O piaware.deb http://flightaware.com/adsb/piaware/files/packages/pool/piaware/p/piaware-support/piaware-repository_3.8.0_all.deb && sudo dpkg -i piaware.deb && sudo nano /etc/apt/sources.list
```

Paste this into the file that pulls up on a new line: `deb http://deb.debian.org/debian buster main contrib non-free`

```
sudo apt update && sudo apt install dump1090-fa && sudo reboot
```

```
sudo bash -c "$(wget -nv -O - https://github.com/wiedehopf/tar1090/raw/master/install.sh)" && sudo apt install git python3-pip python3-full python-is-python3 && pip install meshtastic --break-system-packages && cd ~ && git clone https://github.com/usefulcoder/adsbMilTracker.git && cd adsbMilTracker
```
Add your configs as stated inthe format in the explanations above
```
sudo nano configuration.py
```

```
cd ~/adsbMilTracker && sudo chmod -R 777 ../adsbMilTracker && python createServiceFile.py && sudo mv ./adsbMilTracker.service /etc/systemd/system/adsbMilTracker.service && sudo systemctl daemon-reload && sudo systemctl enable adsbMilTracker.service && sudo systemctl start adsbMilTracker && sudo systemctl status adsbMilTracker
```
