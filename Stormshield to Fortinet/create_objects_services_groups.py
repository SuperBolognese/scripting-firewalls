import csv

file = open('INPUT FILES/local_objects.csv', 'r')

reader = csv.reader(file, delimiter=',')

for row in reader:
    type = row[0]
    name = row[1]

    match type:
        case "host":
            address = row[2]
            comment = row[6]
            if address != "":
                print("edit " + name)
                print("set subnet " + address + "/32")
                print("set comment " + '"' + comment + '"' + "\n")

        case "range":
            startip = row[2]
            endip = row[3]
            comment = row[8]
            print("edit " + name)
            print("set start-ip " + startip)
            print("set end-ip " + endip)
            print("set comment " + '"' + comment + '"' + "\n")

        case "network":
            subnet = row[2]
            mask = row[4]
            comment = row[7]
            if subnet != "":
                print("edit " + name)
                print("set subnet " + subnet + "/" + mask)
                print("set comment " + '"' + comment + '"' + "\n")

        case "group":
            command = ""
            comment = row[3]
            for member in row[2].split(','):
                command += '"' + member + '" '
            print("edit " + name)
            print('set member ' + command)
            print('set comment "' + comment + '"\n')


        case "service":
            protocol = row[2]
            port = row[3]
            endport = row[4]
            comment = row[5]
            if endport != "":
                if protocol == "tcp" or protocol == "udp":
                    print("edit " + name)
                    print('set ' + protocol + '-portrange ' + port + '-' + endport)
                    print('set comment "' + comment + '"\n')
                else:
                    print("edit " + name)
                    print('set tcp-portrange ' + port + '-' + endport)
                    print('set udp-portrange ' + port + '-' + endport)
                    print('set comment "' + comment + '"\n')
            else:
                if protocol == "tcp" or protocol == "udp":
                    print("edit " + name)
                    print('set ' + protocol + '-portrange ' + port)
                    print('set comment "' + comment + '"\n')
                else:
                    print("edit " + name)
                    print('set tcp-portrange ' + port)
                    print('set udp-portrange ' + port)
                    print('set comment "' + comment + '"\n')

        case "servicegroup":
            command = ""
            comment = row[3]
            for member in row[2].split(','):
                command += '"' + member + '" '
            print("edit " + name)
            print('set member ' + command)
            print('set comment "' + comment + '"\n')