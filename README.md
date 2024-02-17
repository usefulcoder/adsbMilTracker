# Currently only works/tested with RTL SDR v3 and AirNav ADS-B Receivers

# Install Instructions

## Raspberry Pi Packages / Install

0. Plug in SDR into the Pi, and connect it to your 1090MHz antenna.

1.  Update and Upgrade Pi.
**This may take some time.**\
```
sudo apt update && sudo apt upgrade
```

2. Add piaware repository\
*Credit to Wiedehopf for this script* \
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