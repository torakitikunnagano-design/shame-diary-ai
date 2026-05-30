from html import escape
from views.html_templates import page_html


def result_html(
    cast_name,
    evaluation,
    char_count,
    good_html,
    bad_html,
    title_html,
    result
):
    return page_html(f"""
        <div class="badge">AI Result</div>
        <h1>採点結果</h1>

        <p style="color:#ff9ad2;">
            キャスト名：{escape(cast_name)}
        </p>

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
            <div class="rewrite">
                {escape(result.get("rewrite_example", ""))}
            </div>
        </div>

        <br>

        <a href="/">← ホームへ戻る</a>
    """)