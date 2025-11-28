import logging
import os
import pyrebase
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

log = logging.getLogger(__name__)
log.info("Starting API server...")
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DB_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MSG_SENDER"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

print("Firebase config:", config)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


class UserCredentials(BaseModel):
    email: str
    password: str

class PresetData(BaseModel):
    preset_id: str
    preset_data: str


def verify_token(token: str):
    try:
        user = auth.get_account_info(token)
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.post("/signup")
def sign_up(request: Request, credentials: UserCredentials):
    try:
        user = auth.create_user_with_email_and_password(credentials.email, credentials.password)
        request.state.user = user
        log.info(f"User created: {user['localId']}")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/signin")
def sign_in(request: Request, credentials: UserCredentials):
    try:
        user = auth.sign_in_with_email_and_password(credentials.email, credentials.password)
        request.state.user = user
        log.info(f"User signed in: {user['localId']}")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/save_preset")
def save_preset(request: Request, data: PresetData):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    id_token = auth_header.split(" ", 1)[1]
    try:
        info = verify_token(id_token)
        user_record = info["users"][0]
        uid = user_record["localId"]

        db.child("presets").child(uid).child(data.preset_id).set(
            data.preset_data,
            id_token
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request, token: str | None = Query(default=None)):
    user_is_authenticated = False
    presets_data = {}
    if token:
        user = verify_token(token)
        authenticated_user = user.get('users', [])[0]
        user_is_authenticated = True
    user_email = authenticated_user.get("email") if user_is_authenticated else ""
    if user_is_authenticated:
        user_id = authenticated_user.get("localId")
        presets = db.child("presets").child(user_id).get(token)
        if presets.each():
            presets_data = {p.key(): p.val() for p in presets.each()}
        return templates.TemplateResponse(
            request=request, name="presets.html", context={
                "user_is_authenticated": user_is_authenticated,
                "user_email": user_email,
                "presets": presets_data
            }
        )
    else:
        return templates.TemplateResponse(
            request=request, name="login.html"
        )

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html")

@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse(
        request=request, name="signup.html")

@app.get("/add_preset", response_class=HTMLResponse)
async def add_preset(request: Request):
    return templates.TemplateResponse(
        request=request, name="preset_form.html")