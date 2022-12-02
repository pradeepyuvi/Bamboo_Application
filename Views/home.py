from flet import *
from flet import dropdown
import flet
import json
from base64 import b64encode
from .gridviewchild import GridViewChild
import backend

class Home(UserControl):

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password
        self.projectDropDown = Ref[Dropdown]()
        self.envroiment = Ref[Dropdown]()
        self.buildEnv = Ref[Dropdown]()
        self.gridview = Ref[Dropdown]()
        self.showMsg = Ref[Dropdown]()
        self.loadButton=Ref[ElevatedButton]()
        self.projectData = {}
        self.envData = {}
        self.buildData = {}
        self.envIds = {}
        self.cronExp = {}
        self.triggerId={}
        self.buildFetchId={}

    @staticmethod
    def genAuthHeader(user, pin):
        usrpass = b64encode(bytes(f"{user}:{pin}", 'utf-8'))
        usrpass = usrpass.decode("utf-8")
        AuthHeader = {'Authorization': f'Basic {usrpass}'}
        return AuthHeader


    def loadDataFromJson(self, e):
        with open("FrontEnd\Views\dup.json") as json_file:
            data = json.load(json_file)
            for project in data["Projects"]:
                self.projectDropDown.current.options.append(
                    dropdown.Option(
                        text=project["name"],
                        key=project["name"],
                    )
                )
                self.projectData[project["name"]] = project["enviroment"]
                self.showProgress("Json Loaded Succfully")
        self.loadButton.current.disabled=True        
        self.update()

    def showProgress(self, txt: str):
        if txt is not None and txt != '':
            self.showMsg.current.value = txt
            self.update()

    def onChangeOnProject(self, e):
        self.envroiment.current.options.clear()
        for i in self.projectData[e.data]:
            self.envroiment.current.options.append(
                dropdown.Option(i["envnames"])
            )
            self.envData[e.data+i["envnames"]] = i["builds"]
        
        self.update()

    def onChangeOnEnv(self, e):
        self.buildEnv.current.options.clear()
        key = self.projectDropDown.current.value+e.data
        for i in self.envData[key]:
            self.buildEnv.current.options.append(
                dropdown.Option(i["Bname"])
            )
            tmpkey=key+i["Bname"]
            self.buildData[tmpkey] = i["buildids"]
            self.envIds[tmpkey] = i["envIds"]           
            self.buildFetchId[tmpkey]=i["buildFetchId"]
            self.cronExp[tmpkey] = i["cronExp"]
            # if "Release" in e.data:
            #     self.cronExp[tmpkey] = i["cronExp"]
            # if "Dev" in e.data:    
            #     self.triggerId[tmpkey]=i["triggerId"]
                
        self.update()

    def onChangeOnBuild(self, e):
        key = self.projectDropDown.current.value+self.envroiment.current.value+e.data
        self.gridview.current.controls.clear()

        '''
        4 task for n build ids and env ids
        #hashMap key->buildId | values ->{currentStatus,lastCompletedWithTime,lastCommit,nextScheduled}
        '''
        authHeader = Home.genAuthHeader(self.username, self.password)
        print(key)
        print(self.buildFetchId[key])
        for i, j, k, l in zip(self.buildData[key], self.envIds[key], self.buildFetchId[key], self.cronExp[key]):
            buildStatusAndNumber = backend.getBuildStatus(authHeader, i)
            status = buildStatusAndNumber['buildStatus']
            latestBuildNumber = buildStatusAndNumber['buildNumber']
            print(status)
            print(key)
            print(self.envroiment.current.value)
            scheduledTime=""
            if(status == 'Successful'):
                if ((self.envroiment.current.value).lower()).startswith("release"):
                    deploymentId = backend.getReleaseDeploymentStatus(authHeader, j, e.data)
                    print("@@@@")
                    print(k)
                    # cronExp=backend.getReleaseNextScheduledTime(k)
                else:
                    deploymentId = backend.getEnvironmentStatus(authHeader, j)
                    print(deploymentId)
                    # cronExp=backend.getNextScheduledTime(authHeader, deploymentId)

                deploymentLogId = backend.getDeploymentStatus(authHeader, deploymentId)
                print(deploymentLogId)
                finalStatus = backend.getDeploymentStatusLog(authHeader, deploymentLogId, deploymentId, 0)
                lastCommit = backend.getCommitStatus(authHeader, i, k , latestBuildNumber)
                print(finalStatus)
                scheduledTime=backend.getNextScheduledData(l)
                print(scheduledTime)
                self.gridview.current.controls.append(
                GridViewChild(e.data, i, self.showMsg, "deployment " + finalStatus['deploymentState'], finalStatus['formattedDate'], lastCommit, scheduledTime)
                )
            else:
                self.gridview.current.controls.append(
                    GridViewChild(e.data, i, self.showMsg, "Build " + status, "")
                )

        self.update()
    
    def build(self):

        return Container(
            content=Column(
                controls=[
                    Container(content=Row(controls=[ElevatedButton(
                        ref=self.loadButton,
                        content=Text("Load Data From Json"), on_click=self.loadDataFromJson),
                        Text(ref=self.showMsg, size=20)])),
                    Card(
                        Container(
                            height=100,
                            padding=20,
                            content=Row(
                                controls=[
                                    Dropdown(
                                        label="Projects",
                                        ref=self.projectDropDown,
                                        on_change=self.onChangeOnProject,
                                    ), Dropdown(
                                        label="Envtoiment",
                                        ref=self.envroiment,
                                        on_change=self.onChangeOnEnv,
                                    ),
                                    Dropdown(
                                        label="Applications",
                                        ref=self.buildEnv,
                                        on_change=self.onChangeOnBuild
                                    )
                                ]
                            )
                        )
                    ), Card(
                        content=Container(
                            height=500,                           
                            padding=5,
                            content=GridView(
                                expand=1,
                                runs_count=1,
                                max_extent=100,
                                width=1000,
                                spacing=100,
                                run_spacing=100,
                                ref=self.gridview,
                            )

                        )
                    )
                ]
            )
        )
