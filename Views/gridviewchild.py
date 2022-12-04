from flet import *
from flet import colors


class GridViewChild(UserControl):
    def __init__(self, name, bulidid, showMsg, curStatus, lastCompletedWithTime, lastCommit, cronTime, appName):
        super().__init__()
        self.name = name
        self.buildid = bulidid
        self.currentStatus = curStatus
        self.lastCompletedWithTime = lastCompletedWithTime
        self.lastCommit = lastCommit
        self.nextScheduled = cronTime
        # use showMsg method refernce to show error or success msgs
        self.showMsg = showMsg
        self.appName = appName

    def build(self):
        return Card(
            elevation=5,
            margin=3,
            content=Column(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Text(self.name, color=colors.PURPLE),
                                Row(controls=[
                                    Text("Application Name ->",
                                         color=colors.YELLOW),
                                    Text(
                                        f"{self.appName}",color=colors.YELLOW),
                                ]),
                                # Row(controls=[
                                #     Text("Build id ->",
                                #          color=colors.YELLOW),
                                #     Text(
                                #         f"{self.buildid}"),
                                # ]),
                                # controls=[
                                #     Text("Build id ->",
                                #          color=colors.PURPLE),
                                #     Text(
                                #         f"{self.buildid}"),
                                # ],
                                # Text(f"Build id ->", color=colors.PURPLE{self.buildid}""),
                            ]
                        )
                    ),
                    Container(
                        padding=4,
                        content=Column(
                            controls=[
                                Row(controls=[
                                    Text("Current status :-",
                                         color=colors.GREEN),
                                    Text(
                                        f"{self.currentStatus}"),
                                ]),
                                Row(controls=[
                                    Text("Last completed with time :-",
                                         color=colors.GREEN),
                                    Text(
                                        f"{self.lastCompletedWithTime}"),
                                ]),
                                Column(controls=[
                                    Text("Last commit :-",
                                         color=colors.GREEN),
                                    Text(
                                        f"{self.lastCommit}"),
                                ]),
                                Column(controls=[
                                    Text("Next scheduled:-",
                                         color=colors.GREEN),
                                    Text(
                                        f"{self.nextScheduled}"),
                                ]),
                                                               
                            ]
                        )

                    )
                ]
            )
        )
