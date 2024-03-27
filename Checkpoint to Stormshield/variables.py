from stormshield.sns.sslclient import SSLClient
import requests, json

#stormshield informations variable
#change values with your informations
fw_stormshield = SSLClient(
    host='your_stormshield_IP', port=443,
    user='admin', password='password',
    sslverifyhost=False
)

#method to make API calls to the checkpoint management appliance
#must have enabled API beforehand : https://community.checkpoint.com/t5/API-CLI-Discussion/Enabling-web-api/td-p/32641

CPmgmtIP = 'SmartCenter_mgmt_IP'

def api_call(ip_addr, port, command, json_payload, sid):
    url = 'https://' + ip_addr + ':' + str(port) + '/web_api/' + command
    if sid == '':
        request_headers = {'Content-Type' : 'application/json'}
    else:
        request_headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}
    r = requests.post(url,data=json.dumps(json_payload), headers=request_headers, verify=False)
    return r.json()

#method to get the SID to make API calls to the Checkpoint SmartCenter
def login(user,password):
    payload = {'user':user, 'password' : password}
    response = api_call(CPmgmtIP, 443, 'login',payload, '')
    return response["sid"]

#put the SmartCenter credentials here
sid = login('admin','password')
