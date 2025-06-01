
import threading
import queue
import time
import flet_audio as fa
from typing import Optional, Callable
from dataclasses import dataclass, field

@dataclass
class MusicCommand:
    """音乐播放命令"""
    action: str  # play, pause, resume, seek, set_song
    data: dict = field(default_factory=dict)  # 命令相关的数据

class MusicPlayerThread(threading.Thread):
    """音乐播放线程"""
    
    def __init__(self, page=None):
        super().__init__(daemon=True)
        self.page = page
        self._command_queue = queue.Queue()
        self._running = True
        self._position_callbacks = []
        self._state_callbacks = []
        
        # 播放器状态
        self._current_song_id = None
        self._playing_state = False
        self._current_position = 0
        self._duration = 0
        
        # 创建音频播放器
        self._audio_player = fa.Audio(
            volume=1,
            on_loaded=self._on_audio_loaded,
            on_position_changed=self._update_position,
            on_state_changed=self._update_state,
        )
        
        # 如果提供了页面实例，将播放器添加到页面
        if page:
            page.add(self._audio_player)
    
    def run(self):
        """线程主循环"""
        while self._running:
            try:
                cmd = self._command_queue.get(timeout=0.1)
                self._handle_command(cmd)
            except queue.Empty:
                continue
    
    def _handle_command(self, cmd: MusicCommand):
        """处理播放命令"""
        if cmd.action == "play":
            self._audio_player.play()
        elif cmd.action == "pause":
            self._audio_player.pause()
        elif cmd.action == "resume":
            self._audio_player.resume()
        elif cmd.action == "seek":
            self._audio_player.seek(cmd.data["position"])
        elif cmd.action == "set_song":
            self._set_song(cmd.data)
        elif cmd.action == "stop":
            self._running = False
            self._audio_player.release()
    
    def _set_song(self, song_data: dict):
        """设置当前播放的歌曲"""
        self._audio_player.release()
        self._current_song_id = song_data["id"]
        self._audio_player.src_base64 = song_data["src"]
        self.page.go("/reload")  # type:ignore  # 刷新页面以更新播放器状态
    
    def _on_audio_loaded(self, e):
        """音频加载完成回调"""
        self._duration = self._audio_player.get_duration()
        self._audio_player.play()
    
    def _update_position(self, e):
        """更新播放位置"""
        self._current_position = int(e.data)
        for callback in self._position_callbacks:
            callback(self._current_position)
    
    def _update_state(self, e):
        """更新播放状态"""
        self._playing_state = e.data == "playing"
        for callback in self._state_callbacks:
            callback(self._playing_state)
    
    # 公共接口
    def play(self):
        """播放音乐"""
        self._command_queue.put(MusicCommand("play"))
    
    def pause(self):
        """暂停音乐"""
        self._command_queue.put(MusicCommand("pause"))
    
    def resume(self):
        """恢复播放"""
        self._command_queue.put(MusicCommand("resume"))
    
    def seek(self, position: int):
        """跳转到指定位置"""
        self._command_queue.put(MusicCommand("seek", {"position": position}))
    
    def set_song(self, song_data: dict):
        """设置要播放的歌曲"""
        self._command_queue.put(MusicCommand("set_song", song_data))
    
    def stop(self):
        """停止播放线程"""
        self._command_queue.put(MusicCommand("stop"))
        self.join()
    
    def add_position_callback(self, callback: Callable):
        """添加位置更新回调"""
        if callback not in self._position_callbacks:
            self._position_callbacks.append(callback)
    
    def remove_position_callback(self, callback: Callable):
        """移除位置更新回调"""
        if callback in self._position_callbacks:
            self._position_callbacks.remove(callback)
    
    def add_state_callback(self, callback: Callable):
        """添加状态更新回调"""
        if callback not in self._state_callbacks:
            self._state_callbacks.append(callback)
    
    def remove_state_callback(self, callback: Callable):
        """移除状态更新回调"""
        if callback in self._state_callbacks:
            self._state_callbacks.remove(callback)
    
    @property
    def current_song_id(self) -> Optional[int]:
        return self._current_song_id
    
    @property
    def playing_state(self) -> bool:
        return self._playing_state
    
    @property
    def current_position(self) -> int:
        return self._current_position
    
    @property
    def duration(self) -> int:
        return self._duration