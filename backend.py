import requests
import xmltodict
from requests.auth import HTTPBasicAuth
import traceback
from base64 import b64encode
import urllib.parse
import os
import json

def getBuildStatus(autHeader, buildId):
    s = requests.Session()
    s.verify = False
    headers = autHeader
    buildStatusUrl = f'{host}/rest/api/latest/result/{buildId}'
    print(buildStatusUrl)
    resp = s.get(buildStatusUrl, headers=headers).content
    resp = xmltodict.parse(resp)
    buildStatus = resp['results']['results']['result'][0]['buildState']
    buildNumber = resp['results']['results']['result'][0]['buildNumber']
    return {
        'buildStatus' : buildStatus,
        "buildNumber": buildNumber
    }


def getEnvironmentStatus(autHeader, environmentId):
    s = requests.Session()
    s.verify = False
    headers = autHeader
    environmentStatusurl = f'{host}/rest/api/latest/deploy/project/{environmentId}'
    print(environmentStatusurl)
    resp = s.get(environmentStatusurl, headers=headers).content
    resp = json.loads(resp)
    resp = resp['environments'][0]['id'] 
    return resp

def getDeploymentStatus(autHeader, deploymentId, index = 0):
    s = requests.Session()
    s.verify = False
    headers = autHeader
    deploymentStatusurl = f'{host}/rest/api/latest/deploy/environment/{deploymentId}/results'
    resp = s.get(deploymentStatusurl, headers=headers)
    print(resp.status_code)
    resp = resp.content
    resp = json.loads(resp)
    # return resp
    return resp['results'][index]['id']

def getDeploymentStatusLog(autHeader, deploymentLogId, deploymentId, index):
    s = requests.Session()
    s.verify = False
    headers = autHeader
    deploymentStatusLogurl = f'{host}/rest/api/latest/deploy/result/{deploymentLogId}?includeLogs=true'
    # print(deploymentStatusLogurl)
    resp = s.get(deploymentStatusLogurl, headers=headers)
    continueMsg='No new release created. Exiting'
    if resp.status_code == 200:
        resp = resp.content
        resp = json.loads(resp)
        deployStatus=resp['deploymentState']
        print(deployStatus)
        if deployStatus == 'FAILED':
            if continueMsg in str(resp):
                print("found")
                deploymentLogId = getDeploymentStatus(autHeader, deploymentId, index)
                print(deploymentLogId)
                index=index+1
                print(index)
                return getDeploymentStatusLog(autHeader, deploymentLogId, deploymentId, index)
            else:
                print("failde but not found")
                return {
                    "formattedDate": resp['logEntries']['logEntry'][0]['formattedDate'],
                    "deploymentState": resp['deploymentState']
                }
        else:
            print("seems succ")
            return {
                "formattedDate": resp['logEntries']['logEntry'][0]['formattedDate'],
                "deploymentState": resp['deploymentState']
            }
    else:
        return {
            "msg": "something wnet wrong",
            "status code": resp.status_code,
            "response": json.loads(resp.content)
        }

def getReleaseDeploymentStatus(autHeader, deploymentReleaseId, envName):
    s = requests.Session()
    s.verify = False
    headers = autHeader
    deploymentStatusurl = f'{host}/rest/api/latest/deploy/project/{deploymentReleaseId}'
    print(deploymentStatusurl)
    resp = s.get(deploymentStatusurl, headers=headers).content
    resp = json.loads(resp)
    for i in resp['environments']:
        if i['name'].startswith(envName):
          return i['id']
    return "enviroment not found"

def genAuthHeader(user, pin):
        usrpass = b64encode(bytes(f"{user}:{pin}", 'utf-8'))
        usrpass = usrpass.decode("utf-8")
        AuthHeader = {'Authorization': f'Basic {usrpass}'}
        print(AuthHeader)
        return AuthHeader
        

from bs4 import BeautifulSoup

def getCommitStatus(autHeader, buildId, buildFetchId, buildNumber):
    s = requests.Session()
    s.verify = False
    headers = autHeader
    url = f'http://ci.swe.la.gov:8085/browse/{buildId}-{buildFetchId}-{buildNumber}/log'
    print(url)
    resp = s.get(url, headers=headers)
    print(resp.status_code)
    print(resp.content)
    bsoup = BeautifulSoup(resp.content, 'lxml')

    table_buildFetchId = bsoup.body.find("table", {"id": "buildFetchId"})
    flag = False
    logsList = ""
    for i in table_buildFetchId.findAll("tr"):
        cells = i.findAll("td", {"class": "buildOutputLog"})
        if cells != []:
            logi = cells[0].find(text=True)
            # print(logi)
            if not flag:
                if logi != None:
                    if logi.startswith("The tip"):
                        flag = True
            if flag:
                if logi != None:
                    logsList = logsList + (cells[0].find(text=True) + ",  ")
    return logsList
    # print(table_buildFetchId.find("td"))
    
    # with open('htmRes.html', 'w') as file:
    #     file.write(str(resp.content.decode("utf-8")))


# def getNextScheduledTime(autHeader, deploymentId):
#     s = requests.Session()
#     s.verify = False
#     headers = autHeader
#     # TODO:// triggerId
#     nextScheduledTimeurl = f'http://ci.swe.la.gov:8085/deploy/config/editEnvironmentTrigger.action?environmentId={deploymentId}&triggerId=1'
#     print(nextScheduledTimeurl)
#     resp = s.get(nextScheduledTimeurl, headers=headers).content
#     # resp = json.loads(resp)
#     # resp = resp['environments'][0]['id'] 
#     bsoup = BeautifulSoup(resp, 'lxml')
#     table_buildLog = bsoup.body.find("span", {"id": "ctcronExpressionDisplay"})
#     logi = table_buildLog.find(text=True)
#     # with open('htmRe.html', 'w') as file:
#     #     file.write(str(resp.decode("utf-8")))
#     # print(logi)
#     cronId=logi
#     converturl=f'http://www.cronmaker.com/rest/sampler?expression={cronId}'
#     resp = s.get(converturl).content
#     # print(resp.decode("utf-8").split(","))
#     # print(cronId)
#     # print(converturl)
#     return resp.decode("utf-8").split(",")

# def getReleaseNextScheduledTime(cronId):
#     s = requests.Session()
#     s.verify = False
#     converturl=f'http://www.cronmaker.com/rest/sampler?expression={cronId}'
#     resp = s.get(converturl).content
#     # print(resp.decode("utf-8").split(","))
#     # print(cronId)
#     # print(converturl)
#     return resp.decode("utf-8").split(",")  

def getNextScheduledData(cronExp):
    s = requests.Session()
    s.verify = False
    converturl=f'http://www.cronmaker.com/rest/sampler?expression={cronExp}'
    resp = s.get(converturl).content
    # print(resp.decode("utf-8").split(","))
    # print(cronId)
    # print(converturl)
    return resp.decode("utf-8").split(",")      

host = 'http://ci.swe.la.gov:8085'

a = genAuthHeader('amey.maldikar', 'Nov.2022$')

# print(getBuildStatus(a,'SIT-EED1WP'))
# print(getReleaseDeploymentStatus('463077377','DEV6')) - all env (dev6) id

# a = genAuthHeader('amey.maldikar', 'Nov.2022$')

# print(getEnvironmentStatus(a, '211353604'))
# print(getDeploymentStatus(genAuthHeader('amey.maldikar', 'Nov.2022$'), '1315209222'))

# print(getDeploymentStatusLog('1373999432', '1315209222', 0))
# print(getBuildStatus(genAuthHeader('amey.maldikar', 'Nov.2022$'), "SIT-EEWPAB")['buildNumber'])

# print(getCommitStatus(genAuthHeader('amey.maldikar', 'Nov.2022$'), "SIT-EED1WP", "9280"))
# print(getNextScheduledTime(genAuthHeader('amey.maldikar', 'Nov.2022$')))

# print(getReleaseNextScheduledTime('0 1 1-7/1,10-22/1 ? * *'))