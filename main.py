import pymongo

from fastapi import FastAPI, Response



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["admin"]
mycol = mydb["team"]
mydict = { "team_name": "Abizov", "first_try": "112", "second_try": "0", "best_try": "0" }

x = mycol.insert_one(mydict)


app = FastAPI()




@app.get("/teams")
async def root(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"

    resuls = list(mycol.find({}, {'_id': False}))
    final_results = []
    for i in range(len(resuls)):
        resuls[i]['best_try'] = resuls[i]['first_try'] if resuls[i]['first_try'] < resuls[i]['second_try'] else resuls[i]['second_try']

    newlist = sorted(resuls, key=lambda d: d['best_try']) 

    for i in range(len(newlist)):
        newlist[i]["id"] = i+1



    print(newlist)

    
    return {"results": resuls}