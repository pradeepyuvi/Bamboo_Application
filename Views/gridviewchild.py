from flet import *


class GridViewChild(UserControl):
    def __init__(self, name, bulidid,showMsg, curStatus, lastCompletedWithTime, lastCommit, cronTime):
        super().__init__()
        self.name = name
        self.buildid = bulidid
        self.currentStatus = curStatus
        self.lastCompletedWithTime = lastCompletedWithTime
        self.lastCommit = lastCommit
        self.nextScheduled = cronTime
        # use showMsg method refernce to show error or success msgs
        self.showMsg=showMsg

    def build(self):
        return Card(
            elevation=5,
            margin=3,
            content=Column(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Text(self.name),
                                Text(
                                    f"Build Id -> {self.buildid}")
                            ]
                        )
                    ),
                    Container(
                        padding=4,
                        content=Column(
                            controls=[
                                Text(
                                    f"Current status :- {self.currentStatus}"),
                                Text(
                                    f"Last completed with time :- {self.lastCompletedWithTime}"),
                                Text(
                                    f"Last commit :- {self.lastCommit}"),
                                Text(
                                    f"Next scheduled:- {self.nextScheduled}"),
                            ]
                        )

                    )
                ]
            )
        )
