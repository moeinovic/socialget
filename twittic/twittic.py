from pprint import pprint
from urllib import response
import requests
from re import search
from .exceptions import (TooManyRequests, TwitterException, HTTPException, BadRequest, Unauthorized, Forbidden, NotFound, TwitterServerError)
from operator import itemgetter
import math
from json import loads, dumps
#class for twitter api without registering an app
class TwitterAPI:
    def __init__(self, access_token=None, proxies=None):
        self.pattern = "^(https?:\/\/(?:www\.)?(?:mobile\.)?twitter\.com(?:\/(?!.*\.\.)(?!.*\\.$)[^\W][\w.]{1,29})?\/status(es)?\/([\d+]{16,19}))"
        if access_token is None:
            access_token = "AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
        else:
            access_token = access_token
        
        self.access_token = access_token
        self.session = requests.Session()
        self.base_url = "https://api.twitter.com/1.1/"
        self.proxies = {}
        if proxies is not None:
            self.proxies = proxies
            self.session.proxies.update(self.proxies)
        self.headers = {
            "Authorization": "Bearer " + self.access_token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        
        
        self.params = {
            "cards_platform": "Web-12",
            "include_cards": 1,
            "include_reply_count": 1,
            "include_user_entities": 1,
            "tweet_mode": "extended"
        }
    
    def request(self, url, method, params=None, headers=None):
        try:

            if params is None:
                params = {}
            
            if headers is None:
                headers = {}
            
            try:
                response = self.session.request(url=url, method=method, headers=headers, params=params, timeout=10)
                print(response)
            except:
                raise TwitterException("Failed to send request")
            
            if response.status_code == 200:
                return response
            elif response.status_code == 400:
                raise BadRequest(response)
            elif response.status_code == 401:
                raise Unauthorized(response)
            elif response.status_code == 403:
                raise Forbidden(response)
            elif response.status_code == 404:
                raise NotFound(response)
            elif response.status_code == 429:
                raise TooManyRequests(response)
                pprint(response)
            elif response.status_code >= 500:
                raise TwitterServerError(response)
            elif response.status_code and 200 >= response.status_code >= 300:
                raise HTTPException(response)
        finally:
            self.session.close()
    
    def get_token(self):
        url = self.base_url + "guest/activate.json"
        try:
            response = self.request(url, method="POST", headers=self.headers).json()
            print(response.headers)
        except Exception as e:
            raise TwitterException(e)

        return response["guest_token"]

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def media_parser(self, media):
        if media["type"] == "photo":
            return {
                "type": "photo",
                "url": media["media_url_https"],
            }
        elif media["type"] == "video" or media["type"] == "animated_gif":
            #get biggest bitraite url from list of variants
            if "video_info" in media:
                try:
                    variants = media["video_info"]["variants"]
                    #Delete variants that do not have a bitraite
                    variants = [variant for variant in variants if "bitrate" in variant]
                    variants = sorted(variants, key=itemgetter("bitrate"), reverse=True)
                    #sort varints by bitrait if content_type is video/mp4 and has bitrate
                    urls = []
                    thumbnail_url = media["media_url_https"]
                    for variant in variants:
                        video_url = variant["url"]
                        data = {
                            "url": video_url,
                            "resolution": video_url.split("/")[-2],
                        }
                        urls.append(data)

                    return {
                        "type": media["type"],
                        "urls": urls,
                        "thumbnail_url": thumbnail_url
                    }
                except Exception as e:
                    raise e

    def quoted_media_parser(self, status):
        quoted = status["is_quote_status"]
        if quoted is True:
            quoted_status = status["quoted_status"]
            if "extended_entities" in quoted_status:
                quoted_status = quoted_status["extended_entities"]
                if "media" in quoted_status:
                    quoted_status = quoted_status["media"]
                    count = len(quoted_status)
                    if count > 0:
                        medias = [self.media_parser(media) for media in quoted_status]
                        return True, medias, count
        elif "entities" in status:
            status = status["entities"]
            if "urls" in status:
                status = status["urls"]
                for url in status:
                    if "photo" or "video" in url["expanded_url"]:
                        sid = search(self.pattern, url["expanded_url"]).group(3)
                        info = self.get_status(sid, only_media=True)
                        return info["has_media"], info["medias"], info["media_count"]
        return False, [], 0

    def get_status(self, tweet_id, only_media=False, raw=False):
        try:
            url = self.base_url + "statuses/show.json"
            params = self.params
            params["id"] = tweet_id
            x_auth_token = self.get_token()
            self.headers["X-Auth-Token"] = x_auth_token
            response = self.request(url, method="GET", params=params, headers=self.headers).json()
            has_media  = True if "extended_entities" in response else False
            if has_media:
                media_count = len(response["extended_entities"]["media"])
                medias = [self.media_parser(media_sec) for media_sec in response["extended_entities"]["media"]]
            else:
                has_media, medias, media_count = self.quoted_media_parser(response)
            if only_media:
                data = {
                    "has_media": has_media,
                    "media_count": media_count,
                    "medias": medias,
                    "id": response["id_str"],
                }
            else:
                full_text = response["full_text"]
                data = {
                    "full_text": full_text,
                    "reply_count": response["reply_count"],
                    "retweet_count": response["retweet_count"],
                    "favorite_count": response["favorite_count"],
                    "has_media": has_media,
                    "media_count": media_count,
                    "medias": medias,
                    "user": {
                        "name": response["user"]["name"],
                        "user_name": response["user"]["screen_name"],
                        "verified": response["user"]["verified"],
                    }
                }
            if raw:
                return response
            return data
        except Exception as e:
            raise e
