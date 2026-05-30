import os
import base64
from html import escape

import requests
from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from openai import OpenAI

from services.ai_service import analyze_diary
from views.html_templates import page_html
from views.login_view import login_html, login_error_html
from views.history_view import history_html
from views.home_view import dashboard_html
from views.score_view import score_form_html
from views.result_view import result_html

load_dotenv()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "temporary-secret-key")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/login", response_class=HTMLResponse)
def login_page():
    return login_html()


@app.post("/login", response_class=HTMLResponse)
def login(login_id: str = Form(...), password: str = Form(...)):

    if (
        login_id == os.getenv("STAFF_ID")
        and password == os.getenv("STAFF_PASSWORD")
    ):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="logged_in", value="true")
        response.set_cookie(key="role", value="staff")
        return response

    if (
        login_id == os.getenv("CAST_ID")
        and password == os.getenv("CAST_PASSWORD")
    ):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="logged_in", value="true")
        response.set_cookie(key="role", value="cast")
        response.set_cookie(key="cast_name", value=login_id)
        return response

    return login_error_html()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    if request.cookies.get("logged_in") != "true":
        return RedirectResponse("/login", status_code=302)

    role = request.cookies.get("role", "cast")
    return dashboard_html(role)


@app.get("/score-form", response_class=HTMLResponse)
def score_form(request: Request):

    if request.cookies.get("logged_in") != "true":
        return RedirectResponse("/login", status_code=302)

    return score_form_html()


@app.post("/score", response_class=HTMLResponse)
async def score(
    cast_name: str = Form("未入力"),
    diary: str = Form(""),
    photo: UploadFile | None = File(default=None)
):
    diary = diary.strip()
    cast_name = cast_name.strip() or "未入力"

    if not diary and (not photo or not photo.filename):
        return page_html("""
            <div class="badge">Error</div>
            <h1>エラー</h1>
            <p>本文か画像のどちらかを入力してください。</p>
            <br>
            <a href="/">← 戻る</a>
        """)

    photo_base64 = None
    photo_type = "image/jpeg"

    if photo is not None:
        photo_bytes = await photo.read()

        if photo.filename and len(photo_bytes) > 0:
            photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
            photo_type = photo.content_type or "image/jpeg"

    try:
        result = analyze_diary(
            cast_name=cast_name,
            diary=diary,
            photo_base64=photo_base64,
            photo_type=photo_type
        )

    except Exception as e:
        result = {
            "score": 0,
            "rank": "ERROR",
            "good_points": [],
            "bad_points": [f"エラー内容: {str(e)}"],
            "title_ideas": [],
            "rewrite_example": "",
            "girl_advice": "設定か画像処理でエラーが出ています。",
            "staff_advice": "",
            "type_analysis": "",
            "image_advice": ""
        }

    char_count = len(diary)

    good_html = "".join([f"<li>{escape(x)}</li>" for x in result.get("good_points", [])])
    bad_html = "".join([f"<li>{escape(x)}</li>" for x in result.get("bad_points", [])])
    title_html = "".join([f"<li>{escape(x)}</li>" for x in result.get("title_ideas", [])])

    try:
        score_value = int(str(result.get("score", 0)).replace("点", "").strip())
    except Exception:
        score_value = 0

    if score_value >= 95:
        evaluation = "良い"
    elif score_value >= 85:
        evaluation = "普通"
    else:
        evaluation = "改善"

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if supabase_url and supabase_key:
        requests.post(
            f"{supabase_url}/rest/v1/diary_scores",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "cast_name": cast_name,
                "diary": diary,
                "evaluation": evaluation,
                "score": score_value,
                "type_analysis": result.get("type_analysis"),
                "good_points": result.get("good_points"),
                "bad_points": result.get("bad_points"),
                "title_ideas": result.get("title_ideas"),
                "rewrite_example": result.get("rewrite_example"),
                "girl_advice": result.get("girl_advice"),
                "staff_advice": result.get("staff_advice"),
                "image_advice": result.get("image_advice")
            }
        )

    return result_html(
    cast_name,
    evaluation,
    char_count,
    good_html,
    bad_html,
    title_html,
    result
)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("logged_in")
    response.delete_cookie("role")
    response.delete_cookie("cast_name")
    return response

@app.get("/history", response_class=HTMLResponse)
def history(request: Request):

    if request.cookies.get("logged_in") != "true":
        return RedirectResponse("/login", status_code=302)

    if request.cookies.get("role") != "staff":
        return RedirectResponse("/", status_code=302)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    rows_html = ""

    if supabase_url and supabase_key:
        response = requests.get(
            f"{supabase_url}/rest/v1/diary_scores?select=*",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}"
            }
        )

        data = response.json()

        for row in reversed(data):
            rows_html += f"""
            <div class="mini" style="margin-bottom:18px;">
                <h2>{escape(str(row.get("cast_name", "未入力")))}</h2>
                <p><strong>評価:</strong> {escape(str(row.get("evaluation", "")))}</p>
                <p><strong>タイプ:</strong> {escape(str(row.get("type_analysis", "")))}</p>
                <div class="rewrite">
                    {escape(str(row.get("diary", "")))}
                </div>
            </div>
            """

    return history_html(rows_html)