"""
网易云音乐第三方客户端
"""

import flet as ft
import pages.homepage as homepage
import pages.search as search
import api


class App:
    """主应用程序类"""

    # 当前页的标题
    page_title = "主页"
    # 当前全部页面
    page_views = []
    # 网易云api
    api = api.MusicApi()

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "网易云音乐"
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.go("/")

    def route_change(self, e):
        """处理路由变化"""
        # 根据当前路由添加相应视图
        self.troute = ft.TemplateRoute(self.page.route)
        if self.troute.match("/"):
            self.page.views.clear()
            self.page.views.append(homepage.Homepage(self.api))
        elif self.troute.match("/search"):
            self.page.views.append(search.SearchPage())
        elif self.troute.match("/search/:value"):
            print(f"Search value: {self.troute.value}")
            self.page.views.append(search.SearchPage(self.troute.value))
        elif self.troute.match("/search_result/:query"):
            print(f"Search query: {self.troute.query}")
            self.page.views.append(search.SearchResultPage(self.troute.query, api=self.api))
        else:
            # 处理未知路由，重定向到首页
            print("Unknown route, redirecting to home")
            self.page.go("/")

        self.page.update()

    def view_pop(self, e):
        """处理视图弹出事件"""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)


ft.app(App)
