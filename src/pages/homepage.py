"""主页相关函数"""

import flet as ft
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
                        on_click=lambda e: self.page.go(    # type: ignore
                            "/search"),
                        expand=True,
                        style=ft.ButtonStyle(
                            bgcolor=ft.CupertinoColors.SYSTEM_BACKGROUND.with_opacity(
                                0.2, ft.CupertinoColors.PRIMARY
                            ),
                            alignment=ft.alignment.center_left,
                        ),
                    ),
                    ft.IconButton(
                        ft.Icons.MUSIC_NOTE_SHARP,
                        on_click=lambda e: self.page.open(    # type: ignore
                            MusicAlert(globals_var)),
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
            selected_index=0,  # 默认选中"推荐"标签
            on_change=self.nav_change,
            border=ft.Border(
                top=ft.BorderSide(
                    color=ft.CupertinoColors.SYSTEM_GREY2, width=0)
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
        self.page.go(f"/playlist/{songlist_id}")  # type: ignore

    def nav_change(self, e):
        """处理导航栏切换"""
        if e.control.selected_index == 1:  # 切换到我的页面
            self.page.go("/my")  # type: ignore


class MusicAlert(ft.AlertDialog):
    """音乐播放提示对话框"""

    def __init__(self, globals_var: models.Globals):
        super().__init__()
        self.page = globals_var.page
        self.music_playing = globals_var.music_playing
        self.globals = globals_var

        self.load_view()

        self.music_playing.add_position_callback(self.update_position)
        self.music_playing.add_state_callback(self.update_state)

    def load_view(self):
        """加载音乐播放提示对话框"""
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
        if not self.music_playing.song_id:
            self.title = ft.Text(
                self.music_playing.song_name or "正在播放的音乐将会显示在这里♥️"
            )
            self.actions = [
                ft.TextButton(
                    "关闭",
                    on_click=lambda e: self.page.close(self),  # type: ignore
                )
            ]
        else:
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
            self.content = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            self.music_playing.song_name,
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
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
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            self.actions = [
                ft.TextButton(
                    "歌曲详情",
                    on_click=lambda e: self.show_detail(),
                ),
                ft.TextButton(
                    "关闭",
                    on_click=lambda e: self.page.close(self),  # type: ignore
                ),
            ]
        self.open = True
        self.modal = True

    def show_detail(self):
        self.page.go(f"/player")  # type: ignore
        self.page.close(self)  # type: ignore

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
                else self.progress_bar.max  # type: ignore
            # 更新时间显示
            self.time_label.value = f"{self.format_time(position/1000)} / {self.format_time(duration/1000)}"
            self.update()

    def seek_position(self, e):
        """跳转到指定位置"""
        duration = self.music_playing.duration
        position = (float(e.control.value) * duration) / 100  # type: ignore
        models.debug(f"seek position: {position}")
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