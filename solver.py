import os
import sys
import requests
import hashlib
from urllib import parse
from datetime import datetime, timedelta
from html.parser import HTMLParser
from typing import Union
import json
import random

session = requests.Session()

def signin(usr, pwd):
    signin = session.post("https://zyserver.zybooks.com/v1/signin", json={"email": usr, "password": pwd}).json()
    if not signin["success"]:
        raise Exception("fart noise")
    return signin

def getbooks(userid, auth):
        books = session.get(f"https://zyserver.zybooks.com/v1/user/{userid}/items?items=%5B%22zybooks%22%5D&auth_token={auth}").json()
        booklist_raw = books["items"]["zybooks"]
        booksdict = dict()
        for book in booklist_raw:
            booksdict[book["title"]] = book["zybook_code"]
        return booksdict
       #
       # with open("testjson", "w") as outfile: #DELETE THIS AFTER WE DONT' NEED THIS JAWN
        #    json.dump(books.json(), outfile)    
        #

def getchapters(auth, bookcode):
    chapters = session.get(f"https://zyserver2.zybooks.com/v1/zybook/{bookcode}/ordering?include=%5B%22content_ordering%22%5D&auth_token={auth}", data={
        "authority" : "zyserver.zybooks.com",   
        "method" : "GET",
        "Accept" : "application/json, text/javascript, */*; q=0.01",
        "Sec-Ch-Ua" : """Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123""",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Sec-Fetch-Dest" : "empty",
        "Sec-Fetch-Mode" : "cors",
        "Sec-Fetch-Site" : "same-site"
    }).json()
    #print(chapters)
    chapter_list = chapters["ordering"]["content_ordering"]["chapters"]

    return chapter_list

#chapter was originally chapter['number']-1
def getsections(chapter_list,  chapter : int):
    #print(chapter_list)
    section_list = chapter_list[chapter-1]["sections"]
    return section_list

def getactivities(bookcode, chapter, section, auth):
    activities = session.get(f"https://zyserver.zybooks.com/v1/zybook/{bookcode}/chapter/{chapter}/section/{section}?auth_token={auth}").json()
    return activities["section"]["content_resources"]


def timespoof(): #TIME SPOOFER TAKEN FROM ONLINE MAYBE IT WORKS?
    global t_spfd
    ct = datetime.now()
    nt = ct + timedelta(seconds=t_spfd)
    ms = f"{random.randint(0, 999):03}"
    ts = nt.strftime(f"%Y-%m-%dT%H:%M:{ms}Z")
    return ts

def committimefraud(auth, section_id, activity_id, part, bookcode):
    global t_spfd
    t = random.randint(1, 60)
    t_spfd += t
    ts = timespoof()
    return session.post(f"https://zyserver2.zybooks.com/v1/zybook/{bookcode}/time_spent", json={"time_spent_records":[{"canonical_section_id":section_id,"content_resource_id":activity_id,"part":part,"time_spent":t,"timestamp":ts}],"auth_token":auth}).json()["success"]

def getbuild(): #ALSO TOOK THIS FROM ONLINE I HAVE NO IDEA WHAT THE FUCK THIS DOES
    class Parser(HTMLParser):
        def handle_starttag(self, tag: str, attrs: list[tuple[str, Union[str, None]]]) -> None:
            if tag == "meta" and attrs[0][1] == "zybooks-web/config/environment":
                self.data = json.loads(parse.unquote(attrs[1][1]))['APP']['BUILDKEY']
    p = Parser()
    p.feed(session.get("https://learn.zybooks.com").text)
    #print(p.data)
    return p.data

def checksmsgen(activity_id, ts, auth, part): #CHECKSUMSHIT
    md5hash = hashlib.md5()
    data = f"content_resource/{activity_id}/activity{ts}{auth}{activity_id}{part}true{getbuild()}"
    md5hash.update(data.encode("utf-8"))
    return md5hash.hexdigest()

def solveproblem(activity_id, auth, part, bookcode, section_id):
    url = (f"https://zyserver.zybooks.com/v1/content_resource/{activity_id}/activity")
    print(url)
    header ={
        "Host": "zyserver.zybooks.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://learn.zybooks.com",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://learn.zybooks.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
        }
    committimefraud(auth, section_id, activity_id, part, bookcode)
    ts = timespoof()
    chksm = checksmsgen(activity_id, ts, auth, part)
    #print(chksm)
    meta = {"isTrusted\\":True, "computerTime\\":ts+"\\"} #maybe not necesary?
    return session.post(url, json={"part": part,"complete": True,"metadata": "{}","zybook_code":bookcode,"auth_token":auth,"timestamp":ts,"__cs__":chksm}, headers=header).json()

def solveall(section, bookcode, chapter, auth):
    section_id = section["canonical_section_id"]
    print (f"solving section {chapter['number']}.{section['number']}")
    problems = getactivities(bookcode, chapter["number"], section["number"], auth)
    print(section)
    p = 1
    for problem in problems:
        activity_id = problem["id"]
        parts = problem["parts"]
        if parts > 0:
            for part in range(parts):
                if solveproblem(activity_id, auth, part, bookcode, section_id):
                    print(f"Solved part {part+1} of problem {p}")
                else:
                    print(f"Failed to solve part {part+1} of problem {p}")
        else:
            if solveproblem(activity_id, auth, 0, bookcode, section_id):
                print(f"Solved problem {p}")
            else:
                print(f"Failed to solve problem {p}")
        p+=1
