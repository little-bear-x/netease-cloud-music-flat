"""音乐播放页面"""

import flet as ft
import flet_audio as fa
import api
import requests
import base64


class PlayerPage(ft.View):
    """音乐播放页面"""

    def __init__(self, song_id: int, api: api.MusicApi):
        super().__init__()

        self.api = api
        self.song_id = song_id
        self.route = f"/player/{song_id}"
        self.adaptive = True
        self.can_pop = True
        self.scroll = ft.ScrollMode.AUTO
        self.padding = ft.padding.all(20)

        # 播放状态
        self.playing_state = True

        self.appbar = ft.AppBar(
            title=ft.Text(f"正在加载 {song_id}"),
        )

        self.load_song_data()
        self.load_view()

    def load_song_data(self) -> None:
        self.song_info = self.api.song_detail(self.song_id)
        self.song_url = self.api.songs_url(self.song_id)
        self.song_data = (
            requests.get(self.song_url.url).content if self.song_url else None
        )

    def load_view(self) -> None:
        """加载视图"""
        if not self.song_info or not self.song_url or not self.song_data:
            self.controls = [ft.Text("歌曲信息或URL加载失败", size=20, color="red")]
            return

        self.appbar = ft.AppBar(
            title=ft.Text(f"{self.song_info.name}", no_wrap=True),
            center_title=True,
        )

        self.audio_player = fa.Audio(
            src_base64=base64.b64encode(self.song_data).decode("utf-8"),
            autoplay=True,
        )

        # 进度条
        self.progress_bar = ft.Slider(
            value=0,
            min=0,
            max=100,
            on_change=self.seek_position,
            expand=True,
        )

        # 时间显示
        self.time_label = ft.Text("00:00 / 00:00", size=12)

        # 播放控制按钮
        self.playing_button = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            icon_size=40,
            icon_color=ft.Colors.WHITE,
            data="play",  # 用于跟踪按钮状态
            on_click=self.toggle_play,
        )

        control_buttons = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
                    icon_size=30,
                    icon_color=ft.Colors.WHITE,
                    on_click=self.previous_track,
                ),
                self.playing_button,
                ft.IconButton(
                    icon=ft.Icons.SKIP_NEXT_ROUNDED,
                    icon_size=30,
                    icon_color=ft.Colors.WHITE,
                    on_click=self.next_track,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # 构建主界面
        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        # 歌曲信息
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        self.song_info.name,
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Text(
                                        " / ".join(
                                            [
                                                artist.name
                                                for artist in self.song_info.artists
                                            ]
                                        ),
                                        size=16,
                                        color=ft.Colors.WHITE60,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            margin=ft.margin.only(bottom=30),
                        ),
                        # 封面图片
                        ft.Container(
                            content=ft.Image(
                                src=self.song_info.album.picUrl,
                                width=300,
                                height=300,
                                border_radius=ft.border_radius.all(10),
                                fit=ft.ImageFit.COVER,
                            ),
                            margin=ft.margin.only(bottom=40),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=10,
                                # color=ft.Colors.BLACK.with_opacity(0.5),
                            ),
                        ),
                        # 进度条和时间
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self.progress_bar,
                                    ft.Container(
                                        content=self.time_label,
                                        alignment=ft.alignment.center_right,
                                    ),
                                ],
                                spacing=0,
                            ),
                            margin=ft.margin.only(bottom=20),
                        ),
                        # 控制按钮
                        control_buttons,
                        # 歌曲
                        ft.Container(
                            content=self.audio_player,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
            )
        ]

        # 设置音频事件监听
        self.audio_player.on_position_changed = self.update_position
        self.audio_player.on_state_changed = self.update_state

    def format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_position(self, e):
        """更新进度条和时间显示"""
        position = int(e.data)
        duration = self.audio_player.get_duration()
        if duration > 0:
            # 更新进度条
            self.progress_bar.value = (position / duration) * 100
            # 更新时间显示
            self.time_label.value = (
                f"{self.format_time(position/1000)} / {self.format_time(duration/1000)}"
            )
            self.update()

    def seek_position(self, e):
        """跳转到指定位置"""
        if self.audio_player:
            duration = self.audio_player.get_duration()
            position = (float(e.control.value) * duration) / 100
            print(position)
            self.audio_player.seek(int(position))

    def update_state(self, e):
        """更新播放状态"""
        state = e.data
        print(state)

        if self.playing_button:
            if state == "playing":
                self.playing_button.icon = ft.Icons.PAUSE_ROUNDED
                self.playing_state = True
            else:
                self.playing_button.icon = ft.Icons.PLAY_ARROW_ROUNDED
                self.playing_state = False
            self.update()

    def toggle_play(self, e):
        """切换播放/暂停状态"""
        if self.playing_state:
            self.audio_player.pause()
        else:
            self.audio_player.resume()

    def previous_track(self, e):
        """播放上一首"""
        # TODO: 实现播放列表功能后完善
        print("Previous track")

    def next_track(self, e):
        """播放下一首"""
        # TODO: 实现播放列表功能后完善
        print("Next track")
