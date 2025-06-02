"""
网易云音乐第三方客户端
"""

import flet as ft
import pages.homepage as homepage
import pages.search as search
import pages.playlist as playlist
import pages.player as player
import pages.my as my
import pages.login as login
import models


class App:
    """主应用程序类"""

    # 当前页的标题
    page_title = "主页"
    # 当前全部页面
    page_views = []

    def __init__(self, page: ft.Page):
        # 全局变量
        self.globals_var = models.Globals(page)

        self.globals_var.page.title = "网易云音乐"
        self.globals_var.page.on_route_change = self.route_change
        self.globals_var.page.on_view_pop = self.view_pop

        self.globals_var.page.go("/")

    def route_change(self, e):
        """处理路由变化"""
        self.globals_var.music_playing.position_callbacks = []
        self.globals_var.music_playing.state_callbacks = []
        models.info(f"前往路由: {self.globals_var.page.route}")
        # 根据当前路由添加相应视图
        self.troute = ft.TemplateRoute(self.globals_var.page.route)
        if self.troute.match("/"):
            self.globals_var.page.views.append(
                homepage.Homepage(self.globals_var))
        elif self.troute.match("/login"):
            self.globals_var.page.views.append(
                login.LoginPage(self.globals_var))
        elif self.troute.match("/my"):
            self.globals_var.page.views.append(
                my.MyPage(self.globals_var))
        elif self.troute.match("/search"):
            self.globals_var.page.views.append(
                search.SearchPage(self.globals_var))
        elif self.troute.match("/search/:value"):
            self.globals_var.page.views.append(search.SearchPage(
                self.globals_var, self.troute.value))  # type: ignore
        elif self.troute.match("/search_result/:query"):
            self.globals_var.page.views.append(search.SearchResultPage(
                self.troute.query, self.globals_var))  # type: ignore
        elif self.troute.match("/playlist/:id"):
            playlist_id = int(self.troute.id)  # type: ignore
            self.globals_var.page.views.append(
                playlist.PlaylistPage(playlist_id, self.globals_var))
        elif self.troute.match("/player"):
            self.globals_var.page.views.append(
                player.PlayerPage(self.globals_var))
        elif self.troute.match("/reload"):
            self.globals_var.page.go(self.globals_var.page.views[-1].route)  # type: ignore
        else:
            # 处理未知路由，重定向到首页
            models.warning("Unknown route, redirecting to home")
            self.globals_var.page.go("/")

        # 删除最后一项重复route
        if self.globals_var.page.views[-2].route and self.globals_var.page.route == self.globals_var.page.views[-2].route:
            models.info(f"Removing duplicate route: {self.globals_var.page.route}")
            del self.globals_var.page.views[-2]

        self.globals_var.page.update()

    def view_pop(self, e):
        """处理视图弹出事件"""
        self.globals_var.page.views.pop()
        top_view = self.globals_var.page.views[-1]
        self.globals_var.page.go(top_view.route)  # type: ignore
        self.globals_var.music_playing.position_callbacks = []
        self.globals_var.music_playing.state_callbacks = []


ft.app(App)