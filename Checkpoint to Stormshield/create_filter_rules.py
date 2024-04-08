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
    parsedResponse = {
        'objects': []
    }
    while ruleNumber < 6:
        payload = {
            "layer": "network",
            "rule-number": ruleNumber
        }
        response = api_call(CPmgmtIP, 443, 'show-access-rule', payload, sid)
        parsedResponse['objects'].extend(response)
        ruleNumber+=1

    return (json.dumps(parsedResponse["objects"]))

def createFWRules(rulesList):
    return