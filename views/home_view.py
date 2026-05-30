from views.html_templates import page_html


def dashboard_html(role, stats_html=""):
    staff_buttons = ""
    cast_buttons = ""

    if role == "staff":
        staff_buttons = """
        <a class="app-button" href="/history">
            <div class="app-icon">📊</div>
            <div>全履歴</div>
        </a>
        """

    if role == "cast":
        cast_buttons = """
        <a class="app-button" href="/my-history">
            <div class="app-icon">📖</div>
            <div>自分の履歴</div>
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

            {staff_buttons}
            {cast_buttons}
            {stats_html}
            <a class="app-button" href="/logout">
                <div class="app-icon">🚪</div>
                <div>ログアウト</div>
            </a>
        </div>
    """)