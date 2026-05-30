from views.html_templates import page_html


def dashboard_html(role):
    history_button = ""

    if role == "staff":
        history_button = """
        <a class="app-button" href="/history">
            <div class="app-icon">📊</div>
            <div>採点履歴</div>
        </a>
        """

    return page_html(f"""
        <div class="badge">Dashboard</div>
        <h1>ホーム</h1>
        <p class="sub">使いたい機能を選んでください。</p>

        <div class="app-grid">
            <a class="app-button" href="/score-form">
                <div class="app-icon">📝</div>
                <div>AI採点</div>
            </a>

            {history_button}

            <a class="app-button" href="/login">
                <div class="app-icon">🔐</div>
                <div>ログイン</div>
            </a>

            <a class="app-button" href="/logout">
                <div class="app-icon">🚪</div>
                <div>ログアウト</div>
            </a>
        </div>
    """)