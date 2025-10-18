"""
Copyright (c) 2023-2024 Bipinkrish
This file is part of the Zlibrary-API by Bipinkrish
Zlibrary-API / Zlibrary.py

For more information, see:
https://github.com/bipinkrish/Zlibrary-API/
"""

import contextlib
from typing import Any, Optional, Union

import requests


class Zlibrary:
    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        remix_userid: Optional[Union[int, str]] = None,
        remix_userkey: Optional[str] = None,
    ) -> None:
        self.__email: str
        self.__name: str
        self.__kindle_email: str
        self.__remix_userid: Union[int, str]
        self.__remix_userkey: str
        self.__domain: str = "1lib.sk"

        self.__loggedin: bool = False
        self.__headers: dict[str, str] = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            ),
            "accept-language": "en-US,en;q=0.9",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/110.0.0.0 Safari/537.36"
            ),
        }
        self.__cookies: dict[str, str] = {
            "siteLanguageV2": "en",
        }

        if email is not None and password is not None:
            self.login(email, password)
        elif remix_userid is not None and remix_userkey is not None:
            self.loginWithToken(remix_userid, remix_userkey)

    def __setValues(self, response: dict[str, Any]) -> dict[str, Any]:
        if not response["success"]:
            return response
        self.__email = response["user"]["email"]
        self.__name = response["user"]["name"]
        self.__kindle_email = response["user"]["kindle_email"]
        self.__remix_userid = str(response["user"]["id"])
        self.__remix_userkey = response["user"]["remix_userkey"]
        self.__cookies["remix_userid"] = self.__remix_userid
        self.__cookies["remix_userkey"] = self.__remix_userkey
        self.__loggedin = True
        return response

    def __login(self, email: str, password: str) -> dict[str, Any]:
        return self.__setValues(
            self.__makePostRequest(
                "/eapi/user/login",
                data={
                    "email": email,
                    "password": password,
                },
                override=True,
            )
        )

    def __checkIDandKey(self, remix_userid: Union[int, str], remix_userkey: str) -> dict[str, Any]:
        return self.__setValues(
            self.__makeGetRequest(
                "/eapi/user/profile",
                cookies={
                    "siteLanguageV2": "en",
                    "remix_userid": str(remix_userid),
                    "remix_userkey": remix_userkey,
                },
            )
        )

    def login(self, email: str, password: str) -> dict[str, Any]:
        return self.__login(email, password)

    def loginWithToken(self, remix_userid: Union[int, str], remix_userkey: str) -> dict[str, Any]:
        return self.__checkIDandKey(remix_userid, remix_userkey)

    def __makePostRequest(
        self, url: str, data: Optional[dict[str, Any]] = None, override: bool = False
    ) -> dict[str, Any]:
        if data is None:
            data = {}
        if not self.isLoggedIn() and override is False:
            print("Not logged in")
            return {}

        response: dict[str, Any] = requests.post(
            "https://" + self.__domain + url,
            data=data,
            cookies=self.__cookies,
            headers=self.__headers,
        ).json()
        return response

    def __makeGetRequest(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        cookies: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        if params is None:
            params = {}
        if not self.isLoggedIn() and cookies is None:
            print("Not logged in")
            return {}

        response: dict[str, Any] = requests.get(
            "https://" + self.__domain + url,
            params=params,
            cookies=self.__cookies if cookies is None else cookies,
            headers=self.__headers,
        ).json()
        return response

    def getProfile(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/user/profile")

    def getMostPopular(self, switch_language: Optional[str] = None) -> dict[str, Any]:
        if switch_language is not None:
            return self.__makeGetRequest(
                "/eapi/book/most-popular", {"switch-language": switch_language}
            )
        return self.__makeGetRequest("/eapi/book/most-popular")

    def getRecently(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/book/recently")

    def getUserRecommended(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/user/book/recommended")

    def deleteUserBook(self, bookid: Union[int, str]) -> dict[str, Any]:
        return self.__makeGetRequest(f"/eapi/user/book/{bookid}/delete")

    def unsaveUserBook(self, bookid: Union[int, str]) -> dict[str, Any]:
        return self.__makeGetRequest(f"/eapi/user/book/{bookid}/unsave")

    def getBookForamt(self, bookid: Union[int, str], hashid: str) -> dict[str, Any]:
        return self.__makeGetRequest(f"/eapi/book/{bookid}/{hashid}/formats")

    def getDonations(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/user/donations")

    def getUserDownloaded(
        self,
        order: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        order takes one of the values\n
        ["year",...]
        """
        params = {
            k: v for k, v in {"order": order, "page": page, "limit": limit}.items() if v is not None
        }
        return self.__makeGetRequest("/eapi/user/book/downloaded", params)

    def getExtensions(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/info/extensions")

    def getDomains(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/info/domains")

    def getLanguages(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/info/languages")

    def getPlans(self, switch_language: Optional[str] = None) -> dict[str, Any]:
        if switch_language is not None:
            return self.__makeGetRequest("/eapi/info/plans", {"switch-language": switch_language})
        return self.__makeGetRequest("/eapi/info/plans")

    def getUserSaved(
        self,
        order: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        order takes one of the values\n
        ["year",...]
        """
        params = {
            k: v for k, v in {"order": order, "page": page, "limit": limit}.items() if v is not None
        }
        return self.__makeGetRequest("/eapi/user/book/saved", params)

    def getInfo(self, switch_language: Optional[str] = None) -> dict[str, Any]:
        if switch_language is not None:
            return self.__makeGetRequest("/eapi/info", {"switch-language": switch_language})
        return self.__makeGetRequest("/eapi/info")

    def hideBanner(self) -> dict[str, Any]:
        return self.__makeGetRequest("/eapi/user/hide-banner")

    def recoverPassword(self, email: str) -> dict[str, Any]:
        return self.__makePostRequest(
            "/eapi/user/password-recovery", {"email": email}, override=True
        )

    def makeRegistration(self, email: str, password: str, name: str) -> dict[str, Any]:
        return self.__makePostRequest(
            "/eapi/user/registration",
            {"email": email, "password": password, "name": name},
            override=True,
        )

    def resendConfirmation(self) -> dict[str, Any]:
        return self.__makePostRequest("/eapi/user/email/confirmation/resend")

    def saveBook(self, bookid: Union[int, str]) -> dict[str, Any]:
        return self.__makeGetRequest(f"/eapi/user/book/{bookid}/save")

    def sendTo(self, bookid: Union[int, str], hashid: str, totype: str) -> dict[str, Any]:
        return self.__makeGetRequest(f"/eapi/book/{bookid}/{hashid}/send-to-{totype}")

    def getBookInfo(
        self,
        bookid: Union[int, str],
        hashid: str,
        switch_language: Optional[str] = None,
    ) -> dict[str, Any]:
        if switch_language is not None:
            return self.__makeGetRequest(
                f"/eapi/book/{bookid}/{hashid}", {"switch-language": switch_language}
            )
        return self.__makeGetRequest(f"/eapi/book/{bookid}/{hashid}")

    def getSimilar(self, bookid: Union[int, str], hashid: str) -> dict[str, Any]:
        return self.__makeGetRequest(f"/eapi/book/{bookid}/{hashid}/similar")

    def makeTokenSigin(self, name: str, id_token: str) -> dict[str, Any]:
        return self.__makePostRequest(
            "/eapi/user/token-sign-in",
            {"name": name, "id_token": id_token},
            override=True,
        )

    def updateInfo(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        name: Optional[str] = None,
        kindle_email: Optional[str] = None,
    ) -> dict[str, Any]:
        return self.__makePostRequest(
            "/eapi/user/update",
            {
                k: v
                for k, v in {
                    "email": email,
                    "password": password,
                    "name": name,
                    "kindle_email": kindle_email,
                }.items()
                if v is not None
            },
        )

    def search(
        self,
        message: Optional[str] = None,
        yearFrom: Optional[int] = None,
        yearTo: Optional[int] = None,
        languages: Optional[str] = None,
        extensions: Optional[str] = None,
        order: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        return self.__makePostRequest(
            "/eapi/book/search",
            {
                k: v
                for k, v in {
                    "message": message,
                    "yearFrom": yearFrom,
                    "yearTo": yearTo,
                    "languages": languages,
                    "extensions[]": extensions,
                    "order": order,
                    "page": page,
                    "limit": limit,
                }.items()
                if v is not None
            },
        )

    def __getImageData(self, url: str) -> Optional[bytes]:
        res = requests.get(url, headers=self.__headers)
        if res.status_code == 200:
            return res.content
        return None

    def getImage(self, book: dict[str, Any]) -> Optional[bytes]:
        return self.__getImageData(book["cover"])

    def __getBookFile(self, bookid: Union[int, str], hashid: str) -> Optional[tuple[str, bytes]]:
        response = self.__makeGetRequest(f"/eapi/book/{bookid}/{hashid}/file")
        
        # Use description if available, otherwise fall back to title or a generic name
        file_info = response.get("file", {})
        filename = file_info.get("description") or file_info.get("title", f"book_{bookid}")

        with contextlib.suppress(Exception):
            author = file_info.get("author")
            if author:
                filename += " (" + author + ")"

        extension = file_info.get("extension", "pdf")
        filename += "." + extension

        ddl = file_info.get("downloadLink")
        if not ddl:
            return None
            
        headers = self.__headers.copy()
        headers["authority"] = ddl.split("/")[2]

        res = requests.get(ddl, headers=headers)
        if res.status_code == 200:
            return filename, res.content
        return None

    def downloadBook(self, book: dict[str, Any]) -> Optional[tuple[str, bytes]]:
        return self.__getBookFile(book["id"], book["hash"])

    def isLoggedIn(self) -> bool:
        return self.__loggedin

    def sendCode(self, email: str, password: str, name: str) -> dict[str, Any]:
        usr_data: dict[str, Any] = {
            "email": email,
            "password": password,
            "name": name,
            "rx": 215,
            "action": "registration",
            "site_mode": "books",
            "isSinglelogin": 1,
        }
        response = self.__makePostRequest(
            "/papi/user/verification/send-code", data=usr_data, override=True
        )
        if response.get("success"):
            response["msg"] = (
                "Verification code is sent to mail, use verify_code to complete registration"
            )
        return response

    def verifyCode(self, email: str, password: str, name: str, code: str) -> dict[str, Any]:
        usr_data: dict[str, Any] = {
            "email": email,
            "password": password,
            "name": name,
            "verifyCode": code,
            "rx": 215,
            "action": "registration",
            "redirectUrl": "",
            "isModa": True,
            "gg_json_mode": 1,
        }
        return self.__makePostRequest("/rpc.php", data=usr_data, override=True)

    def getDownloadsLeft(self) -> int:
        user_profile: dict[str, Any] = self.getProfile()["user"]
        downloads_limit: int = user_profile.get("downloads_limit", 10)
        downloads_today: int = user_profile.get("downloads_today", 0)
        return downloads_limit - downloads_today
