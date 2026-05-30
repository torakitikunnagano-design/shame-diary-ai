from views.html_templates import page_html


def stats_card(good_count, normal_count, improve_count):
    return f"""
    <div class="mini">
        <h2>成長状況</h2>

        <p>🟢 良い：{good_count}回</p>
        <p>🟡 普通：{normal_count}回</p>
        <p>🔴 改善：{improve_count}回</p>
    </div>
    """