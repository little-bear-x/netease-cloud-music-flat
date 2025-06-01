"""
网易云音乐第三方客户端
"""

import flet as ft
import pages.homepage as homepage
import pages.search as search
import pages.playlist as playlist
import pages.player as player
import api
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

        # 将 audio_player 组件添加到页面中
        self.globals_var.page.add(self.globals_var.music_playing.audio_player)

        self.globals_var.page.go("/")

    def route_change(self, e):
        """处理路由变化"""
        self.globals_var.music_playing.position_callbacks = []
        self.globals_var.music_playing.state_callbacks = []
        # 删除最后一项重复route
        if self.globals_var.page.route == self.globals_var.page.views[-1].route:
            print(f"Removing duplicate route: {self.globals_var.page.route}")
            self.globals_var.page.views.pop()
        # 根据当前路由添加相应视图
        self.troute = ft.TemplateRoute(self.globals_var.page.route)
        if self.troute.match("/"):
            self.globals_var.page.views.append(homepage.Homepage(self.globals_var))
        elif self.troute.match("/search"):
            self.globals_var.page.views.append(search.SearchPage(self.globals_var))
        elif self.troute.match("/search/:value"):
            print(f"Search value: {self.troute.value}") # type: ignore
            self.globals_var.page.views.append(search.SearchPage(self.globals_var, self.troute.value)) # type: ignore
        elif self.troute.match("/search_result/:query"):
            print(f"Search query: {self.troute.query}") # type: ignore
            self.globals_var.page.views.append(search.SearchResultPage(self.troute.query, self.globals_var)) # type: ignore
        elif self.troute.match("/playlist/:id"):
            playlist_id = int(self.troute.id) # type: ignore
            print(f"Loading playlist with ID: {playlist_id}")
            self.globals_var.page.views.append(playlist.PlaylistPage(playlist_id, self.globals_var))
        elif self.troute.match("/player"):
            self.globals_var.page.views.append(player.PlayerPage(self.globals_var))
        elif self.troute.match("/player/reload"):
            self.globals_var.page.go("/player")
        else:
            # 处理未知路由，重定向到首页
            print("Unknown route, redirecting to home")
            self.globals_var.page.go("/")

        self.globals_var.page.update()

    def view_pop(self, e):
        """处理视图弹出事件"""
        self.globals_var.page.views.pop()
        top_view = self.globals_var.page.views[-1]
        self.globals_var.page.go(top_view.route) # type: ignore
        self.globals_var.music_playing.position_callbacks = []
        self.globals_var.music_playing.state_callbacks = []

ft.app(App)
