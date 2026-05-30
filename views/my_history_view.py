from views.html_templates import page_html


def my_history_html(rows_html):
    return page_html(f"""
        <div class="badge">My History</div>

        <h1>自分の履歴</h1>
        <p><strong>日時:</strong> {rows_html.get("created_at", "")}</p>

        {rows_html}

        <br>

        <a href="/">← ホームへ戻る</a>
    """)