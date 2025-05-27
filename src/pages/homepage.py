"""主页相关函数"""

import flet as ft
import api


class Homepage(ft.View):
    """主页"""

    def __init__(self, api: api.MusicApi):
        """
        初始化主页
        :param api: 网易云API实例
        """
        super().__init__()

        self.api = api  # 保存API实例
        self.route = "/"
        self.adaptive = True
        self.padding = ft.padding.all(20)
        self.scroll = ft.ScrollMode.AUTO

        # 搜索栏
        self.appbar = ft.AppBar(
            title=ft.Row(
                controls=[
                    ft.TextButton(
                        text="搜索",
                        icon=ft.Icons.SEARCH,
                        on_click=lambda e: self.page.go("/search"),  # type: ignore
                        expand=True,
                    ),
                    ft.IconButton(
                        ft.CupertinoIcons.ADD,
                    ),
                ]
            ),
            bgcolor=ft.Colors.with_opacity(0.04, ft.CupertinoColors.SYSTEM_BACKGROUND),
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

        # print(self.api.search_song("反乌托邦"))  # 打印登录状态
        # 加载内容
        self.load_content()

    def load_content(self):
        """加载主页内容"""
        # try:
        # 获取推荐歌单
        top_song_list = self.api.top_song_list()
        print("\n\n\n\n")
        print(top_song_list)

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
                            ft.Container(
                                width=180,
                                height=250,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Image(
                                            src=playlist.coverImgUrl,
                                            width=180,
                                            height=180,
                                            fit=ft.ImageFit.COVER,
                                            border_radius=10,
                                        ),
                                        ft.Text(playlist.name),
                                    ],
                                ),
                            )
                            for playlist in (top_song_list if len(top_song_list) <= 10 else top_song_list[:10])
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

        # except Exception as e:
        #     print(f"Error loading content: {e}")
        #     self.controls = [
        #         ft.Column(
        #             controls=[
        #                 ft.Text(f"加载失败: {str(e)}", color="red"),
        #                 ft.TextButton("重试", on_click=lambda _: self.load_content()),
        #             ],
        #         )
        #     ]
