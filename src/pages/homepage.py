"""主页相关函数"""

import flet as ft
import api
import models


class Homepage(ft.View):
    """主页"""

    def __init__(self, globals_var: models.Globals):
        """
        初始化主页
        :param api: 网易云API实例
        """
        super().__init__()

        self.api = globals_var.music_api
        self.page = globals_var.page
        self.route = "/"
        self.adaptive = True
        self.padding = ft.padding.all(20)
        self.scroll = ft.ScrollMode.AUTO
        self.can_pop = False

        # 搜索栏
        self.appbar = ft.AppBar(
            automatically_imply_leading=False,  # 禁用自动显示返回按钮
            title=ft.Row(
                controls=[
                    ft.TextButton(
                        text="搜索",
                        icon=ft.Icons.SEARCH,
                        on_click=lambda e: self.page.go("/search"),  # type: ignore
                        expand=True,
                        style=ft.ButtonStyle(
                            bgcolor=ft.CupertinoColors.SYSTEM_BACKGROUND.with_opacity(
                                0.2, ft.CupertinoColors.PRIMARY
                            ),
                            alignment=ft.alignment.center_left,
                        ),
                    ),
                    ft.IconButton(
                        ft.CupertinoIcons.ADD,
                    ),
                ]
            ),
        )

        # 主要内容区域
        self.controls = [
            ft.Column(
                controls=[
                    ft.Text("加载中...", size=20),
                ],
                spacing=20,
            )
        ]

        # 底部导航栏
        self.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="推荐"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="我的"),
            ],
            border=ft.Border(
                top=ft.BorderSide(color=ft.CupertinoColors.SYSTEM_GREY2, width=0)
            ),
        )

        self.load_view()

    def load_view(self):
        """加载主页内容"""
        # 获取推荐歌单
        top_song_list = self.api.top_song_list()

        # 创建内容列表
        content = []

        # 添加推荐歌单
        if top_song_list:
            content.extend(
                [
                    ft.Text("火热歌单", size=24, weight=ft.FontWeight.BOLD),
                    ft.GridView(
                        expand=True,
                        runs_count=2,
                        max_extent=200,
                        spacing=90,
                        run_spacing=20,
                        controls=[
                            ft.TextButton(
                                content=ft.Column(
                                    controls=[
                                        ft.Image(
                                            src=playlist.coverImgUrl,
                                            width=180,
                                            height=180,
                                            fit=ft.ImageFit.COVER,
                                            border_radius=10,
                                        ),
                                        ft.Text(
                                            playlist.name,
                                            no_wrap=False,
                                            max_lines=2,
                                        ),
                                    ],
                                ),
                                expand=True,
                                on_click=lambda e, playlist=playlist: self.to_songlist(
                                    playlist.id
                                ),
                            )
                            for playlist in (
                                top_song_list
                                if len(top_song_list) <= 8
                                else top_song_list[:8]
                            )
                        ],
                    ),
                ]
            )

        # 更新主内容区域
        self.controls = [
            ft.Column(
                controls=content if content else [ft.Text("暂无内容")],
                spacing=20,
            )
        ]

    def to_songlist(self, songlist_id: int):
        """跳转到歌单页面"""
        # print(f"跳转到歌单页面: {songlist_id}")
        # print(self.api.playlist_detail(songlist_id))  # 调试输出
        print(f"跳转到歌单页面: {songlist_id}")
        self.page.go(f"/playlist/{songlist_id}")  # type: ignore
