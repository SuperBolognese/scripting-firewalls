import ipaddress, json

routeFile = open('FILES/SNS_static_routes.txt',"w")
def getIPSubnet(ipAddr,mask):
    interface_network = ipaddress.IPv4Interface(str(ipAddr + "/" + mask))
    return interface_network

def createSNSRoutes():

    #iteration on all the routes declared on the CP
    with open('FILES/CP_static_routes') as routingFile:
        for route in routingFile:
            routeIndex = route.split()
            destSubnet = routeIndex[2]
            gw = routeIndex[6]
            gw_network = getIPSubnet(gw,'24')
            gw_network = ipaddress.IPv4Interface(gw_network)
            gwName = ""
            destName = ""

            #matching ip address and compare to network/address objects in the previously created file
            with open('FILES/SNS_objects.txt') as objectFile:
                for object in objectFile:
                    object = object.split()
                    name = str(object[4].lstrip('name='))
                    if object[2] == "network":
                        mask = str(object[6].lstrip('mask='))
                        ipAddrDestination = object[5].lstrip('ip=') + "/" + mask
                    elif object[2] == "host":
                        ipAddrDestination = object[5].lstrip('ip=')
                    else:
                        ipAddrDestination = ""

                    try:
                        if destSubnet == str(ipaddress.ip_network(ipAddrDestination)):
                            destName = name
                        if gw == ipAddrDestination:
                            gwName = name
                    except:
                        continue


            query = "config network route add remote=" + destName + " gateway=" + gwName + " interface="

            #matching interface with gateway network and put it in the query
            with open('FILES/SNS_interfaces.json') as intFile:
                intFile = json.load(intFile)
                for interface in intFile['interfaces']:
                    if ipaddress.IPv4Interface(interface['ip-address']) in gw_network.network:
                        query += interface['interface']

            print(query, file=routeFile)
def main():
    createSNSRoutes()

if __name__ == '__main__':
    main()
