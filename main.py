import pymongo
from fastapi import FastAPI, Response
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

class Team(BaseModel):
    name: str
    time: int
    

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["admin"]
mycol = mydb["team"]

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/teams")
async def root():
    resuls = list(mycol.find({}, {'_id': False}))
    for i in range(len(resuls)):
        resuls[i]['best_try'] = resuls[i]['first_try'] if resuls[i]['first_try'] < resuls[i]['second_try'] else resuls[i]['second_try']
    newlist = sorted(resuls, key=lambda d: d['best_try']) 
    for i in range(len(newlist)):
        newlist[i]["id"] = i+1
    print(newlist)
    return {"results": resuls}


@app.post("/team/first_try")
async def add_team(team: Team):
    upsertable_data = {"first_try": team.time, "second_try": 0, "best_try": 0}
    mycol.update_one({'team_name': team.name}, {"$set": upsertable_data}, upsert=True)
    return {"status": "200"}

@app.post("/team/second_try")
async def add_team(team: Team):
    cur = mycol.find_one({'team_name': team.name})
    best_try = cur["first_try"]
    if team.time < best_try:
        best_try = team.time
    upsertable_data = {"second_try": team.time, "best_try": best_try}
    mycol.update_one({'team_name': team.name}, {"$set": upsertable_data}, upsert=True)
    return {"status": "200"}