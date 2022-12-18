import pymongo
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path
from typing import Union

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn


def serve_react_app(app: FastAPI, build_dir: Union[Path, str]) -> FastAPI:
    """Serves a React application in the root directory `/`

    Args:
        app: FastAPI application instance
        build_dir: React build directory (generated by `yarn build` or
            `npm run build`)

    Returns:
        FastAPI: instance with the react application added
    """
    if isinstance(build_dir, str):
        build_dir = Path(build_dir)

    app.mount(
        "/static/",
        StaticFiles(directory=build_dir / "static"),
        name="React App static files",
    )
    templates = Jinja2Templates(directory=build_dir.as_posix())

    @app.get("/{full_path:path}")
    async def serve_react_app(request: Request, full_path: str):
        """Serve the react app
        `full_path` variable is necessary to serve each possible endpoint with
        `index.html` file in order to be compatible with `react-router-dom
        """
        return templates.TemplateResponse("index.html", {"request": request})

    return app

class Team(BaseModel):
    name: str
    time: int

class TeamName(BaseModel):
    name: str
    

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["admin"]
mycol = mydb["team"]

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:80",
    "*",
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
    only_show_resuls = []
    for i in range(len(resuls)):
        try:
            if resuls[i]['show'] == 1:
                only_show_resuls.append(resuls[i])
        except Exception as e:
            pass

    for i in range(len(only_show_resuls)):
        only_show_resuls[i]['best_try'] = only_show_resuls[i]['first_try'] if only_show_resuls[i]['first_try'] < only_show_resuls[i]['second_try'] else only_show_resuls[i]['second_try']
    newlist = sorted(only_show_resuls, key=lambda d: d['best_try']) 
    for i in range(len(newlist)):
        newlist[i]["id"] = i+1
    return {"results": newlist}


@app.post("/team/first_try")
async def add_team(team: Team):
    upsertable_data = {"first_try": team.time, "second_try": 0, "best_try": 0, "show": 1}
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


@app.post("/team/hide")
async def delete_team(team: TeamName):
    upsertable_data = {"show": 0}
    mycol.update_one({'team_name': team.name}, {"$set": upsertable_data}, upsert=True)
    return {"status": "200"}


@app.post("/team/show")
async def delete_team(team: TeamName):
    upsertable_data = {"show": 1}
    mycol.update_one({'team_name': team.name}, {"$set": upsertable_data}, upsert=True)
    return {"status": "200"}


@app.post("/timer/start")
async def start_timer():
    mycol = mydb["timer"]
    upsertable_data = {"status": 1}
    mycol.update_one({"timer": "main"}, {"$set": upsertable_data}, upsert=True)
    return {"status": "200"}


@app.post("/timer/stop")
async def start_timer():
    mycol = mydb["timer"]
    upsertable_data = {"status": 0}
    mycol.update_one({"timer": "main"}, {"$set": upsertable_data}, upsert=True)
    return {"status": "200"}


@app.get("/timer/status")
async def get_timer_status():
    mycol = mydb["timer"]
    cur = mycol.find_one({'timer': "main"})
    return {"timer": cur["status"]}


path_to_react_app_build_dir = "./static"
app = serve_react_app(app, path_to_react_app_build_dir)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)