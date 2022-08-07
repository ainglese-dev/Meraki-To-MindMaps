# Meraki-To-MindMaps

![Script Result](images/table.svg)

# Installation for debian-based OS
Virtual Environment

We recommend running Mind nMap in a Python virtual environment while testing or developing. This will help keep your host system clean and allow you to have multiple environments to try new things. If you are not using a virtual environment, start at the download/clone step below.

You will also need Python 3, pip, and venv installed on your host system.

In your project directory, create your virtual environment
``` console
python3 -m venv myvenv
```
Activate (use) your new virtual environment (Linux):
``` console
source myvenv/bin/activate
```
Download or clone the mind_nmap repository:

``` console
git clone https://github.com/AngelIV23/Meraki-To-MindMaps.git
```

Install markmap into your environment:
``` console
sudo apt update
sudo apt install npm
sudo npm install markmap-cli -g
```

