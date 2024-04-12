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

def getCheckpointNatRules():

    ruleNumber = 1
    ruleloop = True

    parsedResponse = {
        'objects':[]
    }

    while ruleloop:
        payload = {
            "package":"oui",
            "rule-number": ruleNumber,
            "details-level": "full"
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-nat-rule', payload, sid)
            content = response[0]
            code = response[1]
            match code:
                case 200:
                    parsedResponse['objects'].append(content)
                    ruleNumber += 1
                case 400:
                    print(json.dumps(content, indent=2))
                    ruleloop = False
                case 404:
                    ruleNumber += 1
                    print(json.dumps(content, indent=2))
                    ruleloop = False
                case _ :
                    print('API call for filter rule #' + str(ruleNumber) + " failed, skipping")
                    ruleNumber += 1
        except:
            print('API call for filter rule #'+str(ruleNumber)+" failed, exiting")
            ruleloop = False
    return json.dumps(parsedResponse)

def createStormshieldNatRules(natRulesList):

    natRulesList = json.loads(natRulesList)
    ruleNumber = 1

    for natRule in natRulesList['objects']:
        name = natRule['name']
        originalSource = natRule['original-source']['name']
        originalDest = natRule['original-destination']['name']
        originalService = natRule['original-service']['name']
        translatedSource = natRule['translated-source']['name']
        translatedDest = natRule['translated-destination']['name']
        translatedService = natRule['translated-service']['name']
        installationTargets = []
        state = natRule['enabled']
        for target in natRule['install-on']:
            installationTargets.append(target['name'])
        if 'Policy Targets' in installationTargets or 'KMH-GatewayCluster' in installationTargets or 'All' in installationTargets:
            if translatedSource == "Original" and translatedDest == "Original" and translatedService == "Original":
                print('Nat rule #'+str(ruleNumber)+" is a no-nat rule, Skipping")
            else:
                if state:
                    query = "config filter rule insert index=10 type=nat state=on"
                else:
                    query = "config filter rule insert index=10 type=nat state=off"
            query += ' rulename="' + name + '" action=nat srctarget=' + originalSource + " dstport=" + originalService +" dsttarget=" + originalDest + " natsrctarget=" + translatedSource + " natdsttarget=" + translatedDest + " natdstport=" + translatedService
            print(query)
        else:
            print('Nat rule #'+ruleNumber+" has no right installation target")
        ruleNumber += 1

def main():
    natRulesList = getCheckpointNatRules()
    createStormshieldNatRules(natRulesList)

if __name__ == '__main__':
    main()