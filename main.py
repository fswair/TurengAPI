from ctypes import Union
import logging
from httpx import stream
from requests import get
from bs4 import BeautifulSoup
from time import time
from time import sleep
import re
from json import dumps
import json


class Tureng(object):

    def __init__(
        self,
        word: str = "",
        type: str = "",
        main_results: bool = True,
        other_results: bool = False,
        suggest_related_words: bool = 0,

    ) -> None:
        self.word = word
        self.suggest_related_words = suggest_related_words
        self.types = {
            "tr-en": "turkce-ingilizce",
            "de-en": "almanca-ingilizce",
            "es-en": "ispanyolca-ingilizce",
            "fr-en": "fransizca-ingilizce",
        }

        self.other_results = other_results
        self.main_results = main_results
        self.type = self.get_type_of_query(type, self.types)
        self.request_url = f"https://tureng.com/tr/{self.type}/{word}"

        self.informations = dict()

        self.request()

    def get(self, id: int):
        main = self.informations[self.word]["main"]
        if id > len(main):
            return main[0]
        return main[id-1]

    def get_type_of_query(self, arg: str, types: dict) -> str:
        pattern = re.findall("[ ?\W?]?(\w{2})?[\-\W]?(\w{2})?", arg.lower())

        try:
            for i, key in enumerate(list(types.keys())):
                _type = pattern[0][0]
                if _type == "en":
                    _type = pattern[0][-1]
                if key == _type or _type in key:
                    return list(types.values())[i]
        except IndexError:
            logging.error("Entered language type is not correct style.")
            return types["tr-en"]
    
    def get_related_words(self,
        query: str = "",
        rapid_api_key: str = "your_api_key"
    ) -> list[str]:
        """GET API KEY FROM: https://rapidapi.com/dpventures/api/wordsapi/pricing"""
        try:
            if not query:
                query = self.word

            words = get(
                f"https://wordsapiv1.p.rapidapi.com/words/{query}/typeOf",
                headers={
                    "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
                    "X-RapidAPI-Key": rapid_api_key,
                    "User-Agent": "Mozilla Firefox V1.0",
                },
            ).json()["typeOf"]

            return words
        except:
            return "This tool works for just english words."

    def request(self) -> None:
        r = get(
            self.request_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:6.0) Gecko/20110314 Firefox/36.0"
            },
        )

        scraper = BeautifulSoup(r.content, "html.parser")
        results = [
            int("".join([d for d in x.text if d.isdigit()]))
            for x in scraper.select("h2")
        ]

        tables = [
            x
            for x in scraper.select("tr")
            if "glyphicon glyphicon-option-horizontal" in str(x)
        ]

        self.informations[self.word] = {}

        if self.main_results:
            main_res = tuple(
                [
                    (i, j)
                    for i, j in [
                        (
                            [element.text for element in table.select("td")][2].strip("\n"),
                            [element.text for element in table.select("td")][3].strip("\n"),
                        )
                        for table in list(tables)[: results[0]]
                    ]
                ]
            )

            self.informations[self.word]["main"] = main_res

        if self.other_results:
            other_res = tuple(
                [
                    (i, j)
                    for i, j in [
                        (
                            [element.text for element in table.select("td")][2].strip("\n"),
                            [element.text for element in table.select("td")][3].strip("\n"),
                        )
                        for table in list(tables)[results[0]:]
                    ]
                ]
            )
            self.informations[self.word]["other"] = other_res
    

