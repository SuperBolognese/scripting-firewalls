import json

from variables import api_call, sid, CPmgmtIP

def getTCPServices():
    limit = 500
    parsedResponse = {
        "objects":[]
    }
    payload = {
        "limit": limit,
        "details-level": "standard"
    }
    #change the limit to the max to ensure to get all services (500) on Checkpoint
    try:
        response = api_call(CPmgmtIP, 443, 'show-services-tcp', payload, sid)[0]
    except:
        print("Error occured, skipping offset")
    parsedResponse['objects'].extend(response["objects"])
    total = response['total']
    to = response['to']
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset":offset
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-services-tcp', payload, sid)[0]
        except:
            print("Error occured, skipping offset TCP")
        parsedResponse['objects'].extend(response["objects"])
        to = response['to']
    return(json.dumps(parsedResponse, indent=2))

def getUDPServices():
    limit = 500
    parsedResponse = {
        "objects": []
    }
    payload = {
        "limit": limit,
        "details-level": "standard"
    }

    #change the limit to the max to ensure to get all services (500) on Checkpoint
    try:
        response = api_call(CPmgmtIP, 443, 'show-services-udp', payload, sid)[0]
    except:
        print("Error occured, skipping offset UDP")
    parsedResponse['objects'].extend(response["objects"])
    total = response['total']
    to = response['to']
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-services-udp', payload, sid)[0]
        except:
            print("Error occured, skipping offset UDP")
        parsedResponse['objects'].extend(response["objects"])
        to = response['to']
    return (json.dumps(parsedResponse, indent=2))


def createServiceList(TCPserviceList, UDPserviceList):
    jsonExtract = {
        "objects": []
    }
    TCPserviceList = json.loads(TCPserviceList)
    UDPserviceList = json.loads(UDPserviceList)
    for element in TCPserviceList['objects']:
        if 'name' in element:
            payload = {
                "name": element['name'],
            }
            try:
                response = api_call(CPmgmtIP, 443, 'show-service-tcp', payload, sid)[0]
            except:
                print("API Call failed, skipping TCP service name="+element['name'])
            jsonExtract['objects'].append(response)
        else:
            print("Skipping element, no name defined")
    for element in UDPserviceList['objects']:
        if 'name' in element:
            payload = {
                "name": element['name'],
            }
            try:
                response = api_call(CPmgmtIP, 443, 'show-service-udp', payload, sid)[0]
            except:
                print("API Call failed, skipping UDP service name="+element['name'])
            jsonExtract['objects'].append(response)
        else:
            print("Skipping element, no name defined")
    return(json.dumps(jsonExtract))


def getCheckpointServiceGroups():
    limit = 500
    parsedResponse = {
        "objects": []
    }
    payload = {
        "limit": limit,
        "details-level": "standard"
    }
    try:
        # change the limit to the max to ensure to get all services (500) on Checkpoint
        response = api_call(CPmgmtIP, 443, 'show-service-groups', payload, sid)[0]
    except:
        print("API Call failed, skipping service group offset")
    parsedResponse['objects'].extend(response["objects"])
    total = response['total']
    to = response['to']
    while total > to:
        offset = to
        payload = {
            "limit": limit,
            "details-level": "standard",
            "offset": offset
        }
        try:
            response = api_call(CPmgmtIP, 443, 'show-service-groups', payload, sid)[0]
        except:
            print("API Call failed, skipping offset")
        parsedResponse['objects'].extend(response["objects"])
        to = response['to']
    return (json.dumps(parsedResponse, indent=2))

def createServiceGroupsList(groupsList):
    jsonExtract = {
        "objects": []
    }
    groupsList = json.loads(groupsList)
    for element in groupsList['objects']:
        if 'name' in element:
            payload = {
                "name": element['name'],
            }
            try:
                response = api_call(CPmgmtIP, 443, 'show-service-group', payload, sid)[0]
            except:
                print("API call for group failed, skipping. GroupName : "+element['name'])
            jsonExtract['objects'].append(response)
        else:
            print('No name element for group, skipping')
    return (json.dumps(jsonExtract))

def createStormshieldServicegroups(servicegroups):
    servicegroups = json.loads(servicegroups)
    for group in servicegroups['objects']:
        groupName = group['name']
        comment = group['comments']
        query = "config  object servicegroup new name=" + groupName + ' comment="' + comment +'"'
        print(query)
        #print(fw_stormshield.send_command(query))

def createStormshieldServices(servicesList):
    servicesList = json.loads(servicesList)
    for service in servicesList['objects']:
        serviceName = service['name'].replace(" ", "_")
        port = service['port']
        comment = service['comments']
        type = service['type']
        groups = service['groups']
        match type:
            case x if "tcp" in x:
                serviceType = "tcp"
            case x if "udp" in x:
                serviceType = "udp"
        match port:
            case x if "-" in x:
                startPort = port[0: port.index("-")]
                endPort = port[port.index("-") + len("-"):]
                query = "config  object service new name=" + serviceName + " port=" + startPort + ' proto='+ serviceType +' comment="' + comment + '" toport=' + endPort
            case x if ">" in x:
                startPort = str(int(str(port).replace(">", "")) + 1)
                query = "config  object service new name=" + serviceName + " port=" + startPort + ' proto='+ serviceType +' comment="' + comment + '" toport=65535'
            case _:
                query = "config  object service new name=" + serviceName + " port=" + port + ' proto='+ serviceType +' comment="' + comment + '"'
        print(query)
        #print(fw_stormshield.send_command(query))

        if groups:
            for group in groups:
                addToGroup = "config  object servicegroup addto group=" + group['name'] + " node=" + serviceName
                print(addToGroup)
                #print(fw_stormshield.send_command(addToGroup))


def main():
    #print(fw_stormshield.send_command("modify on"))
    servicesList = createServiceList(getTCPServices(), getUDPServices())
    serviceGroups = createServiceGroupsList(getCheckpointServiceGroups())
    createStormshieldServicegroups(serviceGroups)
    createStormshieldServices(servicesList)
    #fw_stormshield.disconnect()

if __name__ == '__main__':
    main()