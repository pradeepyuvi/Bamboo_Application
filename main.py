from urllib.parse import parse_qs, urlparse

import flet
from flet import *
from flet import colors, dropdown, icons, padding
from Views import home


class Main(UserControl):
    def __init__(self):
        super().__init__()
        self.username = Ref[TextField]()
        self.password = Ref[TextField]()

    def login(self, e):
        if (self.username.current.value == ''):
            self.username.focus()
            return
        if (self.password.current.value == ''):
            self.password.focus()
            return
        self.page.go("home", username=self.username.current.value,
                     password=self.password.current.value)

    def build(self):
        return Row(
            vertical_alignment='center',
            controls=[
                Column(
                    controls=[TextField(ref=self.username, label="UserName"),
                              TextField(ref=self.password, label="Password",
                                        password=True),
                              ElevatedButton(
                        text="Login", on_click=self.login),
                    ],
                ),

            ],
            alignment="center"
        )


def main(page: Page):

    def logout(e):
        nonlocal isusernameandpasswordSetted
        isusernameandpasswordSetted = False
        toppage = page.views[0]
        page.views.clear()
        page.views.append(toppage)
        page.update()
    page.title = "bamboo build"
    page.horizontal_alignment = "center"
    page.update()

    isusernameandpasswordSetted = False
    # create application instance

    app = Main()

    # add application's root control to the page
    page.add(app)

    username = ""
    password = ""

    def onRouteChange(e):
        nonlocal isusernameandpasswordSetted, username, password

        parserdurl = urlparse(e.data)
        parameters = parse_qs(parserdurl.query)

        print(f"Navigate to /{parserdurl.path} with parameter of {parameters}")

        if (not isusernameandpasswordSetted and 'username' in parameters and 'password' in parameters):
            username = parameters["username"][0]
            password = parameters["password"][0]
            isusernameandpasswordSetted = False

        if (parserdurl.path == "home"):
            page.views.append(View(
                "/home",
                [
                    home.Home(username, password)
                ],
                vertical_alignment="center",
                horizontal_alignment="center", appbar=AppBar(title=Text("Bamboo"), leading_width=40, bgcolor=colors.SURFACE_VARIANT, center_title=True, )),
            )
        page.update()

    def onViewPop(e):
        page.views.pop()
        top_view = page.views[len(page.views)-1]
        page.go(top_view.route)

    page.on_route_change = onRouteChange
    page.on_view_pop = onViewPop


flet.app(target=main)
