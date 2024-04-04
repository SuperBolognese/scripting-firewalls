#################################################################################
#
#
#
#Script to create firewall filter rules from imported objects and services
#This creates a file with all Stormshield commands to create thr rules, and must then be entered manually on the SNS
#
#
#
#################################################################################

import json, os, requests

from variables import api_call, sid, CPmgmtIP

def getCheckpointRules():
    ruleNumber = 1
    while True:
        payload = {
            "layer": "network",
            "rule-number": ruleNumber
        }
        parsedResponse = {}
        response = api_call(CPmgmtIP, 443, 'show-access-rule', payload, sid)
        print(json.dumps(response,indent=2))
        if response[1] == 200:
            parsedResponse['objects'] = response[0]["objects"]
            ruleNumber+=1
        else:
            break

    print(json.dumps(parsedResponse, indent=2))
    #return (json.dumps(parsedResponse["objects"]))

getCheckpointRules()