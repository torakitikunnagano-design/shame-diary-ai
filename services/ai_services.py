import os
import json

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def make_prompt(cast_name, diary):
    return f"""
あなたは売上重視の写メ日記AI教育スタッフです。

風俗業界における
「会いたくなる感情」
「性的期待感」
「親近感」
「指名したくなる空気感」
を重視してください。

ただし露骨な規約違反ではなく、
売上につながる範囲で最大限魅力的に改善してください。

【重要視する項目】
・会いたくなるか
・エロ想像力
・彼女感
・指名導線
・感情の距離感

画像が存在しない場合は、
画像アドバイスを「画像未入力」としてください。

文章と画像を総合的に採点してください。

必ずJSONだけで返してください。

形式:
{{
  "score": 85,
  "rank": "A",
  "good_points": ["良い点1", "良い点2"],
  "bad_points": ["改善点1", "改善点2"],
  "title_ideas": ["タイトル案1", "タイトル案2", "タイトル案3"],
  "rewrite_example": "改善後の写メ日記本文",
  "girl_advice": "女の子向けの優しいコメント",
  "staff_advice": "スタッフ向けの指導コメント",
  "type_analysis": "彼女感型。親近感が強み。",
  "image_advice": "画像に関する改善コメント"
}}

キャスト名:
{cast_name}

写メ日記:
{diary}
"""


def analyze_diary(cast_name, diary, photo_base64=None, photo_type="image/jpeg"):
    prompt = make_prompt(cast_name, diary)

    content = [
        {
            "type": "input_text",
            "text": prompt
        }
    ]

    if photo_base64:
        content.append({
            "type": "input_image",
            "image_url": f"data:{photo_type};base64,{photo_base64}"
        })

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0.4
    )

    text = response.output_text or ""
    text = text.replace("```json", "").replace("```", "").strip()

    if not text:
        raise ValueError("AIの返答が空です。")

    result = json.loads(text)

    if not photo_base64:
        result["image_advice"] = "画像未入力"

    return result