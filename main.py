import os
import json
import base64
from fastapi import Request
from services.ai_service import analyze_diary
from views.login_view import login_html, login_error_html
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from html import escape
import requests
from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from openai import OpenAI
from views.html_templates import page_html

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

@app.post("/login")
def login(password: str = Form(...)):

    if password == os.getenv("APP_PASSWORD"):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="logged_in", value="true")
        return response

    return login_error_html()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    if request.cookies.get("logged_in") != "true":
        return RedirectResponse("/login", status_code=302)
    return page_html("""
        <div class="badge">AI Diary Coach</div>
        <h1>写メ日記AI採点</h1>
        <p class="sub">本文と画像を入れると、AIが総合的に採点します。</p>

        <form action="/score" method="post" enctype="multipart/form-data">
            <input type="text" name="cast_name" placeholder="キャスト名">

            <textarea
                id="diary"
                name="diary"
                placeholder="ここに写メ日記の本文を入力してください"
                oninput="updateCount()"
            ></textarea>

            <p style="color:#ff9ad2;margin-top:10px;">
                現在の文字数：<span id="charCount">0</span>文字
            </p>

            <input
                type="file"
                name="photo"
                accept="image/*"
                onchange="previewImage(event)"
            >

            <img
                id="preview"
                style="
                    display:none;
                    width:100%;
                    max-height:420px;
                    object-fit:contain;
                    margin-top:18px;
                    border-radius:18px;
                    border:1px solid rgba(255,255,255,.15);
                    background:#111;
                "
            >

            <button type="submit">AI採点する</button>
        </form>

        <script>
        function updateCount() {
            const diary = document.getElementById("diary");
            const count = document.getElementById("charCount");
            count.textContent = diary.value.length;
        }

        function previewImage(event) {
            const file = event.target.files[0];
            const preview = document.getElementById("preview");

            if (!file) {
                preview.style.display = "none";
                preview.src = "";
                return;
            }

            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
        }
        </script>
    """)


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
            div class = "badge">Error</div>
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

#採点基準
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
        score = int(str(result.get("score", 0)).replace("点", "").strip())
    except Exception:
        score = 0

    if score >= 95:
        evaluation = "良い"
    elif score >= 85:
        evaluation = "普通"
    else:
        evaluation = "改善"

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    db_status = "未実行"
    db_text = ""

    if supabase_url and supabase_key:
        response_db = requests.post(
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
            "score": score,
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
            
        db_status = response_db.status_code
        db_text = response_db.text

    else:
        db_status = "SUPABASE_URL または UPABESE_KEY が未設定です。"

    return page_html(f"""
            <div class="badge">AI Result</div>
            <h1>採点結果</h1>

            <p style="color:#ff9ad2;">キャスト名：{escape(cast_name)}</p>

            <div class="score-box">
                <div class="score">{evaluation}</div>
                <p>文字数: {char_count}文字</p>
            </div>

            <div class="grid">
                <div class="mini">
                    <h2>良い点</h2>
                    <ul>{good_html}</ul>
                </div>

                <div class="mini">
                    <h2>改善点</h2>
                    <ul>{bad_html}</ul>
                </div>

                <div class="mini">
                    <h2>タイトル案</h2>
                    <ul>{title_html}</ul>
                </div>

                <div class="mini">
                    <h2>女の子への声かけ</h2>
                    <p>{escape(result.get("girl_advice", ""))}</p>
                </div>

                <div class="mini">
                    <h2>スタッフ向け指導</h2>
                    <p>{escape(result.get("staff_advice", ""))}</p>
                </div>

                <div class="mini">
                    <h2>タイプ分析</h2>
                    <p>{escape(result.get("type_analysis", ""))}</p>
                </div>

                <div class="mini">
                    <h2>画像アドバイス</h2>
                    <p>{escape(result.get("image_advice", ""))}</p>
                </div>

            </div>

            <div class="mini" style="margin-top:18px;">
                <h2>改善例</h2>
                <div class="rewrite">{escape(result.get("rewrite_example", ""))}</div>
            </div>

            <br>
            <a href="/">← もう一度採点する</a>
        """)