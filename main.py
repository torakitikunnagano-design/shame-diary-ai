import os
import json
import base64
from html import escape
import requests
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def page_html(content):
    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>写メ日記AI採点</title>
<style>
body {{
    margin:0;
    min-height:100vh;
    background:linear-gradient(135deg,#090910 0%,#140b1f 45%,#1c1024 100%);
    background-attachment:fixed;
    background-repeat:no-repeat;
    background-size:cover;
    color:white;
    font-family:"Segoe UI",sans-serif;
}}
.wrap {{
    max-width:960px;
    margin:auto;
    padding:40px 20px;
}}
.card {{
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:24px;
    padding:30px;
    box-shadow:0 20px 60px rgba(0,0,0,.4);
}}
.badge {{
    display:inline-block;
    background:rgba(255,77,166,.18);
    color:#ff9ad2;
    padding:7px 14px;
    border-radius:999px;
    font-size:13px;
}}
h1 {{ font-size:34px; }}
.sub {{ color:#cfc3d8; }}
input, textarea {{
    width:100%;
    box-sizing:border-box;
    background:#101018;
    color:white;
    border:1px solid #333;
    border-radius:16px;
    padding:16px;
    font-size:16px;
    margin-top:14px;
}}
textarea {{
    height:240px;
    line-height:1.7;
}}
button {{
    margin-top:22px;
    width:100%;
    padding:18px;
    border:none;
    border-radius:999px;
    background:linear-gradient(90deg,#ff4da6,#ff7ac8);
    color:white;
    font-size:18px;
    font-weight:bold;
}}
.score-box {{
    text-align:center;
    background:linear-gradient(135deg,#ff4da6,#7c3cff);
    border-radius:24px;
    padding:30px;
    margin:25px 0;
}}
.score {{
    font-size:72px;
    font-weight:bold;
}}
.rank {{
    font-size:28px;
    font-weight:bold;
}}
.grid {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:18px;
}}
.mini {{
    background:#11111a;
    border:1px solid rgba(255,255,255,.1);
    border-radius:18px;
    padding:20px;
}}
.mini h2 {{
    color:#ff9ad2;
    font-size:20px;
}}
li {{
    margin-bottom:8px;
    line-height:1.7;
}}
.rewrite {{
    white-space:pre-wrap;
    line-height:1.8;
}}
a {{
    color:#ff8ccc;
    font-weight:bold;
    text-decoration:none;
}}
@media(max-width:700px){{
    .grid {{ grid-template-columns:1fr; }}
    .score {{ font-size:56px; }}
}}
</style>
</head>
<body>
<div class="wrap">
<div class="card">
{content}
</div>
</div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    print("DEBUG evaluation:", evaluation)
    print("DEBUG score:", score)
    print("DEBUG result:", result)
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
    diary: str = Form(...),
    photo: UploadFile = File(None)
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

    if photo and photo.filename:
        photo_bytes = await photo.read()
        photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
        photo_type = photo.content_type or "image/jpeg"

#採点基準
    prompt = f"""
あなたは写メ日記のAI教育スタッフです。
女の子を傷つけず、売上につながるように優しく改善してください。
画像が存在しない場合は、
画像アドバイスを「画像未入力」としてください。

文章と画像を総合的に採点してください。

必ずJSONだけで返してください。

形式:
{{
  "score": 85,
  "rank": "A",
  "good_points": ["良い点1", "良い点2"],
  "bad_points": ["改善点1", "改善点2"],
  "title_ideas": ["タイトル案1", "タイトル案2", "タイトル案3"],
  "rewrite_example": "改善後の写メ日記本文",
  "girl_advice": "女の子向けの優しいコメント",
  "staff_advice": "スタッフ向けの指導コメント",
  "type_analysis": "彼女感型。親近感が強み。",
  "image_advice": "画像に関する改善コメント"
}}

キャスト名:
{cast_name}

写メ日記:
{diary}
"""

    content = [
        {
            "type": "input_text",
            "text": prompt
        }
    ]

    if photo_base64:
        content.append({
            "type": "input_image",
            "image_url": f"data:{photo_type};base64,{photo_base64}"
        })

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=0.4
        )

        text = response.output_text
        text = text.replace("```json", "").replace("```", "").strip()

        result = json.loads(text)
        score = int(result.get("score", 0))

        if score >= 95:
            evaluation = "良い"
        elif score >= 85:
            evaluation = "普通"
        else:
            evaluation = "改善"

        if not photo_base64:
            result["image_advice"] = "画像未入力"

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

    # supabase.table("diary_scores").insert({
    #     "cast_name": cast_name,
    #     "diary": diary,

    #     "evaluation": evaluation,
    #     "score": score,

    #     "type_analysis": result.get("type_analysis"),

    #     "good_points": result.get("good_points"),
    #     "bad_points": result.get("bad_points"),

    #     "title_ideas": result.get("title_ideas"),

    #     "rewrite_example": result.get("rewrite_example"),

    #     "girl_advice": result.get("girl_advice"),
    #     "staff_advice": result.get("staff_advice"),

    #     "image_advice": result.get("image_advice")
    # }).execute()


    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    db_status = "未実行"
    db_text = ""
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
        db_status = response.status_code
        db_text = response.text
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