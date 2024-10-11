import csv

file = open('INPUT FILES/filter_nat_rules.csv', 'r')
configFile = open('OUTPUT/filter_rules.txt', 'w')

reader = csv.reader(file, delimiter=',')
rule_id = 1
for row in reader:
    type = row[0]
    name = row[3]
    comment = row[4]
    state = row[5]
    action = row[6]
    inspection = row[10]
    log_level = row[12]
    schedule = row[13]

    match type:
        case "local_filter_slot":  #filer rule
            ip_proto = row[17]
            user = row[19]
            src = row[22]
            srcport = row[26]
            srcif = row[27]
            dst = row[29]
            dstport = row[33]
            dstif = row[34]
            srcaddr =''
            dstaddr = ''
            to_port = ''

            if state == "on":
                print("edit " + str(rule_id), file=configFile)

                if srcif != "": #source interface
                    print("set srcintf " + srcif, file=configFile)
                else: print('set srcintf "any"', file=configFile)

                if dstif != "": #destination interface
                    print("set dstintf " + dstif, file=configFile)
                else: print('set dstintf "any"', file=configFile)

                for member in src.split(','): #sources address/groups
                    srcaddr += '"' + member + '" '
                if srcaddr == '"any" ':
                    srcaddr = '"all"'
                print("set srcaddr " + srcaddr, file=configFile)

                for member in dst.split(','): #destination address/groups
                    dstaddr += '"' + member + '" '
                if dstaddr == '"any" ':
                    dstaddr = '"all"'
                print("set dstaddr " + dstaddr, file=configFile)

                for member in dstport.split(','): #services
                    to_port += '"' + member + '" '

                if to_port == '"any" ':
                    print('set service "all"', file=configFile)
                else : print("set service " + to_port, file=configFile)

                print('set name "' + name + '"', file=configFile)
                print('set comment "' + comment + '"', file=configFile)

                if state == "on":
                    state = 'enable'
                else: state = "disable"
                print("set status " + state, file=configFile)

                if action == 'pass' or action == 'decrypt':
                    action = 'accept'
                else:
                    action = 'deny'
                print('set action ' + action, file=configFile)
                print('set logtraffic ' + log_level, file=configFile)
                print('next \n', file=configFile)
                rule_id += 1