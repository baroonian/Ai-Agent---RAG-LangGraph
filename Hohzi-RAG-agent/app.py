"""
رابط چت — گرِیدیو

مسیری که ایجنت طی کرده کنار هر جواب نشان داده می‌شود.
این همان «رصد» ایستگاه دوازدهم است: بدون دیدن قدم‌ها، دیباگ غیرممکن است.

تاریخچهٔ مکالمه هم به ایجنت داده می‌شود تا سؤال دوم بفهمد
سؤال اول دربارهٔ چه بود.

اجرا:
    python app.py
"""

import gradio as gr
from agent import ask

CSS = """
.rtl textarea, .rtl input { direction: rtl; text-align: right; }
.message { direction: rtl; text-align: right; }
footer { display: none !important; }
"""

NEMOONE = [
    "چانکینگ چیه؟",
    "وکتور دیتابیس چیه و چرا لازمه؟",
    "کانتکست ویندو یعنی چی؟",
    "پرامپت اینجکشن چیه؟",
    "لنگ‌گراف چیه؟",
    "قیمت دلار امروز چنده؟",
]


def _tabdil(tarikhche):
    """
    گرِیدیو تاریخچه را به شکل خودش می‌دهد.
    ما فقط نقش و متن را لازم داریم.
    """
    out = []
    if not tarikhche:
        return out
    for m in tarikhche:
        if isinstance(m, dict) and m.get("content"):
            out.append({"role": m.get("role", "user"), "content": str(m["content"])})
        elif isinstance(m, (list, tuple)) and len(m) == 2:
            if m[0]:
                out.append({"role": "user", "content": str(m[0])})
            if m[1]:
                out.append({"role": "assistant", "content": str(m[1])})
    return out


def pasokh(payam, tarikhche):
    try:
        javab, masir = ask(payam, _tabdil(tarikhche))
    except Exception as e:
        return f"خطا: {type(e).__name__} — {e}"

    khat = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(masir))
    return f"{javab}\n\n---\n**مسیر ایجنت:**\n\n{khat}"


with gr.Blocks(title="دستیار هژی") as demo:
    gr.Markdown("## دستیار هژی\nهر چیزی که توی ویدیوهای کانال گفته شده، ازم بپرس.")

    gr.ChatInterface(
        fn=pasokh,
        examples=NEMOONE,
        textbox=gr.Textbox(placeholder="سؤالت را بنویس ...", elem_classes="rtl"),
    )


if __name__ == "__main__":
    demo.launch(css=CSS, inbrowser=True)
import os
demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 10000)))
