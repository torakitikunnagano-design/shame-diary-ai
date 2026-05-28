from views.html_templates import page_html


def login_html():
    return page_html("""
        <div class="badge">Login</div>
        <h1>ログイン</h1>

        <form action="/login" method="post">
            <input type="password" name="password" placeholder="パスワード">
            <button type="submit">ログイン</button>
        </form>
    """)


def login_error_html():
    return page_html("""
        <div class="badge">Error</div>
        <h1>ログイン失敗</h1>

        <p>パスワードが違います。</p>

        <br>

        <a href="/login">← 戻る</a>
    """)