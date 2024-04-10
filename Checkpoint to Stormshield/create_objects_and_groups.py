##############################################################################################
#
#       Enable to export firewall objects and groups, rework them and import them to the Stormshield appliance
#             Works for the following objects :
#             - Hosts
#             - Networks
#             - Address ranges
#
#
##############################################################################################

import json, os

from variables import api_call, sid, fw_stormshield, CPmgmtIP

def getCheckpointHosts():
    limit = 200
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "standard"
    }
    parsedResponse = {}
    try:
        response = api_call(CPmgmtIP, 443, 'show-hosts', payload, sid)[0]
        parsedResponse['objects'] = response["objects"]
        total = int(response['total'])
        to = int(response['to'])
    except:
        print("API Call for hosts failed, skipping offset")

    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-hosts', payload, sid)[0]
            parsedResponse['objects'].extend(response["objects"])
            to = int(response['to'])
        except:
            print("API Call for hosts failed, skipping offset")

    return (parsedResponse)

def getCheckpointNetworks():
    limit = 200
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "standard"
    }
    parsedResponse = {}
    try:
        response = api_call(CPmgmtIP, 443, 'show-networks', payload, sid)[0]
        parsedResponse['objects'] = response["objects"]
        total = int(response['total'])
        to = int(response['to'])
    except:
        print("API call for Networks failed, skipping offset")
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-networks', payload, sid)[0]
            parsedResponse['objects'].extend(response["objects"])
            to = int(response['to'])
        except:
            print("API call for Networks failed, skipping offset")

    return (parsedResponse)

def getCheckpointAddressRanges():
    limit = 200
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "standard"
    }
    parsedResponse = {}
    try:
        response = api_call(CPmgmtIP, 443, 'show-address-ranges', payload, sid)[0]
        parsedResponse['objects'] = response["objects"]
        total = int(response['total'])
        to = int(response['to'])
    except:
        print("API Call for address ranges failed, skipping offset #1")
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-address-ranges', payload, sid)[0]
            parsedResponse['objects'].extend(response["objects"])
            to = int(response['to'])
        except:
            print("API Call for address ranges failed, skipping offset")
    return (parsedResponse)


def getCheckpointGroups():
    limit = 1
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "full"
    }
    parsedResponse = {}
    try:
        response = api_call(CPmgmtIP, 443, 'show-groups', payload, sid)[0]
        parsedResponse['objects'] = response["objects"]
        total = int(response['total'])
        to = int(response['to'])
    except:
        print("API call for object groups failed, skipping offset #1")
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-groups', payload, sid)[0]
            parsedResponse['objects'].extend(response["objects"])
            to = int(response['to'])
        except:
            print("API call for objects groups failed, skipping offset")
    return (parsedResponse)


def createNetworkGroups(groupsList):
    for group in groupsList["objects"]:
        groupName = group['name']
        comment = group['comments']
        query = "config  object group new name=" + groupName + ' comment="' + comment +'"'
        print(query)
        #print(fw_stormshield.send_command(query))

def makeObjectsList(hostsList, networkList, rangeList):
    jsonExtract = {
        "objects": []
    }
    for element in hostsList['objects']:
        if 'name' in element:
            payload = {
                "name": element['name'],
            }
            try:
                response = api_call(CPmgmtIP, 443, 'show-host', payload, sid)[0]
                jsonExtract['objects'].append(response)
            except:
                print("API call for object failed. Skipping. hostname : "+element['name'])
        else:
            print('No name for element, skipping object')

    for element in networkList['objects']:
        if 'name' in element:
            payload = {
                "name": element['name'],
            }
            try:
                response = api_call(CPmgmtIP, 443, 'show-network', payload, sid)[0]
                jsonExtract['objects'].append(response)
            except:
                print('API call for network object failed. Skipping. Networkname : '+element['name'])
        else:
            print('No name for element, skipping object')

    for element in rangeList['objects']:
        if 'name' in element:
            payload = {
                "name": element['name'],
            }
            try:
                response = api_call(CPmgmtIP, 443, 'show-address-range', payload, sid)[0]
                jsonExtract['objects'].append(response)
            except:
                print('API call for address range object failed. Skipping. Range : '+element['name'])
        else:
            print('No name for element, skipping object')
    return(json.dumps(jsonExtract))


def createStormshieldObjects(objectList):
    objectList = json.loads(objectList)
    for element in objectList['objects']:
        name = element['name']
        type = element["type"]
        comment = element['comments']
        groups = element['groups']
        match type:
            case "host":
                ipv4 = element['ipv4-address']
                query = "config object host new name="+ name + " ip=" + ipv4 + ' comment="' + comment +'"'
            case "network":
                if "subnet4" in element:
                    mask = element['subnet-mask']
                    subnet = element['subnet4']
                    query = "config object network new name="+ name + " ip=" + subnet +" mask="+ mask + ' comment="' + comment +'"'
                elif "subnet6" in element:
                    prefix = element['mask-length6']
                    subnet = element['subnet6']
                    query = "config object network new name="+ name + " ipv6=" + subnet +" prefixlenv6="+ str(prefix) + ' comment="' + comment +'"'
            case "address-range":
                startIP = element['ipv4-address-first']
                endIP = element['ipv4-address-last']
                query = "config object host new name="+ name + " begin=" + startIP +" end="+ endIP + ' comment="' + comment +'"'
        print(query)
        #print(fw_stormshield.send_command(query))

        if groups:
            for group in groups:
                addToGroup = "config object group addto group=" + group['name'] + " node=" + name
                print(addToGroup)
                #print(fw_stormshield.send_command(addToGroup))

def main():
    #print(fw_stormshield.send_command("modify on"))
    objectGroups = getCheckpointGroups()
    objectList = makeObjectsList(getCheckpointHosts(), getCheckpointNetworks(), getCheckpointAddressRanges())
    createNetworkGroups(objectGroups)
    createStormshieldObjects(objectList)
    #fw_stormshield.disconnect()

if __name__ == '__main__':
    main()