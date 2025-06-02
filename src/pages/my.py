"""我的页面"""

import flet as ft
import models


class MyPage(ft.View):
    """我的页面"""

    def __init__(self, globals_var: models.Globals):
        super().__init__()

        self.page = globals_var.page
        self.api = globals_var.music_api
        self.globals = globals_var
        self.route = "/my"
        self.adaptive = True
        self.can_pop = False
        self.padding = ft.padding.all(20)
        self.is_login = False

        # AppBar
        self.appbar = ft.AppBar(
            title=ft.Text("我的"),
            automatically_imply_leading=False,  # 禁用自动返回按钮
        )

        # 底部导航栏
        self.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="推荐"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="我的"),
            ],
            selected_index=1,  # 默认选中"我的"标签
            on_change=self.nav_change
        )

        # 主要内容区域
        self.controls = [
            ft.Text("正在加载", size=20),
        ]

        self.load_view()  # 加载页面内容
    
    def load_view(self):
        """加载页面"""
        self.controls.clear()

        if self.api.login_status().account:
            self.is_login = True
            self.controls.append(
                ft.ElevatedButton(
                    text="退出登录",
                    on_click=self.login,
                )
            )
        else:
            self.is_login = False
            self.controls.append(
                ft.ElevatedButton(
                    text="前往登录",
                    on_click=self.login,
                )
            )
    
    def login(self, e):
        """登录"""
        self.page.go("/login")  # type: ignore
    
    def logout(self, e):
        """退出登录"""
        self.globals.logout()

    def nav_change(self, e):
        """处理导航栏切换"""
        if e.control.selected_index == 0:  # 切换到推荐页
            self.page.go("/")  # type: ignore