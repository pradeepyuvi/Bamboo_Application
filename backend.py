import requests
import xmltodict
from requests.auth import HTTPBasicAuth
import traceback
from base64 import b64encode
import urllib.parse
import os
import json
from bs4 import BeautifulSoup
import logging



def log(msg: str):
    logging.warning(msg)


def getBuildStatus(autHeader, buildId):
    try:
        s = requests.Session()
        s.verify = False
        headers = autHeader
        buildStatusUrl = f'{host}/rest/api/latest/result/{buildId}'
        log(buildStatusUrl)
        resp = s.get(buildStatusUrl, headers=headers).content
        resp = xmltodict.parse(resp)
        buildStatus = resp['results']['results']['result'][0]['buildState']
        buildNumber = resp['results']['results']['result'][0]['buildNumber']
        return {
            'buildStatus': buildStatus,
            "buildNumber": buildNumber
        }
    except:
        return {
            'buildStatus': 'build error',
            "buildNumber": ''
        }


def getEnvironmentStatus(autHeader, environmentId):
    try:
        s = requests.Session()
        s.verify = False
        headers = autHeader
        environmentStatusurl = f'{host}/rest/api/latest/deploy/project/{environmentId}'
        log(environmentStatusurl)
        resp = s.get(environmentStatusurl, headers=headers).content
        resp = json.loads(resp)
        resp = resp['environments'][0]['id']
        return resp
    except:
        return "errorr!!!"


def getDeploymentStatus(autHeader, deploymentId, index=0):
    try:
        s = requests.Session()
        s.verify = False
        headers = autHeader
        deploymentStatusurl = f'{host}/rest/api/latest/deploy/environment/{deploymentId}/results'
        resp = s.get(deploymentStatusurl, headers=headers)
        log(resp.status_code)
        resp = resp.content
        resp = json.loads(resp)
        # return resp
        return resp['results'][index]['id']
    except:
        return "errorr!!!"


def getDeploymentStatusLog(autHeader, deploymentLogId, deploymentId, index):
    try:
        s = requests.Session()
        s.verify = False
        headers = autHeader
        deploymentStatusLogurl = f'{host}/rest/api/latest/deploy/result/{deploymentLogId}?includeLogs=true'
        # log(deploymentStatusLogurl)
        resp = s.get(deploymentStatusLogurl, headers=headers)
        continueMsg = 'No new release created. Exiting'
        if resp.status_code == 200:
            resp = resp.content
            resp = json.loads(resp)
            deployStatus = resp['deploymentState']
            log(deployStatus)
            if deployStatus == 'FAILED':
                if continueMsg in str(resp):
                    log("found")
                    deploymentLogId = getDeploymentStatus(
                        autHeader, deploymentId, index)
                    log(deploymentLogId)
                    index = index+1
                    log(index)
                    return getDeploymentStatusLog(autHeader, deploymentLogId, deploymentId, index)
                else:
                    log("failde but not found")
                    return {
                        "formattedDate": resp['logEntries']['logEntry'][0]['formattedDate'],
                        "deploymentState": resp['deploymentState']
                    }
            else:
                log("seems succ")
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
    except:
        return "errorr!!!"


def getReleaseDeploymentStatus(autHeader, deploymentReleaseId, envName):
    try:
        s = requests.Session()
        s.verify = False
        headers = autHeader
        deploymentStatusurl = f'{host}/rest/api/latest/deploy/project/{deploymentReleaseId}'
        log(deploymentStatusurl)
        resp = s.get(deploymentStatusurl, headers=headers).content
        resp = json.loads(resp)
        for i in resp['environments']:
            if i['name'].startswith(envName):
                return i['id']
        return "enviroment not found"
    except:
        return "errorr!!!"


def genAuthHeader(user, pin):
    try:
        usrpass = b64encode(bytes(f"{user}:{pin}", 'utf-8'))
        usrpass = usrpass.decode("utf-8")
        AuthHeader = {'Authorization': f'Basic {usrpass}'}
        log(AuthHeader)
        return AuthHeader
    except:
        return "errorr!!!"


def getCommitStatus(autHeader, buildId, buildFetchId, buildNumber):
    try:
        s = requests.Session()
        s.verify = False
        headers = autHeader
        url = f'http://ci.swe.la.gov:8085/browse/{buildId}-{buildFetchId}-{buildNumber}/log'
        log(url)
        resp = s.get(url, headers=headers)
        log(resp.status_code)
        # log(resp.content)
        bsoup = BeautifulSoup(resp.content, 'lxml')

        table_buildFetchId = bsoup.body.find("table", {"id": "buildLog"})
        flag = False
        logsList = ""
        for i in table_buildFetchId.findAll("tr"):
            cells = i.findAll("td", {"class": "buildOutputLog"})
            if cells != []:
                logi = cells[0].find(text=True)
                # log(logi)
                if not flag:
                    if logi != None:
                        if logi.startswith("The tip"):
                            flag = True
                if flag:
                    if logi != None:
                        logsList = logsList + \
                            (cells[0].find(text=True) + ",  ")
        return logsList
    except:
        return "error!!!!"
    # log(table_buildFetchId.find("td"))

    # with open('htmRes.html', 'w') as file:
    #     file.write(str(resp.content.decode("utf-8")))


# def getNextScheduledTime(autHeader, deploymentId):
#     s = requests.Session()
#     s.verify = False
#     headers = autHeader
#     # TODO:// triggerId
#     nextScheduledTimeurl = f'http://ci.swe.la.gov:8085/deploy/config/editEnvironmentTrigger.action?environmentId={deploymentId}&triggerId=1'
#     log(nextScheduledTimeurl)
#     resp = s.get(nextScheduledTimeurl, headers=headers).content
#     # resp = json.loads(resp)
#     # resp = resp['environments'][0]['id']
#     bsoup = BeautifulSoup(resp, 'lxml')
#     table_buildLog = bsoup.body.find("span", {"id": "ctcronExpressionDisplay"})
#     logi = table_buildLog.find(text=True)
#     # with open('htmRe.html', 'w') as file:
#     #     file.write(str(resp.decode("utf-8")))
#     # log(logi)
#     cronId=logi
#     converturl=f'http://www.cronmaker.com/rest/sampler?expression={cronId}'
#     resp = s.get(converturl).content
#     # log(resp.decode("utf-8").split(","))
#     # log(cronId)
#     # log(converturl)
#     return resp.decode("utf-8").split(",")

# def getReleaseNextScheduledTime(cronId):
#     s = requests.Session()
#     s.verify = False
#     converturl=f'http://www.cronmaker.com/rest/sampler?expression={cronId}'
#     resp = s.get(converturl).content
#     # log(resp.decode("utf-8").split(","))
#     # log(cronId)
#     # log(converturl)
#     return resp.decode("utf-8").split(",")

def getNextScheduledData(cronExp):
    try:

        if cronExp == "no CronExpression":
            return " no CronExpression"
        else:
            s = requests.Session()
            s.verify = False
            converturl = f'http://www.cronmaker.com/rest/sampler?expression={cronExp}'
            resp = s.get(converturl).content
            # log(resp.decode("utf-8").split(","))
            # log(cronId)
            # log(converturl)
            return resp.decode("utf-8").split(",")
    except:
        return "errorr!!!"


host = 'http://ci.swe.la.gov:8085'

a = genAuthHeader('amey.maldikar', 'Nov.2022$')

# # log(getBuildStatus(a,'SIT-EED3HPCC)/)
# log(getReleaseDeploymentStatus('463077377','DEV6')) - all env (dev6) id

# a = genAuthHeader('amey.maldikar', 'Nov.2022$')

# log(getEnvironmentStatus(a, '211353604'))
# log(getDeploymentStatus(genAuthHeader('amey.maldikar', 'Nov.2022$'), '1315209222'))

# log(getDeploymentStatusLog('1373999432', '1315209222', 0))
# log(getBuildStatus(genAuthHeader('amey.maldikar', 'Nov.2022$'), "SIT-EEWPAB")['buildNumber'])

# log(getCommitStatus(genAuthHeader('amey.maldikar', 'Nov.$'), "SIT-EED1WP", "FP", "9280"))
# log(getNextScheduledTime(genAuthHeader('amey.maldikar', 'Nov.2022$')))

# log(getNextScheduledData('0 1 1-7/1,10-22/1 ? * *'))
