from views.html_templates import page_html


def history_html(rows_html):
    return page_html(f"""
        <div class="badge">History</div>

        <h1>採点履歴</h1>

        {rows_html}

        <br>

        <a href="/">← 戻る</a>
    """)