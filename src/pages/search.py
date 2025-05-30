import flet as ft
from api import MusicApi


class SearchPage(ft.View):
    """搜索页面"""

    def __init__(self, default_query: str = ""):
        super().__init__()

        self.route = f"/search/{default_query}"
        self.adaptive = True
        self.padding = ft.padding.all(20)
        self.can_pop = True

        self.search_field = ft.TextField(
            hint_text="搜索",
            expand=True,
            autofocus=True,
            border_width=1,
            border=ft.InputBorder.UNDERLINE,
            value=default_query,
        )

        self.appbar = ft.AppBar(
            title=ft.Row(
                [
                    self.search_field,
                    ft.IconButton(
                        icon=ft.Icons.SEARCH,
                        on_click=self.submit_search,  # type: ignore
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        )

    def submit_search(self, e):
        if self.search_field.value == "":
            return
        self.page.go(f"/search_result/{self.search_field.value}")  # type: ignore


class SearchResultPage(ft.View):
    """搜索结果展示页面"""

    def __init__(self, search_query: str, api: MusicApi):
        super().__init__()

        self.api = api
        self.search_query = search_query
        self.route = f"/search_result/{search_query}"
        self.adaptive = True
        self.padding = ft.padding.all(20)
        self.can_pop = True

        self.appbar = ft.AppBar(
            title=ft.Row(
                [
                    ft.TextButton(
                        text=f"{search_query}",
                        icon=ft.Icons.SEARCH,
                        on_click=lambda e: self.page.go(f"/search/{search_query}"),  # type: ignore
                        expand=True,
                        style=ft.ButtonStyle(
                            bgcolor=ft.CupertinoColors.SYSTEM_BACKGROUND.with_opacity(
                                0.2, ft.CupertinoColors.PRIMARY
                            ),
                        ),
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        )

        # Initialize controls with loading indicator
        self.controls = [
            ft.Text("搜索中...", size=20),
        ]

        # Load search results
        self.load_search_results()

    def load_search_results(self):
        """加载搜索结果"""
        if not self.api:
            self.controls = [ft.Text("API未初始化", size=20, color="red")]
            return

        try:
            # 获取搜索结果
            songs = self.api.search_song(self.search_query)

            # 如果没有结果
            if not songs:
                self.controls = [ft.Text("没有找到相关歌曲", size=20)]
                return

            # 创建搜索结果列表
            results_list = ft.ListView(
                expand=1,
                spacing=10,
                padding=10,
                controls=[
                    ft.ListTile(
                        title=ft.Text(song.name),
                        subtitle=ft.Text(
                            " / ".join([artist.name for artist in song.artists]),
                            size=12,
                            color=ft.Colors.BLACK54,
                        ),
                        trailing=ft.Icon(ft.Icons.PLAY_ARROW),
                        # TODO: 添加点击播放功能
                        # on_click=lambda e, s=song: self.play_song(s),
                    )
                    for song in songs
                ],
            )

            # 更新页面内容
            self.controls = [
                ft.Column(
                    controls=[
                        ft.Divider(height=1),
                        results_list,
                    ],
                    expand=True,
                )
            ]

        except Exception as e:
            self.controls = [ft.Text(f"搜索失败: {str(e)}", size=20, color="red")]
