import flet as ft
from api import MusicApi
import models


class PlaylistPage(ft.View):
    def __init__(self, playlist_id: int, globals_var: models.Globals):
        super().__init__()

        self.route = f"/playlist/{playlist_id}"
        self.playlist_id = playlist_id
        self.api = globals_var.music_api
        self.page = globals_var.page

        self.adaptive = True
        self.padding = ft.padding.all(20)
        self.can_pop = True

        self.appbar = ft.AppBar(
            title=ft.Text(f"正在加载 {playlist_id}"),
        )

        self.load_view()

    def load_view(self) -> None:
        """加载歌单"""
        playlist = self.api.playlist_detail(self.playlist_id)
        self.appbar = ft.AppBar(
            title=ft.Text(f"{playlist.name}", no_wrap=True),
        )

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
                    on_click=lambda e, song=song: self.page.go(f"/player/{song.id}"),  # type: ignore
                )
                for song in playlist.tracks
            ],
        )
        self.controls = [
            ft.Column(
                controls=[
                    ft.Divider(height=1),
                    results_list,
                ],
                expand=True,
            )
        ]
