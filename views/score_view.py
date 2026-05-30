from views.html_templates import page_html

def score_form_html(cast_name=""):

    html = page_html("""
        <div class="badge">AI Diary Coach</div>
        <h1>写メ日記AI採点</h1>
        <p class="sub">本文と画像を入れると、AIが総合的に採点します。</p>

        <form action="/score" method="post" enctype="multipart/form-data">
            <textarea
                id="diary"
                name="diary"
                placeholder="ここに写メ日記の本文を入力してください"
                oninput="updateCount()"
            ></textarea>

            <p style="color:#ff9ad2;margin-top:10px;">
                現在の文字数：<span id="charCount">0</span>文字
            </p>

            <input
                type="file"
                name="photo"
                accept="image/*"
                onchange="previewImage(event)"
            >

            <img
                id="preview"
                style="
                    display:none;
                    width:100%;
                    max-height:420px;
                    object-fit:contain;
                    margin-top:18px;
                    border-radius:18px;
                    border:1px solid rgba(255,255,255,.15);
                    background:#111;
                "
            >

            <button type="submit">AI採点する</button>
        </form>

        <script>
        function updateCount() {
            const diary = document.getElementById("diary");
            const count = document.getElementById("charCount");
            count.textContent = diary.value.length;
        }

        function previewImage(event) {
            const file = event.target.files[0];
            const preview = document.getElementById("preview");

            if (!file) {
                preview.style.display = "none";
                preview.src = "";
                return;
            }

            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
        }
        </script>
    """)
    return html.replace("__CAST_NAME__", cast_name)