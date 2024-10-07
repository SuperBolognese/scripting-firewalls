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

import json, ipaddress

from variables import api_call, sid, CPmgmtIP

natFile = open('FILES/SNS_NAT_rules.txt', 'w')

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


def getCheckpointHost(hostname) :
    payload = {
        "name":hostname
    }
    # request to get IP of object OriginalDest for comparison
    response = api_call(CPmgmtIP, 443, 'show-host', payload, sid)
    content = response[0]
    code = response[1]

    match code:
        case 200:
            return content['ipv4-address'] + '/32'
        case 404:
            response = api_call(CPmgmtIP, 443, 'show-network', payload, sid)
            content_network = response[0]
            code_network = response[1]
            match code_network:
                case 200:
                    subnet = str(content_network['subnet4']) + '/' + str(content_network['mask-length4'])
                    return subnet
                case 404 :
                    response = api_call(CPmgmtIP, 443, 'show-address-range', payload, sid)
                    content_range = response[0]
                    code_range = response[1]
                    addr_range = content_range['ipv4-address-first'] + '/32'
                    match code_range:
                        case 200:
                            return addr_range
                        case 404:
                            print('Address range not found')
                        case 400:
                            print(content_range)
                        case _ :
                            print("Unknown error - Address range")
                case 400:
                    print(content_network)
                case _ :
                    print("Unknown error - Network")
        case 400 :
            print(content)
        case _ :
            print("unknown error - address")

def createStormshieldNatRules(natRulesList):

    query = ""
    natRulesList = json.loads(natRulesList)
    ruleNumber = 1
    for natRule in natRulesList['objects']:
        name = natRule['name']
        originalSource = natRule['original-source']['name']
        originalSourceIp = ipaddress.ip_network(getCheckpointHost(originalSource))
        originalDest = natRule['original-destination']['name']
        originalDestIp = ipaddress.ip_network(getCheckpointHost(originalDest))
        originalService = natRule['original-service']['name']
        translatedSource = natRule['translated-source']['name']
        translatedDest = natRule['translated-destination']['name']
        translatedService = natRule['translated-service']['name']
        installationTargets = []
        state = natRule['enabled']

        #iteration sur les installation targets pour déterminer si c'est ok
        for target in natRule['install-on']:
            installationTargets.append(target['name'])
        if 'Policy Targets' in installationTargets or 'KMH-GatewayCluster' in installationTargets or 'All' in installationTargets: #changer pour donner les installation targets
            if translatedSource == "Original" and translatedDest == "Original" and translatedService == "Original":
                print('Nat rule #'+str(ruleNumber)+" is a no-nat rule, Skipping", file=natFile)
            else:
                if state:
                    query = "config filter rule insert index=10 type=nat state=on"
                else:
                    query = "config filter rule insert index=10 type=nat state=off"
                query += ' rulename="' + name + '" action=nat srctarget=' + originalSource + " dstport=" + originalService +" dsttarget=" + originalDest

                #matching des règles de NAT sur les routes pour déterminer l'interface in/out
                if translatedSource != "Original" and translatedDest == "Original": #SNAT
                    with open('FILES/CP_static_routes') as routefile:
                        interface_nat = "out" #remplacer par le nom de l'interface par défaut
                        for route in routefile:
                            try:
                                dictRoute = str(route).split()
                                remoteSub = ipaddress.ip_network(dictRoute[2])
                                remoteSubGW = dictRoute[6] + "/24"
                                remoteSubGW = ipaddress.IPv4Interface(remoteSubGW)
                                if originalSourceIp.subnet_of(remoteSub) : #condition ok
                                    with open('FILES/SNS_interfaces.json') as intFile:
                                        intFile = json.load(intFile)
                                        for interface in intFile['interfaces']:
                                            dstInt = ipaddress.IPv4Interface(interface['ip-address'])
                                            if dstInt.network == remoteSubGW.network:
                                                interface_nat = interface['interface']
                                    break
                            except:
                                print("Route format error, skipping")
                        query += " dstif=" + interface_nat + " natsrctarget=" + translatedSource + " natsrcport=ephemeral_fw"


                elif translatedSource == "Original" and translatedDest != "Original": #DNAT
                    with open('FILES/CP_static_routes') as routefile:
                        interface_nat = "out"
                        for route in routefile:
                            try:
                                dictRoute = str(route).split()
                                remoteSub = ipaddress.ip_network(dictRoute[2])
                                remoteSubGW = dictRoute[6] + "/24"
                                remoteSubGW = ipaddress.IPv4Interface(remoteSubGW)
                                if originalDestIp.subnet_of(remoteSub):  # condition ok
                                    with open('FILES/SNS_interfaces.json') as intFile:
                                        intFile = json.load(intFile)
                                        for interface in intFile['interfaces']:
                                            dstInt = ipaddress.IPv4Interface(interface['ip-address'])
                                            if dstInt.network == remoteSubGW.network:
                                                interface_nat = interface['interface']
                                    break
                            except:
                                print('route format error')
                        query += " srcif=" + interface_nat + " natdsttarget=" + translatedDest

                elif translatedSource == "Original" and translatedDest == "Original" and translatedService != "Original": #PAT
                    query += " natdstport=" + translatedService + " natdsttarget=" + originalDest

                elif translatedSource != "Original" and translatedDest != "Original":
                    continue
                print(query, file=natFile)
                ruleNumber +=1

def main():
    natRulesList = getCheckpointNatRules()
    createStormshieldNatRules(natRulesList)

if __name__ == '__main__':
    main()