#!/usr/bin/python

#  __      _   _   _                 
# / _\ ___| |_| |_(_)_ __   __ _ ___ 
# \ \ / _ \ __| __| | '_ \ / _` / __|
# _\ \  __/ |_| |_| | | | | (_| \__ \
# \__/\___|\__|\__|_|_| |_|\__, |___/
#                          |___/     

# See https://api.cloudflare.com/#getting-started-requests for info about theese settings.

# Zone ID
zoneid = ""

# Email
cfEmail = ""

# Cloudflare API-key
cfAPIKey = ""

# htaccess-file
htaccessFile = "/home/username/public_html/.htaccess"

# Note
# Don't change after initial setup, this is used to only add/delete entries
# added by this script.

cfNote = "cf-auto-ipsettings"

#    ___          _      
#   / __\___   __| | ___ 
#  / /  / _ \ / _` |/ _ \
# / /__| (_) | (_| |  __/
# \____/\___/ \__,_|\___|
                       
import re
import requests
import json

newVar = {}
ips = []

headers = {
        "X-Auth-Email": cfEmail,
        "X-Auth-Key": cfAPIKey,
        "Content-Type": "application/json",
    }

url = "https://api.cloudflare.com/client/v4/zones/" + zoneid + "/firewall/access_rules/rules?scope_type=zone&notes=" + cfNote + "&match=any"

response = requests.get(url, headers=headers)

data = response.json()

for output in data["result"]:
    newVar[output["configuration"]["value"]] = output["id"]

with open(htaccessFile, 'r') as f:
    filecont = f.readlines()
    for line in filecont:
        if re.match("deny from [0-9]+", line, re.IGNORECASE):
            tempVar = line.split('\n')[0]
            denyReg = re.compile('deny from ', re.IGNORECASE).split(tempVar)[1]
            ips.append(denyReg)

toBeDeleted = [item for item in newVar if item not in ips]

toBeCreated = [item for item in ips if item not in newVar]

def deleteEntry ( id ):
    url2 = "https://api.cloudflare.com/client/v4/zones/" + zoneid + "/firewall/access_rules/rules/" + id
    res = requests.delete(url2, headers=headers)

def addEntry ( ip ):
    url3 = "https://api.cloudflare.com/client/v4/zones/" + zoneid + "/firewall/access_rules/rules/"
    if re.match(".+\/[0-9]{1,2}$", ip):
        type = "ip_range"
    else:
        type = "ip"
    postdata = '{"mode":"block","configuration":{"target":"'+ type +'","value":"'+ ip +'"},"notes":"'+cfNote+'"}'
    res = requests.post(url3, headers=headers, data=postdata)

for id, ip in enumerate(toBeDeleted):
    deleteEntry (newVar[ip])

for id, ip in enumerate(toBeCreated):
    addEntry(ip)
