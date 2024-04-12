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

import json

from variables import api_call, sid, CPmgmtIP

def getCheckpointRules():

    ruleNumber = 1
    ruleloop = True

    parsedResponse = {
        'objects':[]
    }

    while ruleloop:
        payload = {
            "layer": "oui network",   # Change layer name with layer. If no layer specifically stated, put "{package_name} network"
            "rule-number": ruleNumber,
            "details-level": "full"
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-access-rule', payload, sid)
            content = response[0]
            code = response[1]
            match code:
                case 200:
                    parsedResponse['objects'].append(content)
                    ruleNumber += 1
                case 400:
                    ruleNumber += 1
                    print(json.dumps(content, indent=2))
                    ruleloop = False
                case 404:
                    ruleNumber += 1
                    print(json.dumps(content, indent=2))
                case _ :
                    ruleNumber += 1
        except:
            print("API call for filter rule #"+str(ruleNumber)+" failed, skipping")
    return json.dumps(parsedResponse)

def createFWRules(rulesList):

    rulesList = json.loads(rulesList)

    for rule in rulesList['objects']:
        strSource = ""
        strDst = ""
        strService = ""
        strLogLevel =rule['track']['type']['name']
        if 'name' in rule:
            strName = str.replace(rule['name']," ", "_")
            query = "config filter rule insert index=10 type=filter state=on rulename="+strName
        else:
            query = "config filter rule insert index=10 type=filter state=on"
        for source in rule['source']:
            strSource += source['name']+","
        for dest in rule['destination']:
            strDst += dest['name']+","
        for serv in rule['service']:
            strService += serv['name']+","
        action = rule['action']['name']
        match action:
            case 'Drop':
                strAction = "reset"
            case 'Accept':
                strAction = "pass"
            case 'Reject':
                strAction = "block"
        strSource = strSource[:-1]
        strService = strService[:-1]
        strDst = strDst[:-1]
        query += " action="+strAction +" srctarget="+strSource+" dsttarget="+strDst+" dstport="+strService+" loglevel="+strLogLevel +"inspection=ids"
        print(query)


def main():
    rulelist = getCheckpointRules()
    createFWRules(rulelist)

if __name__ == '__main__':
    main()