"""
Core API client for NetEase Cloud Music.
This is a Python implementation of the Rust netease-cloud-music-api library.
"""

import re
import json
import os
import random
import string
from enum import Enum
from typing import Optional, Dict, Any, List, Union, Tuple
import httpx

from .constants import BASE_URL, TIMEOUT, USER_AGENT_LIST, LINUX_USER_AGENT
from .encrypt import Crypto
from .models import (
    Msg,
    LoginInfo,
    SingerInfo,
    BannersInfo,
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
)
from .utils import (
    choose_user_agent,
    build_url,
    build_linux_api_data,
    to_login_info,
    to_msg,
    to_song_id_list,
    to_songinfo,
    to_playlist,
    to_play_list_detail,
    to_album_detail,
    to_banners_info,
    to_song_list_from_songs,
)


def create_random_string(length: int) -> str:
    """Create a random string of specified length."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class CryptoApi(Enum):
    """Encryption methods for different API endpoints."""

    WEAPI = "weapi"
    LINUX_API = "linuxapi"
    EAPI = "eapi"
    API = "api"


class MusicApi:
    """NetEase Cloud Music API client."""

    def __init__(self, max_connections: int = 0):
        """Initialize client with httpx client and settings."""
        self.client = httpx.Client(
            timeout=TIMEOUT,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=max_connections or None),
        )
        self._csrf_token = ""
        self._cookies = {
            "os": "pc",
            "appver": "2.7.1.198277",
            "_ntes_nuid": create_random_string(32),
        }

    def _extract_csrf_token(self, cookies: Dict[str, str]) -> None:
        """Extract CSRF token from cookies."""
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        csrf_match = re.search(r"__csrf=([^(;|$)]+)", cookie_str)
        if csrf_match:
            self._csrf_token = csrf_match.group(1)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        crypto_type: CryptoApi = CryptoApi.API,
        ua_type: str = "",
        append_csrf: bool = True,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = build_url(BASE_URL, path)
        if append_csrf and self._csrf_token:
            if "?" in url:
                url = f"{url}&csrf_token={self._csrf_token}"
            else:
                url = f"{url}?csrf_token={self._csrf_token}"

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "music.163.com",
            "Referer": "https://music.163.com",
            "User-Agent": (
                LINUX_USER_AGENT
                if crypto_type == CryptoApi.LINUX_API
                else choose_user_agent(ua_type)
            ),
        }

        data = None
        if params is not None:
            if crypto_type == CryptoApi.LINUX_API:
                data = Crypto.linux_api(build_linux_api_data(url, params))
            elif crypto_type == CryptoApi.WEAPI:
                if append_csrf:
                    params["csrf_token"] = self._csrf_token
                data = Crypto.weapi(params)
            elif crypto_type == CryptoApi.EAPI:
                if append_csrf:
                    params["csrf_token"] = self._csrf_token
                data = Crypto.eapi({"url": path, "params": params})
            else:
                data = params

        # Print request info for debugging
        # print(f"\nRequesting {url} with method {method}")
        # print(f"Headers: {headers}")
        # print(f"Data: {data}")
        # print(f"Cookies before: {self._cookies}")

        try:
            resp = self.client.request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                cookies=self._cookies,
            )
            resp.raise_for_status()

            # Print response info for debugging
            # print(f"Response status: {resp.status_code}")
            # print(f"Response headers: {resp.headers}")
            # print(f"Response cookies: {resp.cookies}")
            # print(f"Response text: {resp.text}")

            # Update cookies and CSRF token
            self._cookies.update(dict(resp.cookies))
            self._extract_csrf_token(dict(resp.cookies))
            # print(f"Cookies after: {self._cookies}")

            result = resp.json()
            return result
        except Exception as e:
            print(f"Request failed: {str(e)}")
            if isinstance(e, httpx.HTTPError) and hasattr(e, "response"):
                response = getattr(e, "response", None)
                if response:
                    print(f"Response status: {response.status_code}")
                    print(f"Response text: {response.text}")
            return {"code": -1, "msg": str(e)}

    def login(self, username: str, password: str) -> LoginInfo:
        """Login with username (email/phone) and password."""
        params = {"password": password, "rememberLogin": "true"}

        if len(username) == 11 and username.isdigit():
            # Phone number login
            path = "/api/login/cellphone"
            params["phone"] = username
        else:
            # Email login
            path = "/weapi/login"
            params["username"] = username
            params["clientToken"] = (
                "1_jVUMqWEPke0/1/Vu56xCmJpo5vP1grjn_SOVVDzOc78w8OKLVZ2JH7IfkjSXqgfmh"
            )

        result = self._request("POST", path, params)
        return to_login_info(json.dumps(result))

    def login_cellphone(self, ctcode: str, phone: str, captcha: str) -> LoginInfo:
        """Login with phone number and verification code."""
        path = "/api/login/cellphone"
        params = {
            "phone": phone,
            "countrycode": ctcode,
            "captcha": captcha,
            "rememberLogin": "true",
        }
        result = self._request("POST", path, params)
        return to_login_info(json.dumps(result))

    def captcha(self, ctcode: str, phone: str) -> None:
        """Request SMS verification code."""
        path = "/api/sms/captcha/sent"
        params = {"cellphone": phone, "ctcode": ctcode}
        self._request("POST", path, params)

    def login_qr_create(self) -> Tuple[str, str]:
        """Create QR code for login."""
        path = "/api/login/qrcode/unikey"
        params = {"type": "1"}
        result = self._request("POST", path, params)
        unikey = result["unikey"]
        return (f"https://music.163.com/login?codekey={unikey}", unikey)

    def login_qr_check(self, key: str) -> Msg:
        """Check QR code login status."""
        path = "/api/login/qrcode/client/login"
        params = {"key": key, "type": "1"}
        result = self._request("POST", path, params)
        return to_msg(json.dumps(result))

    def login_status(self) -> LoginInfo:
        """Get current login status."""
        path = "/api/nuser/account/get"
        result = self._request("POST", path)
        print(result)
        return to_login_info(json.dumps(result))

    def logout(self) -> None:
        """Logout current user."""
        path = "/api/logout"
        self._request("POST", path)

    def daily_task(self) -> Msg:
        """Sign in for daily task."""
        path = "/api/point/dailyTask"
        params = {"type": "0"}
        result = self._request("POST", path, params)
        return to_msg(json.dumps(result))

    def user_song_id_list(self, uid: int) -> List[int]:
        """Get user's liked song IDs."""
        path = "/api/song/like/get"
        params = {"uid": str(uid)}
        result = self._request("POST", path, params)
        return to_song_id_list(json.dumps(result))

    def user_song_list(
        self, uid: int, offset: int = 0, limit: int = 30
    ) -> List[SongList]:
        """Get user's playlists."""
        path = "/api/user/playlist"
        params = {"uid": str(uid), "offset": str(offset), "limit": str(limit)}
        result = self._request("POST", path, params)
        song_lists = []

        if result and "code" in result and result["code"] == 200:
            # Process each playlist
            for playlist in result.get("playlist", []):
                created_song_list = {
                    "id": playlist.get("id", 0),
                    "name": playlist.get("name", ""),
                    "coverImgUrl": playlist.get("coverImgUrl", ""),
                    "description": playlist.get("description", ""),
                    "creator": playlist.get("creator", {}),
                }
                # Get songs
                songs = to_song_info(
                    json.dumps(
                        {
                            "code": 200,
                            "playlist": {"tracks": playlist.get("tracks", [])},
                        }
                    ),
                    "playlist",
                )
                song_lists.extend(to_song_list_from_songs(songs, created_song_list))

        return song_lists

    def album_sublist(self, offset: int = 0, limit: int = 30) -> List[SongList]:
        """Get user's subscribed albums."""
        path = "/api/album/sublist"
        params = {"total": "true", "offset": str(offset), "limit": str(limit)}
        result = self._request("POST", path, params)
        song_lists = []

        if result and "code" in result and result["code"] == 200:
            # Extract subscribed album data which contains the album metadata
            for album in result.get("data", []):
                # Create metadata for a single album
                created_song_list = {
                    "id": album.get("id", 0),
                    "name": album.get("name", ""),
                    "coverImgUrl": album.get("picUrl", ""),
                    "description": album.get("description", ""),
                    "creator": {
                        "nickname": album.get("artist", {}).get("name", "Unknown")
                    },
                }

                # Get songs for this album
                songs_in_album = to_song_info(
                    json.dumps({"code": 200, "songs": [album]}), "album"
                )
                # Add the album as a song list
                song_lists.extend(
                    to_song_list_from_songs(songs_in_album, created_song_list)
                )

        return song_lists

    def user_cloud_disk(self) -> List[SongInfo]:
        """Get user's cloud disk songs."""
        path = "/api/v1/cloud/get"
        params = {"offset": "0", "limit": "10000"}
        result = self._request("POST", path, params)
        return to_song_info(json.dumps(result), "cloud")

    def playlist_detail(self, songlist_id: int) -> PlayListDetail:
        """Get playlist details."""
        path = "/api/v6/playlist/detail"
        params = {
            "id": str(songlist_id),
            "offset": "0",
            "total": "true",
            "limit": "1000",
            "n": "1000",
        }
        result = self._request("POST", path, params)
        return to_play_list_detail(result.get("playlist", {}))

    def songs_detail(self, ids: List[int]) -> List[SongInfo]:
        """Get details for multiple songs."""
        path = "/api/v3/song/detail"
        c = [{"id": str(i)} for i in ids]
        params = {"c": json.dumps(c)}
        result = self._request("POST", path, params)
        return to_song_info(json.dumps(result), "songs")

    def songs_url(self, ids: List[int], br: str = "320000") -> List[SongUrl]:
        """Get song URLs."""
        path = "https://interface3.music.163.com/api/song/enhance/player/url"
        params = {"ids": json.dumps(ids), "br": br}
        result = self._request("POST", path, params, crypto_type=CryptoApi.EAPI)
        return [SongUrl(**url) for url in result.get("data", [])]

    def recommend_resource(self) -> List[SongList]:
        """Get daily recommended playlists."""
        path = "/api/v1/discovery/recommend/resource"
        result = self._request("POST", path)
        song_lists = []

        if result and "code" in result and result["code"] == 200:
            # Process each recommended resource
            for rec in result.get("recommend", []):
                created_song_list = {
                    "id": rec.get("id", 0),
                    "name": rec.get("name", ""),
                    "coverImgUrl": rec.get("picUrl", ""),
                    "description": rec.get("copywriter", ""),
                    "creator": rec.get("creator", {}),
                }
                # Get songs
                songs = to_song_info(
                    json.dumps({"code": 200, "recommend": [rec]}), "recommend"
                )
                song_lists.extend(to_song_list_from_songs(songs, created_song_list))

        return song_lists

    def recommend_songs(self) -> List[SongInfo]:
        """Get daily recommended songs."""
        path = "/api/v2/discovery/recommend/songs"
        params = {"total": "true"}
        result = self._request("POST", path, params)
        return to_song_info(json.dumps(result), "recommend_songs")

    def personal_fm(self) -> List[SongInfo]:
        """Get personal FM playlist."""
        path = "/api/v1/radio/get"
        result = self._request("POST", path)
        return to_song_info(json.dumps(result), "personal_fm")

    def like(self, songid: int, like: bool = True) -> bool:
        """Like/unlike a song."""
        path = "/api/radio/like"
        params = {
            "alg": "itembased",
            "trackId": str(songid),
            "like": str(like).lower(),
            "time": "25",
        }
        result = self._request("POST", path, params)
        msg = to_msg(json.dumps(result))
        return msg.code == 200

    def fm_trash(self, songid: int) -> bool:
        """Add song to FM trash."""
        path = "/api/radio/trash/add"
        params = {"alg": "RT", "songId": str(songid), "time": "25"}
        result = self._request("POST", path, params)
        msg = to_msg(json.dumps(result))
        return msg.code == 200

    def search(
        self, keywords: str, type_: int = 1, offset: int = 0, limit: int = 30
    ) -> str:
        """Search for music/albums/artists/playlists/etc."""
        path = "/api/search/get"
        params = {
            "s": keywords,
            "type": str(type_),
            "offset": str(offset),
            "limit": str(limit),
        }
        result = self._request("POST", path, params)
        return json.dumps(result)

    def search_song(
        self, keywords: str, offset: int = 0, limit: int = 30
    ) -> List[SongInfo]:
        """Search for songs.

        Args:
            keywords: Search keywords
            offset: Start offset
            limit: Number of results per page

        Returns:
            List of matched songs
        """
        result = self.search(keywords, 1, offset, limit)
        result = json.loads(result)
        song_list = []

        if result and "code" in result and result["code"] == 200:
            # Process each song in search results
            for song in result.get("result", {}).get("songs", []):
                song_list.append(to_songinfo(json.dumps(song)))
        return song_list

    def search_singer(
        self, keywords: str, offset: int = 0, limit: int = 30
    ) -> List[SingerInfo]:
        """Search for singers.

        Args:
            keywords: Search keywords
            offset: Start offset
            limit: Number of results per page

        Returns:
            List of matched singers
        """
        result = self.search(keywords, 100, offset, limit)
        return [
            SingerInfo(**singer)
            for singer in json.loads(result).get("result", {}).get("artists", [])
        ]

    def search_album(
        self, keywords: str, offset: int = 0, limit: int = 30
    ) -> List[SongList]:
        """Search for albums.

        Args:
            keywords: Search keywords
            offset: Start offset
            limit: Number of results per page

        Returns:
            List of matched albums
        """
        result = self.search(keywords, 10, offset, limit)
        result_data = json.loads(result)
        song_lists = []

        if result_data and "code" in result_data and result_data["code"] == 200:
            # Process each album in search results
            for album in result_data.get("result", {}).get("albums", []):
                created_song_list = {
                    "id": album.get("id", 0),
                    "name": album.get("name", ""),
                    "coverImgUrl": album.get("picUrl", ""),
                    "description": album.get("description", ""),
                    "creator": {
                        "nickname": album.get("artist", {}).get("name", "Unknown")
                    },
                }
                # Get songs
                songs = to_song_info(
                    json.dumps({"code": 200, "songs": [album]}), "album"
                )
                song_lists.extend(to_song_list_from_songs(songs, created_song_list))

        return song_lists

    def search_songlist(
        self, keywords: str, offset: int = 0, limit: int = 30
    ) -> List[SongList]:
        """Search for playlists.

        Args:
            keywords: Search keywords
            offset: Start offset
            limit: Number of results per page

        Returns:
            List of matched playlists
        """
        result = self.search(keywords, 1000, offset, limit)
        result_data = json.loads(result)
        song_lists = []

        if result_data and "code" in result_data and result_data["code"] == 200:
            # Process each playlist in search results
            for playlist in result_data.get("result", {}).get("playlists", []):
                created_song_list = {
                    "id": playlist.get("id", 0),
                    "name": playlist.get("name", ""),
                    "coverImgUrl": playlist.get("coverImgUrl", ""),
                    "description": playlist.get("description", ""),
                    "creator": playlist.get("creator", {}),
                }
                # Get songs
                songs = to_song_info(
                    json.dumps({"code": 200, "playlist": playlist}), "playlist"
                )
                song_lists.extend(to_song_list_from_songs(songs, created_song_list))

        return song_lists

    def search_lyrics(
        self, keywords: str, offset: int = 0, limit: int = 30
    ) -> List[SongInfo]:
        """Search for lyrics.

        Args:
            keywords: Search keywords
            offset: Start offset
            limit: Number of results per page

        Returns:
            List of songs matched by lyrics
        """
        result = self.search(keywords, 1006, offset, limit)
        return to_song_info(json.dumps(result), "search")

    def singer_songs(self, id: int) -> List[SongInfo]:
        """Get singer's hot songs.

        Args:
            id: Singer ID
        """
        path = f"/api/v1/artist/{id}"
        result = self._request("POST", path, {}, append_csrf=False)
        return to_song_info(json.dumps(result), "singer")

    def singer_all_songs(
        self, id: int, order: str = "hot", offset: int = 0, limit: int = 30
    ) -> List[SongInfo]:
        """Get all songs of a singer.

        Args:
            id: Singer ID
            order: Sort order ("hot" or "time")
            offset: Offset for pagination
            limit: Number of songs to return
        """
        path = "/api/v1/artist/songs"
        params = {
            "id": str(id),
            "private_cloud": "true",
            "work_type": "1",
            "order": order,
            "offset": str(offset),
            "limit": str(limit),
        }
        result = self._request("POST", path, params, append_csrf=False)
        return to_song_info(json.dumps(result), "singer_songs")

    def new_albums(
        self, area: str = "ALL", offset: int = 0, limit: int = 30
    ) -> List[SongList]:
        """Get new albums.

        Args:
            area: Area filter ("ALL", "ZH", "EA", "KR", "JP")
            offset: Offset for pagination
            limit: Number of albums to return
        """
        path = "/api/album/new"
        params = {
            "area": area,
            "offset": str(offset),
            "limit": str(limit),
            "total": "true",
        }
        result = self._request("POST", path, params)
        song_lists = []

        if result and "code" in result and result["code"] == 200:
            # Process each new album
            for album in result.get("albums", []):
                created_song_list = {
                    "id": album.get("id", 0),
                    "name": album.get("name", ""),
                    "coverImgUrl": album.get("picUrl", ""),
                    "description": album.get("description", ""),
                    "creator": {
                        "nickname": album.get("artist", {}).get("name", "Unknown")
                    },
                }
                # Get songs
                songs = to_song_info(
                    json.dumps({"code": 200, "songs": [album]}), "album"
                )
                song_lists.extend(to_song_list_from_songs(songs, created_song_list))

        return song_lists

    def album(self, album_id: int) -> AlbumDetail:
        """Get album details.

        Args:
            album_id: Album ID
        """
        path = f"/api/v1/album/{album_id}"
        result = self._request("POST", path, {})
        return to_album_detail(result)

    def songlist_detail_dynamic(self, songlist_id: int) -> PlayListDetailDynamic:
        """Get dynamic details of a playlist.

        Args:
            songlist_id: Playlist ID
        """
        path = "/api/playlist/detail/dynamic"
        params = {"id": str(songlist_id)}
        result = self._request("POST", path, params)
        return PlayListDetailDynamic(
            subscribed=result.get("subscribed", False),
            shareCount=result.get("shareCount", 0),
            commentCount=result.get("commentCount", 0),
            playCount=result.get("playCount", 0),
        )

    def album_detail_dynamic(self, album_id: int) -> AlbumDetailDynamic:
        """Get dynamic details of an album.

        Args:
            album_id: Album ID
        """
        path = "/api/album/detail/dynamic"
        params = {"id": str(album_id)}
        result = self._request("POST", path, params)
        return AlbumDetailDynamic(
            onSale=result.get("onSale", False),
            subCount=result.get("subCount", 0),
            liked=result.get("liked", False),
            commentCount=result.get("commentCount", 0),
            shareCount=result.get("shareCount", 0),
        )

    def top_song_list(
        self, cat: str = "全部", order: str = "hot", offset: int = 0, limit: int = 30
    ) -> List[SongList]:
        """Get top playlists with no track details.

        Args:
            cat: Category filter
            order: Sort order ("hot" or "new")
            offset: Offset for pagination
            limit: Number of playlists to return
        """
        path = "/api/playlist/list"
        params = {
            "cat": cat,
            "order": order,
            "total": "true",
            "offset": str(offset),
            "limit": str(limit),
        }
        result = self._request("POST", path, params)
        song_lists = []

        if result and "code" in result and result["code"] == 200:
            # Process each playlist from result directly
            for playlist in result.get("playlists", []):
                # Create SongList without song details for now
                song_lists.append(to_playlist(json.dumps(playlist)))

        return song_lists

    def top_song_list_highquality(
        self, cat: str = "全部", lasttime: int = 0, limit: int = 30
    ) -> List[SongList]:
        """Get high quality playlists.

        Args:
            cat: Category filter
            lasttime: Last update time for pagination
            limit: Number of playlists to return
        """
        path = "/api/playlist/highquality/list"
        params = {
            "cat": cat,
            "total": "true",
            "lasttime": str(lasttime),
            "limit": str(limit),
        }
        result = self._request("POST", path, params)
        song_lists = []

        if result and "code" in result and result["code"] == 200:
            # Process each high quality playlist
            for playlist in result.get("playlists", []):
                created_song_list = {
                    "id": playlist.get("id", 0),
                    "name": playlist.get("name", ""),
                    "coverImgUrl": playlist.get("coverImgUrl", ""),
                    "description": playlist.get("description", ""),
                    "creator": playlist.get("creator", {}),
                }
                # Get songs
                songs = to_song_info(
                    json.dumps({"code": 200, "playlist": playlist}), "playlist"
                )
                song_lists.extend(to_song_list_from_songs(songs, created_song_list))

        return song_lists

    def toplist(self) -> List[TopList]:
        """Get all toplists."""
        path = "/api/toplist"
        result = self._request("POST", path, {})
        toplists = []
        for item in result.get("list", []):
            toplist = TopList(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                coverImgUrl=item.get("coverImgUrl", ""),
                updateFrequency=item.get("updateFrequency", ""),
                tracks=item.get("tracks", []),
            )
            toplists.append(toplist)
        return toplists

    def top_songs(self, list_id: int) -> PlayListDetail:
        """Get songs in a toplist.

        Args:
            list_id: Toplist ID
        """
        return self.song_list_detail(list_id)

    def song_lyric(self, music_id: int) -> Lyrics:
        """Get song lyrics.

        Args:
            music_id: Song ID
        """
        path = "/weapi/song/lyric"
        params = {
            "id": str(music_id),
            "lv": "-1",
            "tv": "-1",
            "csrf_token": self._csrf_token,
        }
        result = self._request("POST", path, params)
        return Lyrics(
            lrc=result.get("lrc", {}).get("lyric", ""),
            tlyric=result.get("tlyric", {}).get("lyric", ""),
        )

    def song_list_like(self, like: bool, id: int) -> bool:
        """Subscribe/unsubscribe to a playlist.

        Args:
            like: True to subscribe, False to unsubscribe
            id: Playlist ID
        """
        path = "/api/playlist/subscribe" if like else "/api/playlist/unsubscribe"
        params = {"id": str(id)}
        result = self._request("POST", path, params)
        msg = to_msg(json.dumps(result))
        return msg.code == 200

    def album_like(self, like: bool, id: int) -> bool:
        """Subscribe/unsubscribe to an album.

        Args:
            like: True to subscribe, False to unsubscribe
            id: Album ID
        """
        path = f"/api/album/{'sub' if like else 'unsub'}?id={id}"
        params = {"id": str(id)}
        result = self._request("POST", path, params, append_csrf=False)
        msg = to_msg(json.dumps(result))
        return msg.code == 200

    def homepage(self, client_type: Optional[ClientType] = None) -> str:
        """Get homepage block data.

        Args:
            client_type: Client type info
        """
        path = "/api/homepage/block/page"
        params = {"refresh": "false", "cursor": "null"}
        result = self._request("POST", path, params)
        return json.dumps(result)

    def banners(self) -> List[BannersInfo]:
        """Get homepage banners."""
        path = "/api/v2/banner/get"
        params = {"clientType": "pc"}
        result = self._request("POST", path, params)
        print(result)
        return to_banners_info(json.dumps(result))

    def download_img(self, url: str, path: str, width: int, height: int) -> None:
        """Download an image from network and save to local path.

        Args:
            url: Image URL
            path: Local save path (including filename)
            width: Image width
            height: Image height
        """
        if not os.path.exists(path):
            image_url = f"{url}?param={width}y{height}"
            response = self.client.get(image_url)
            response.raise_for_status()

            with open(path, "wb") as f:
                f.write(response.content)

    def download_song(self, url: str, path: str) -> None:
        """Download a song from network and save to local path.

        Args:
            url: Song URL
            path: Local save path (including filename)
        """
        if not os.path.exists(path):
            response = self.client.get(url)
            response.raise_for_status()

            with open(path, "wb") as f:
                f.write(response.content)

    def user_radio_sublist(self, offset: int = 0, limit: int = 30) -> Dict[str, Any]:
        """Get user's subscribed radio lists.

        Args:
            offset: Start offset for pagination
            limit: Number of results per page

        Returns:
            Dict containing subscribed radio stations
        """
        path = "/api/djradio/get/subed"
        params = {"total": "true", "offset": str(offset), "limit": str(limit)}
        return self._request("POST", path, params)

    def radio_program(
        self, radio_id: int, offset: int = 0, limit: int = 30, asc: bool = False
    ) -> Dict[str, Any]:
        """Get program list for a radio station.

        Args:
            radio_id: ID of the radio station
            offset: Start offset for pagination
            limit: Number of results per page
            asc: Sort in ascending order if True, descending if False

        Returns:
            Dict containing radio programs
        """
        path = "/api/dj/program/byradio"
        params = {
            "radioId": str(radio_id),
            "offset": str(offset),
            "limit": str(limit),
            "asc": str(asc).lower(),
        }
        return self._request("POST", path, params)

    def playmode_intelligence_list(
        self,
        song_id: int,
        sid: Optional[str] = None,
        play_list_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get intelligent playlist based on a song (heart mode).

        Args:
            song_id: ID of the seed song
            sid: Session ID (optional)
            play_list_id: ID of the playlist (optional)

        Returns:
            Dict containing intelligent playlist
        """
        path = "/api/playmode/intelligence/list"
        params = {"songId": str(song_id), "type": "fromPlayOne"}
        if sid:
            params["sid"] = sid
        if play_list_id:
            params["playlistId"] = play_list_id

        return self._request("POST", path, params)
