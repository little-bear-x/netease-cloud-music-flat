"""音乐播放页面"""

import flet as ft
import models


class PlayerPage(ft.View):
    """音乐播放页面"""

    def __init__(self, globals_var: models.Globals):
        super().__init__()

        self.page = globals_var.page
        self.api = globals_var.music_api
        self.music_playing = globals_var.music_playing
        self.globals = globals_var
        self.route = f"/player"
        self.adaptive = True
        self.can_pop = True
        self.scroll = ft.ScrollMode.AUTO
        self.padding = ft.padding.all(20)

        self.appbar = ft.AppBar(
            title=ft.Text(f"正在加载"),
        )

        # 加载数据和视图
        self.load_view()

        # 注册回调
        self.music_playing.add_position_callback(self.update_position)
        self.music_playing.add_state_callback(self.update_state)


    def load_view(self) -> None:
        """加载视图"""
        self.globals.refresh_music_playing()

        self.appbar = ft.AppBar()

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
            icon=(
                ft.Icons.PLAY_ARROW_ROUNDED
                if not self.music_playing.playing_state
                else ft.Icons.PAUSE_ROUNDED
            ),
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
                                        self.music_playing.song_name,
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Text(
                                        " / ".join(
                                            [
                                                artist.name
                                                for artist in self.music_playing.artists
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
                                src=self.music_playing.song_pic,
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
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
            )
        ]


    def format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_position(self, position):
        """更新进度条和时间显示"""
        duration = self.music_playing.duration

        if duration > 0:  # type: ignore
            # 更新进度条
            self.progress_bar.value = (position / duration) * 100 \
                if (position / duration) * 100 <= self.progress_bar.max \
                else self.progress_bar.max   # type: ignore
            # 更新时间显示
            self.time_label.value = f"{self.format_time(position/1000)} / {self.format_time(duration/1000)}"
            self.update()

    def seek_position(self, e):
        """跳转到指定位置"""
        duration = self.music_playing.duration
        position = (float(e.control.value) * duration) / 100  # type: ignore
        print(position)
        self.music_playing.seek(int(position))

    def update_state(self, state):
        """更新播放状态"""
        if self.playing_button:
            if state:
                self.playing_button.icon = ft.Icons.PAUSE_ROUNDED
            else:
                self.playing_button.icon = ft.Icons.PLAY_ARROW_ROUNDED
            self.update()

    def toggle_play(self, e):
        """切换播放/暂停状态"""
        if self.music_playing.playing_state:
            self.music_playing.pause()
        else:
            self.music_playing.resume()

    def previous_track(self, e):
        """播放上一首"""
        if self.globals.music_playing_index > 0:
            self.globals.music_playing_index -= 1
            self.globals.refresh_music_playing()

    def next_track(self, e):
        """播放下一首"""
        if self.globals.music_playing_index < len(self.globals.music_playing_list) - 1:
            self.globals.music_playing_index += 1
            self.globals.refresh_music_playing()
