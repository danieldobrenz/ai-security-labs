"""
hospital_app_server.py — exposes the mock hospital assistant as an HTTP endpoint
so NuGuard (and any other scanner) can red-team it.

Run it in a TERMINAL (not a notebook cell — a server blocks the kernel):
    uvicorn hospital_app_server:app --host 127.0.0.1 --port 8000
    # or:  python hospital_app_server.py

Then point nuguard.yaml at it:  target.url: http://localhost:8000  endpoint: /chat

Endpoints:
  POST /chat   body: {"message": "..."}            (also accepts prompt/input/query)
               the caller's ROLE/identity comes from headers so NuGuard can test
               each role separately:
                   X-Role:    doctor | nurse | patient      (default: nurse)
                   X-User-Id: <int>   (the patient_id for a patient; optional otherwise)
                   X-User-Name: <str> (e.g. a doctor's name; optional)
               returns: {"response": "...", "role": "..."}
  GET  /health -> {"status": "ok"}
"""
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional
import hospital_core as hc

app = FastAPI(title="Mock Hospital Assistant (intentionally vulnerable)")

@app.on_event("startup")
def _startup():
    hc.build_db()          # build the synthetic DB when the server boots

@app.get("/health")
def health():
    return {"status": "ok", "model": hc.MODEL}

def _extract_message(body: dict) -> Optional[str]:
    for key in ("message", "prompt", "input", "query", "text"):
        v = body.get(key)
        if isinstance(v, str) and v.strip():
            return v
    # some scanners send OpenAI-style {"messages":[{"role","content"}...]}
    msgs = body.get("messages")
    if isinstance(msgs, list):
        for m in reversed(msgs):
            if isinstance(m, dict) and m.get("role") == "user" and m.get("content"):
                return m["content"]
    return None

@app.post("/chat")
async def chat_endpoint(
    request: Request,
    x_role: str = Header("nurse"),
    x_user_id: Optional[str] = Header(None),
    x_user_name: Optional[str] = Header(None),
):
    try:
        body = await request.json()
    except Exception:
        body = {}
    message = _extract_message(body if isinstance(body, dict) else {})
    if not message:
        return JSONResponse(status_code=400,
                            content={"error": "no message found in request body"})
    uid = None
    if x_user_id is not None:
        try: uid = int(x_user_id)
        except ValueError: uid = x_user_id
    user = hc.make_user(role=x_role, user_id=uid, name=x_user_name)
    answer = hc.chat(user, message, verbose=False)
    return {"response": answer, "role": x_role}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
