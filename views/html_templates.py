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