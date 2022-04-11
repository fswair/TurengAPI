from fastapi import FastAPI, HTTPException
from main import Tureng

client = FastAPI()
@client.get("/search")
def tureng(query: str, selection: str):
    try:
        tureng = Tureng(query, selection, 1, 1, 0)
        print(tureng.get(0))
        if selection.lower() in tureng.types.keys():
            return {"word":{"request_url":tureng.request_url,"results":tureng.informations, "status":200, "related_words":tureng.get_related_words() if tureng.suggest_related_words else "Suggestions inactive..."}}
        else:
            return HTTPException("404", detail="Please give correct langcode..")
    except Exception as e:
        return HTTPException("404", detail="We don't find that word specified with langcode.")