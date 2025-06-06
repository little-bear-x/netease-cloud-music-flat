import flet as ft
from api import MusicApi
import models


class SearchPage(ft.View):
    """搜索页面"""

    def __init__(self, globals_var: models.Globals, default_query: str = ""):
        super().__init__()

        self.route = f"/search/{default_query}"
        self.adaptive = True
        self.padding = ft.padding.all(20)
        self.can_pop = True
        self.page = globals_var.page

        self.search_field = ft.TextField(
            hint_text="搜索",
            expand=True,
            autofocus=True,
            border_width=1,
            border=ft.InputBorder.UNDERLINE,
            value=default_query,
        )
        self.load_view()

    def load_view(self) -> None:
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

    def __init__(self, search_query: str, globals_var: models.Globals):
        super().__init__()

        self.api = globals_var.music_api
        self.page = globals_var.page
        self.globals = globals_var
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
                            alignment=ft.alignment.center_left,
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
        self.load_view()

    def load_view(self):
        """加载搜索结果"""
        if not self.api:
            self.controls = [ft.Text("API未初始化", size=20, color="red")]
            return

        try:
            # 获取搜索结果
            self.songs = self.api.search_song(self.search_query)

            # 如果没有结果
            if not self.songs:
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
                        on_click=lambda e, song=song, index=index: self.play_music(index),
                    )
                    for (index, song) in enumerate(self.songs)
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
    
    def play_music(self, playlist_index: int):
        """播放歌曲"""
        self.globals.music_playing_list = self.songs
        self.globals.music_playing_index = playlist_index
        self.page.go(f"/player")  # type: ignore
