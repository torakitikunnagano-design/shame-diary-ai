from views.html_templates import page_html


def my_history_html(rows_html):
    return page_html(f"""
        <div class="badge">My History</div>

        <h1>自分の履歴</h1>

        {rows_html}

        <br>

        <a href="/">← ホームへ戻る</a>
    """)