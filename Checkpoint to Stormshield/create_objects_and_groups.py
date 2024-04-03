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
    limit = 1
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "standard"
    }
    parsedResponse = {}
    response = api_call(CPmgmtIP, 443, 'show-hosts', payload, sid)
    parsedResponse['objects'] = response["objects"]
    total = int(response['total'])
    to = int(response['to'])
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        response = api_call(CPmgmtIP, 443, 'show-hosts', payload, sid)
        parsedResponse['objects'].extend(response["objects"])
        to = int(response['to'])

    return(json.dumps(parsedResponse["objects"]))

def getCheckpointNetworks():
    limit = 1
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "standard"
    }
    parsedResponse = {}
    response = api_call(CPmgmtIP, 443, 'show-networks', payload, sid)
    total = int(response['total'])
    to = int(response['to'])
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        response = api_call(CPmgmtIP, 443, 'show-networks', payload, sid)
        parsedResponse['objects'].extend(response["objects"])
        to = int(response['to'])
    return (parsedResponse)

def getCheckpointAddressRanges():
    limit = 1
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "standard"
    }
    parsedResponse = {}
    response = api_call(CPmgmtIP, 443, 'show-address-ranges', payload, sid)
    total = int(response['total'])
    to = int(response['to'])
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        response = api_call(CPmgmtIP, 443, 'show-address-ranges', payload, sid)
        parsedResponse['objects'].extend(response["objects"])
        to = int(response['to'])
    return (parsedResponse)


def getCheckpointGroups():
    limit = 1
    payload = {
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        "limit": limit,
        "details-level": "full"
    }
    parsedResponse = {}
    response = api_call(CPmgmtIP, 443, 'show-groups', payload, sid)
    total = int(response['total'])
    to = int(response['to'])
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        response = api_call(CPmgmtIP, 443, 'show-groups', payload, sid)
        parsedResponse['objects'].extend(response["objects"])
        to = int(response['to'])
    return (parsedResponse)


def createNetworkGroups(groupsList):
    for group in groupsList["objects"]:
        groupName = group['name']
        comment = group['comments']
        uuid = group['uid']
        object = {
            "name": groupName,
            "uuid": uuid
        }
        query = "config global object group new name=" + groupName + ' comment="' + comment +'"'
        #print(fw_stormshield.send_command(query))

def makeObjectsList(hostsList, networkList, rangeList):
    jsonExtract = {
        "objects": []
    }
    for element in json.load(hostsList['objects']):
        payload = {
            "name": element['name'],
        }
        response = api_call(CPmgmtIP, 443, 'show-host', payload, sid)
        jsonExtract['objects'].append(response)

    for element in networkList['objects']:
        payload = {
            "name": element['name'],
        }
        response = api_call(CPmgmtIP, 443, 'show-network', payload, sid)
        jsonExtract['objects'].append(response)

    for element in rangeList['objects']:
        payload = {
            "name": element['name'],
        }
        response = api_call(CPmgmtIP, 443, 'show-address-range', payload, sid)
        jsonExtract['objects'].append(response)

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
                query = "config global object host new name="+ name + " ip=" + ipv4 + ' comment="' + comment +'"'
            case "network":
                if "subnet4" in element:
                    mask = element['subnet-mask']
                    subnet = element['subnet4']
                    query = "config global object network new name="+ name + " ip=" + subnet +" mask="+ mask + ' comment="' + comment +'"'
                elif "subnet6" in element:
                    prefix = element['mask-length6']
                    subnet = element['subnet6']
                    query = "config global object network new name="+ name + " ipv6=" + subnet +" prefixlenv6="+ str(prefix) + ' comment="' + comment +'"'
            case "address-range":
                startIP = element['ipv4-address-first']
                endIP = element['ipv4-address-last']
                query = "config global object host new name="+ name + " begin=" + startIP +" end="+ endIP + ' comment="' + comment +'"'
        print(query)
        print(fw_stormshield.send_command(query))

        if groups:
            for group in groups:
                addToGroup = "config global object group addto group=" + group['name'] + " node=" + name
                print(addToGroup)
                print(fw_stormshield.send_command(addToGroup))

def main():
    print(fw_stormshield.send_command("modify on"))
    objectGroups = getCheckpointGroups()
    objectList = makeObjectsList(getCheckpointHosts(), getCheckpointNetworks(), getCheckpointAddressRanges())
    createNetworkGroups(objectGroups)
    createStormshieldObjects(objectList)
    fw_stormshield.disconnect()

if __name__ == '__main__':
    main()