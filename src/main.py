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
        self.page.views.clear()  # 清除所有视图

        # 根据当前路由添加相应视图
        if self.page.route == "/":
            self.page_views.append("/")
            self.page.views.append(homepage.Homepage(self.api))
        elif self.page.route == "/search":
            self.page_views.append("/search")
            self.page.views.append(search.SearchPage())
        else:
            # 处理未知路由，重定向到首页
            self.page.go("/")

        self.page.update()

    def view_pop(self, e):
        """处理视图弹出(如浏览器后退按钮)"""
        self.page_views.pop()  # 移除当前视图
        top_view = self.page_views[-1]  # 获取上一个视图
        self.page.go(top_view)  # 导航到上一个视图的路由


ft.app(App)
