"""
NetEase Cloud Music API client.
"""

from .client import MusicApi
from .models import (
    Msg,
    SongUrl,
    Lyrics,
    SongInfo,
    SongList,
    AlbumInfo,
    AlbumDetail,
    AlbumDetailDynamic,
    PlayListDetail,
    PlayListDetailDynamic,
    TopList,
    Comment,
    ClientType,
    SingerInfo,
)

__all__ = [
    "MusicApi",
    "Msg",
    "SongUrl",
    "Lyrics",
    "SongInfo",
    "SongList",
    "AlbumInfo",
    "AlbumDetail",
    "AlbumDetailDynamic",
    "PlayListDetail",
    "PlayListDetailDynamic",
    "TopList",
    "Comment",
    "ClientType",
    "SingerInfo",
]
