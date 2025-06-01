import flet as ft
import api
from flet import OptionalEventCallable
import flet_audio as fa
import requests
import base64


class MusicPlaying:
    """全局音乐播放控制器"""

    def __init__(self):
        self.song_id: int | None = None
        self.song_name: str | None = None
        self.song_pic: str | None = None
        self.playing_state: bool = False
        self.duration: int | None = None
        self.current_time: int = 0
        self.artists: list[api.SingerInfo] = []

        # 创建音频播放器
        self.audio_player = fa.Audio(
            volume=1,
            on_loaded=self.on_audio_loaded,
            on_position_changed=self.update_position,
            on_state_changed=self.update_state,
        )

        # 注册回调函数列表
        self.position_callbacks: list[OptionalEventCallable] = []
        self.state_callbacks: list[OptionalEventCallable] = []

    def on_audio_loaded(self, e):
        """音频加载完成时的回调并开始播放"""
        print(f"Audio loaded: {self.song_name}")
        self.duration = self.audio_player.get_duration()
        self.play()

    def add_position_callback(self, callback: OptionalEventCallable):
        """添加位置更新回调函数"""
        if callback not in self.position_callbacks:
            self.position_callbacks.append(callback)

    def remove_position_callback(self, callback: OptionalEventCallable):
        """移除位置更新回调函数"""
        if callback in self.position_callbacks:
            self.position_callbacks.remove(callback)

    def add_state_callback(self, callback: OptionalEventCallable):
        """添加状态更新回调函数"""
        if callback not in self.state_callbacks:
            self.state_callbacks.append(callback)

    def remove_state_callback(self, callback: OptionalEventCallable):
        """移除状态更新回调函数"""
        if callback in self.state_callbacks:
            self.state_callbacks.remove(callback)

    def update_position(self, e):
        """更新播放位置"""
        self.current_time = int(e.data)
        # 通知所有注册的回调
        for callback in self.position_callbacks:
            if callback is None:
                continue
            callback(self.current_time)

    def update_state(self, e):
        """更新播放状态"""
        state = e.data
        self.playing_state = state == "playing"
        # 通知所有注册的回调
        for callback in self.state_callbacks:
            if callback is None:
                continue
            callback(self.playing_state)

    def set_song(
        self,
        song_id: int,
        song_name: str,
        song_src: str,
        song_pic: str,
        song_artists: list[api.SingerInfo],
    ):
        """设置当前播放的歌曲信息"""
        print(f"Setting song: {song_name} (ID: {song_id})")
        self.audio_player.release()  # 释放之前的音频资源
        self.song_id = song_id
        self.song_name = song_name
        self.song_pic = song_pic
        self.audio_player.src_base64 = song_src
        self.artists = song_artists

    def play(self):
        """播放音乐"""
        if self.song_id is not None:
            self.audio_player.play()

    def pause(self):
        """暂停音乐"""
        if self.song_id is not None:
            self.audio_player.pause()

    def resume(self):
        """恢复播放"""
        if self.song_id is not None:
            self.audio_player.resume()

    def seek(self, position: int):
        """跳转到指定位置"""
        if self.song_id is not None:
            self.audio_player.seek(position)

    def dispose(self):
        """清理资源"""
        self.audio_player.release()
        self.position_callbacks.clear()
        self.state_callbacks.clear()


class Globals:
    """全局变量"""

    music_api: api.MusicApi
    music_playing: MusicPlaying
    music_playing_list: list[api.SongInfo] = []  # 播放列表
    music_playing_index: int = 0  # 当前播放列表索引
    music_playing_mode: str = "list"  # 播放模式，默认为列表循环

    page: ft.Page

    def __init__(self, p: ft.Page):
        self.music_api = api.MusicApi()
        self.page = p
        self.music_playing = MusicPlaying()
        self.page.add(self.music_playing.audio_player)

    def refresh_music_playing(self):
        """刷新当前播放的歌曲"""
        if self.music_playing_list[self.music_playing_index].id == self.music_playing.song_id:
            return
        song_info = self.music_api.song_detail(
            self.music_playing_list[self.music_playing_index].id
        )
        song_url = self.music_api.songs_url(self.music_playing_list[self.music_playing_index].id)
        print(song_url)
        song_data = (
            requests.get(song_url.url).content if song_url else None
        )
        if not song_data:
            return
        self.music_playing.set_song(
            self.music_playing_list[self.music_playing_index].id,
            self.music_playing_list[self.music_playing_index].name,
            base64.b64encode(song_data).decode("utf-8"),
            song_info.album.picUrl if song_info.album.picUrl else "",
            song_info.artists
        )
