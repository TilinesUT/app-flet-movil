import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import flet as ft

from src.controllers.auth_controller import AuthController
from src.views.login_page import LoginPage
from src.views.dashboard_page import DashboardPage

def main(page: ft.Page) -> None:
    page.title = "Proyecto Movil"
    page.bgcolor = "#0f172a"
    page.padding = 0
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = False
    page.scroll = ft.ScrollMode.AUTO

    auth = AuthController()

    def navigate_to_login() -> None:
        page.controls.clear()
        login = LoginPage(page, on_success=navigate_to_dashboard)
        page.controls.append(login.build())
        page.update()

    def navigate_to_dashboard() -> None:
        page.controls.clear()
        dashboard = DashboardPage(page, on_logout=navigate_to_login)
        page.controls.append(dashboard.build())
        page.update()

    session = auth.restore_session()
    if session is not None:
        navigate_to_dashboard()
    else:
        navigate_to_login()


if __name__ == "__main__":
    view = os.environ.get("FLET_VIEW", "native")
    flet_view = (
        ft.AppView.WEB_BROWSER
        if view == "web"
        else ft.AppView.FLET_APP
    )
    ft.run(main, view=flet_view, port=8550)