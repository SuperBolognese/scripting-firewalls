import json

from variables import api_call, sid, fw_stormshield

def getTCPServices():
    payload = {
        "limit": 2,
        "details-level": "standard"
    }
    #change the limit to the max to ensure to get all services (500) on Checkpoint
    response = api_call(CPmgmtIP, 443, 'show-services-tcp', payload, sid)
    return(response)


def getUDPServices():
    payload = {
        "limit": 2,
        "details-level": "standard"
    }

    #change the limit to the max to ensure to get all services (500) on Checkpoint
    response = api_call(CPmgmtIP, 443, 'show-services-udp', payload, sid)
    return(response)


def createServiceList(TCPserviceList, UDPserviceList):
    jsonExtract = {
        "objects": []
    }
    for element in TCPserviceList['objects']:
        payload = {
            "name": element['name'],
        }
        response = api_call(CPmgmtIP, 443, 'show-service-tcp', payload, sid)
        jsonExtract['objects'].append(response)

    for element in UDPserviceList['objects']:
        payload = {
            "name": element['name'],
        }
        response = api_call(CPmgmtIP, 443, 'show-service-udp', payload, sid)
        jsonExtract['objects'].append(response)


    return(json.dumps(jsonExtract))


def getCheckpointServiceGroups():
    print(sid)
    payload = {
        "limit": 2,
        "details-level": "full"
    }
    # change the limit to the max to ensure to get all services (500) on Checkpoint
    response = api_call(CPmgmtIP, 443, 'show-service-groups', payload, sid)
    return (response)

def createStormshieldServicegroups(servicegroups):
    for group in servicegroups['objects']:
        groupName = group['name']
        comment = group['comments']
        print(fw_stormshield.send_command("config global object servicegroup new name=" + groupName + ' comment="' + comment +'"'))

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
                query = "config global object service new name=" + serviceName + " port=" + startPort + ' proto='+ serviceType +' comment="' + comment + '" toport=' + endPort
            case x if ">" in x:
                startPort = str(int(str(port).replace(">", "")) + 1)
                query = "config global object service new name=" + serviceName + " port=" + startPort + ' proto='+ serviceType +' comment="' + comment + '" toport=65535'
            case _:
                query = "config global object service new name=" + serviceName + " port=" + port + ' proto='+ serviceType +' comment="' + comment + '"'
        print(fw_stormshield.send_command(query))
        if groups:
            for group in groups:
                addToGroup = "config global object servicegroup addto group=" + group['name'] + " node=" + serviceName
                print(fw_stormshield.send_command(addToGroup))


def main():
    print(fw_stormshield.send_command("modify on"))
    servicesList = createServiceList(getTCPServices(), getUDPServices())
    serviceGroups = getCheckpointServiceGroups()
    createStormshieldServicegroups(serviceGroups)
    createStormshieldServices(servicesList)
    fw_stormshield.disconnect()

main()