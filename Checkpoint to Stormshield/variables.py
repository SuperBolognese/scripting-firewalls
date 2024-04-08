from stormshield.sns.sslclient import SSLClient
import requests, json

#stormshield informations variable
#change values with your informations
fw_stormshield = SSLClient(
    host='10.43.193.169', port=443,
    user='admin', password='Tibiscuit_666$',
    sslverifyhost=False
)

#method to make API calls to the checkpoint management appliance
#must have enabled API beforehand : https://community.checkpoint.com/t5/API-CLI-Discussion/Enabling-web-api/td-p/32641

CPmgmtIP = '10.43.193.25'

def api_call(ip_addr, port, command, json_payload, sid):
    url = 'https://' + ip_addr + ':' + str(port) + '/web_api/' + command
    if sid == '':
        request_headers = {'Content-Type' : 'application/json'}
    else:
        request_headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}
    r = requests.post(url,data=json.dumps(json_payload), headers=request_headers, verify=False)
    return r.json(),r.status_code

#method to get the SID to make API calls to the Checkpoint SmartCenter
def login(user,password):
    payload = {'user':user, 'password' : password}
    response = api_call(CPmgmtIP, 443, 'login',payload, '')[0]
    return response["sid"]

#put the SmartCenter credentials here
sid = login('admin','admin1')