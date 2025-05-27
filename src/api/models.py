"""
Data models for NetEase Cloud Music API responses.
Matches the Rust implementation's model types.
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Msg:
    """Generic message response."""
    code: int
    msg: str

@dataclass
class LoginInfo:
    """Login information response."""
    code: int
    account: Dict[str, Any]
    profile: Optional[Dict[str, Any]] = None

@dataclass
class SingerInfo:
    """Singer/Artist information."""
    id: int
    name: str
    picUrl: Optional[str] = None
    alias: List[str] = field(default_factory=list)

@dataclass
class BannersInfo:
    """Banner information."""
    pic: str
    targetId: int
    targetType: int
    titleColor: str
    typeTitle: str
    url: Optional[str] = None

@dataclass
class SongUrl:
    """Song URL information."""
    id: int
    url: str
    br: int  # bitrate
    size: int
    md5: str
    type: str
    
@dataclass
class Lyrics:
    """Song lyrics."""
    lrc: Optional[str] = None
    tlyric: Optional[str] = None

@dataclass
class AlbumInfo:
    """Album information."""
    id: int
    name: str
    picUrl: str
    description: Optional[str] = None
    publishTime: Optional[int] = None  # timestamp in milliseconds
    artists: List[SingerInfo] = field(default_factory=list)

@dataclass
class SongInfo:
    """Song information."""
    id: int
    name: str
    album: 'AlbumInfo'
    duration: int  # in milliseconds
    source: Optional[str] = None
    url: Optional[str] = None
    pic_url: Optional[str] = None
    lyric: Optional[str] = None
    artists: List[SingerInfo] = field(default_factory=list)

@dataclass
class SongList:
    """Song list / playlist information."""
    id: int
    name: str
    description: Optional[str]
    coverImgUrl: str
    playCount: int = 0
    trackCount: int = 0
    songs: Optional[List[SongInfo]] = None
    creator: Dict[str, Any] = field(default_factory=dict)  # User info

@dataclass
class AlbumDetail:
    """Detailed album information."""
    album: AlbumInfo
    songs: List[SongInfo] = field(default_factory=list)

@dataclass
class AlbumDetailDynamic:
    """Dynamic album information."""
    onSale: bool
    subCount: int
    liked: bool
    commentCount: int
    shareCount: int

@dataclass
class PlayListDetail:
    """Detailed playlist information."""
    id: int
    name: str
    coverImgUrl: str
    createTime: int
    updateTime: int
    description: str
    tags: List[str] = field(default_factory=list)
    creator: Dict[str, Any] = field(default_factory=dict)  # User info
    tracks: List[SongInfo] = field(default_factory=list)

@dataclass
class PlayListDetailDynamic:
    """Dynamic playlist information."""
    subscribed: bool
    shareCount: int
    commentCount: int
    playCount: int

@dataclass
class TopList:
    """Toplist information."""
    id: int
    name: str
    description: str
    coverImgUrl: str
    updateFrequency: str
    tracks: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class Comment:
    """Comment information."""
    commentId: int
    content: str
    time: int  # timestamp in milliseconds
    likedCount: int
    replyCount: int = 0
    isHot: bool = False
    beReplied: Optional[List[Dict[str, Any]]] = None
    user: Dict[str, Any] = field(default_factory=dict)  # User info

@dataclass
class ClientType:
    """Client type information."""
    clientType: str = "pc"  # pc, android, iphone etc.
