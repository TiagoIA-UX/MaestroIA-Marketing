from fastapi import FastAPI, HTTPException
from maestroia.graphs.marketing_graph import build_marketing_graph
from maestroia.core.state import MaestroState

app = FastAPI(title="MaestroIA Marketing API")

graph = build_marketing_graph()

@app.post("/campaign/run")
async def run_campaign(state: MaestroState):
    try:
        result = graph.invoke(state)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
