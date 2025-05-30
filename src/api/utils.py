"""
Utility functions for NetEase Cloud Music API.
Matches the functionality from the Rust implementation.
"""

import json
import random
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode
from .constants import USER_AGENT_LIST, LINUX_USER_AGENT
from .models import (
    LoginInfo,
    Msg,
    SongInfo,
    SingerInfo,
    AlbumInfo,
    BannersInfo,
    PlayListDetail,
    AlbumDetail,
    SongList,
)


def choose_user_agent(ua_type: Optional[str] = None) -> str:
    """Choose a user agent string based on type.

    Args:
        ua_type: Type of user agent ('linux' or None for random)
    Returns:
        User agent string
    """
    if ua_type == "linux":
        return LINUX_USER_AGENT
    return random.choice(USER_AGENT_LIST)


def to_login_info(json_str: str) -> LoginInfo:
    """Convert JSON response to LoginInfo object.

    Args:
        json_str: Raw JSON response string
    Returns:
        LoginInfo object
    """
    data = json.loads(json_str)
    return LoginInfo(
        code=data.get("code", -1),
        account=data.get("account", {}),
        profile=data.get("profile"),
    )


def to_msg(json_str: str) -> Msg:
    """Convert JSON response to Msg object.

    Args:
        json_str: Raw JSON response string
    Returns:
        Msg object
    """
    data = json.loads(json_str)
    return Msg(code=data.get("code", -1), msg=data.get("msg", ""))


def to_song_id_list(json_str: str) -> List[int]:
    """Convert JSON response to song ID list.

    Args:
        json_str: Raw JSON response string
    Returns:
        List of song IDs
    """
    try:
        data = json.loads(json_str)
        if data.get("code") == 200:
            return data.get("ids", [])
        return []
    except:
        return []


def to_songinfo(json_str: str) -> SongInfo:
    """Convert JSON response to SongInfo objects.

    Args:
        json_str: Raw JSON response string
    Returns:
        SongInfo objects
    """
    song = json.loads(json_str)
    return SongInfo(
        id=song.get("id", 0),
        name=song.get("name", ""),
        album=AlbumInfo(
            id=song.get("album", {}).get("id", 0),
            name=song.get("album", {}).get("name", ""),
            picUrl=song.get("album", {}).get("picUrl", ""),
        ),
        duration=song.get("duration", 0),
        pic_url=song.get("album", {}).get("picUrl", ""),
        artists=[
            SingerInfo(
                id=artist.get("id", 0),
                name=artist.get("name", ""),
                picUrl=artist.get("picUrl", ""),
            )
            for artist in song.get("artists", [])
        ],
    )


def to_playlist(json_str: str) -> SongList:
    """Convert JSON response to SongList objects.

    Args:
        json_str: Raw JSON response string
    Returns:
        SongList objects
    """
    playlist = json.loads(json_str)
    return SongList(
        id=playlist.get("id", 0),
        name=playlist.get("name", ""),
        description=playlist.get("description", ""),
        creator=playlist.get("creator", {}),
        coverImgUrl=playlist.get("coverImgUrl", ""),
        playCount=playlist.get("playCount", 0),
        trackCount=playlist.get("trackCount", 0),
        songs=[],  # Empty list since we don't have track details yet
    )


def build_linux_api_data(url: str, params: Dict[str, Any]) -> str:
    """Build data for Linux API request.

    Args:
        url: API endpoint URL
        params: Request parameters
    Returns:
        JSON formatted string
    """
    return json.dumps(
        {"method": "linuxapi", "url": url.replace("weapi", "api"), "params": params}
    )


def build_url(base_url: str, path: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Build complete URL with parameters.

    Args:
        base_url: Base URL
        path: API endpoint path
        params: Optional URL parameters
    Returns:
        Complete URL string
    """
    url = f"{base_url}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    return url


def to_play_list_detail(data: Dict[str, Any]) -> PlayListDetail:
    """Convert JSON data to PlayListDetail object."""
    return PlayListDetail(
        id=data.get("id", 0),
        name=data.get("name", ""),
        coverImgUrl=data.get("coverImgUrl", ""),
        createTime=data.get("createTime", 0),
        updateTime=data.get("updateTime", 0),
        description=data.get("description", ""),
        tags=data.get("tags", []),
        creator=data.get("creator", {}),
        tracks=[to_songinfo(json.dumps(song)) for song in data.get("tracks", [])],
    )


def to_album_detail(data: Dict[str, Any]) -> AlbumDetail:
    """Convert JSON data to AlbumDetail object."""
    album_data = data.get("album", {})
    artists = album_data.get("artists", [])

    album = AlbumInfo(
        id=album_data.get("id", 0),
        name=album_data.get("name", ""),
        picUrl=album_data.get("picUrl", ""),
        artists=[
            SingerInfo(
                id=artist.get("id", 0),
                name=artist.get("name", ""),
                picUrl=artist.get("picUrl", ""),
            )
            for artist in artists
        ],
        description=album_data.get("description"),
        publishTime=album_data.get("publishTime"),
    )

    songs = to_song_info(json.dumps(data), "album")

    return AlbumDetail(album=album, songs=songs)


def to_banners_info(json_str: str) -> List[BannersInfo]:
    """Convert JSON response to list of BannersInfo objects."""
    data = json.loads(json_str)
    banners = []
    for item in data.get("banners", []):
        banner = BannersInfo(
            pic=item.get("imageUrl", ""),
            targetId=item.get("targetId", 0),
            targetType=item.get("targetType", 0),
            titleColor=item.get("titleColor", ""),
            typeTitle=item.get("typeTitle", ""),
            url=item.get("url"),
        )
        banners.append(banner)
    return banners


def to_song_list_from_songs(
    songs: List[SongInfo], playlist_info: Optional[Dict[str, Any]] = None
) -> List[SongList]:
    """Convert a list of SongInfo objects to SongList objects.

    Args:
        songs: List of SongInfo objects
        playlist_info: Optional playlist metadata

    Returns:
        List of SongList objects
    """
    if not playlist_info:
        playlist_info = {}

    return [
        SongList(
            id=playlist_info.get("id", 0),
            name=playlist_info.get("name", ""),
            description=playlist_info.get("description", ""),
            creator=playlist_info.get("creator", {}),
            coverImgUrl=playlist_info.get("coverImgUrl", ""),
            playCount=playlist_info.get("playCount", 0),
            trackCount=playlist_info.get("trackCount", len(songs)),
            songs=songs,
        )
    ]
