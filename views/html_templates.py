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
.badge {{
    display:inline-block;
    background:rgba(255,77,166,.18);
    color:#ff9ad2;
    padding:7px 14px;
    border-radius:999px;
    font-size:13px;
}}

h1 {{
    font-size:34px;
}}

.sub {{
    color:#cfc3d8;
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

.rewrite {{
    white-space:pre-wrap;
    line-height:1.8;
}}

a {{
    color:#ff8ccc;
    font-weight:bold;
    text-decoration:none;
}}
.app-grid {{
    display:grid;
    grid-template-columns:repeat(2, 1fr);
    gap:18px;
    margin-top:24px;
}}

.app-button {{
    display:block;
    text-align:center;
    background:#11111a;
    border:1px solid rgba(255,255,255,.12);
    border-radius:22px;
    padding:24px 12px;
    color:white;
    text-decoration:none;
}}

.app-icon {{
    font-size:42px;
    margin-bottom:10px;
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