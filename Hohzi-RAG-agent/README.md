# Hozhi RAG Agent

A Persian-speaking RAG agent built with LangGraph that answers **only from your own data**, cites its sources, and honestly **admits when it doesn't know** — instead of hallucinating. Free, local, and beginner-friendly.

> 🎥 This repo is the companion code for the video tutorial on building an AI agent from scratch.

**[فارسی را پایین‌تر بخوانید ↓](#راهنمای-فارسی)**

---

## What makes this an agent, not a workflow

A plain RAG pipeline is a straight line: question → retrieve → answer. This agent makes real decisions:

1. **Retrieve** from a local vector database.
2. **Self-grade** — a model judges whether the retrieved chunks actually answer the question.
3. **Rewrite & loop** — if not, it rewrites the query and searches again (max 2 tries).
4. **Admit & fall back** — if it still can't answer, it says so honestly, then searches the web.

It has two real tools (the archive and the web), a loop, and it judges its own output. That's what makes it an agent.

## Features

- 🎯 Answers grounded in your documents, with source citations
- 🔁 Self-correcting retrieval loop with a hard iteration cap
- 🧠 Conversation memory (follow-up questions work)
- 🛡️ Prompt-injection guardrails (3 layers)
- 🌐 Falls back to web search when the archive has no answer
- ♻️ Model-failover chain — survives rate limits and dead endpoints
- 🇮🇷 Multilingual embeddings — works well with Persian text
- 💰 Fully free: free models, local embeddings, local database

## Stack

| Layer | Tool |
|---|---|
| Orchestration | LangGraph |
| LLM | NVIDIA Build (free tier) |
| Embeddings | BAAI/bge-m3 (local, CPU) |
| Vector DB | Chroma (local) |
| Web search | ddgs (DuckDuckGo) |
| UI | Gradio |

## Project structure

```
config.py       Model connection, failover chain, embeddings
ingest.py       Reads Word files → chunks → embeds → Chroma
agent.py        The LangGraph agent (6 nodes)
guard.py        3-layer prompt-injection guardrails
app.py          Gradio chat interface
requirements.txt
scripts/        ← put your own .docx files here
metadata.xlsx   ← optional: file, title, url
```

## Setup

**1. Clone and enter**
```bash
git clone <repo-url>
cd hozhi-rag-agent
```

**2. Virtual environment**
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate
```

**3. Install**
```bash
pip install -r requirements.txt
```

**4. Configure**

Copy `.env.example` to `.env` and add your free NVIDIA API key from [build.nvidia.com](https://build.nvidia.com):
```
NVIDIA_API_KEY=nvapi-xxxxxxxx
```

**5. Add your data**

Drop your `.docx` files into `scripts/`. Optionally add `metadata.xlsx` with columns `file`, `title`, `url` so answers can link back to sources.

## Run

```bash
# 1. Build the index (once, takes a few minutes)
python ingest.py

# 2. Launch the chat UI
python app.py
```

## Swapping models

All model names live in `.env`, not in the code. Because NVIDIA follows the OpenAI-compatible standard, switching providers is usually just changing `NVIDIA_BASE_URL` and the model names — the code stays untouched.

If a model gets deprecated, just edit `.env`. No code changes needed.

## Notes

- The NVIDIA free tier is rate-limited (~40 req/min). The agent handles this with exponential backoff and a model-failover chain.
- The free key is for personal/development use. Commercial use needs a license.
- Embeddings run locally on CPU — no rate limits, no expiry, works offline after the first download (~2.3 GB).

## License

MIT

---
---

<a name="راهنمای-فارسی"></a>

<div dir="rtl">

# دستیار هوش مصنوعی هژی (نسخهٔ فارسی)

یک ایجنت هوش مصنوعی فارسی‌زبان، ساخته‌شده با LangGraph، که **فقط از روی دیتای خودت** جواب می‌دهد، منبع هر جوابش را نشان می‌دهد، و هر جا نداند **صادقانه می‌گوید نمی‌دانم** — به‌جای اینکه از خودش دربیاورد. رایگان، لوکال، و مناسب مبتدی.

> 🎥 این کد، همراه ویدیوی آموزش ساخت ایجنت از صفر است.

## چرا این ایجنت است، نه ورک‌فلو

یک رگ ساده یک خط مستقیم است: سؤال ← بازیابی ← جواب. ولی این ایجنت واقعاً تصمیم می‌گیرد:

۱. **بازیابی** از وکتور دیتابیس لوکال.
۲. **داوری** — یک مدل قضاوت می‌کند که آیا تیکه‌های پیداشده واقعاً جواب سؤال را دارند.
۳. **بازنویسی و حلقه** — اگر نداشتند، سؤال را با کلمات دیگر می‌نویسد و دوباره می‌گردد (سقف: دو بار).
۴. **اعتراف و ابزار دوم** — اگر باز هم نشد، صادقانه می‌گوید بلد نیست، بعد می‌رود سراغ وب.

دو ابزار واقعی دارد (آرشیو و وب)، یک حلقه دارد، و روی خروجی خودش قضاوت می‌کند. همین یعنی ایجنت.

## امکانات

- 🎯 جواب از روی اسناد خودت، با ذکر منبع
- 🔁 حلقهٔ بازیابی خوداصلاح، با سقف تکرار مشخص
- 🧠 حافظهٔ مکالمه (سؤال دنباله‌دار کار می‌کند)
- 🛡️ محافظت در برابر پرامپت اینجکشن (سه لایه)
- 🌐 وقتی آرشیو جواب نداشت، می‌رود سراغ وب
- ♻️ زنجیرهٔ جایگزینی مدل — از ریت‌لیمیت و مرگ مدل جان سالم به در می‌برد
- 🇮🇷 امبدینگ چندزبانه — با متن فارسی خوب کار می‌کند
- 💰 کاملاً رایگان: مدل رایگان، امبدینگ لوکال، دیتابیس لوکال

## استک

| لایه | ابزار |
|---|---|
| ارکستریشن | LangGraph |
| مدل زبانی | NVIDIA Build (لایهٔ رایگان) |
| امبدینگ | BAAI/bge-m3 (لوکال، سی‌پی‌یو) |
| وکتور دیتابیس | Chroma (لوکال) |
| جست‌وجوی وب | ddgs |
| رابط کاربری | Gradio |

## ساختار پروژه

```
config.py       اتصال به مدل، زنجیرهٔ جایگزین، امبدینگ
ingest.py       خواندن فایل ورد ← چانکینگ ← امبدینگ ← کروما
agent.py        گراف لنگ‌گراف (شش گره)
guard.py        سه لایه گاردریل امنیتی
app.py          رابط چت گرِیدیو
requirements.txt
scripts/        ← فایل‌های ورد خودت را اینجا بگذار
metadata.xlsx   ← اختیاری: file, title, url
```

## نصب

**۱. کلون و ورود به پوشه**
```bash
git clone <repo-url>
cd hozhi-rag-agent
```

**۲. محیط مجازی**
```bash
python -m venv .venv
# ویندوز:
.\.venv\Scripts\Activate.ps1
# مک / لینوکس:
source .venv/bin/activate
```

**۳. نصب پکیج‌ها**
```bash
pip install -r requirements.txt
```

**۴. تنظیمات**

فایل `.env.example` را به `.env` تغییر نام بده و کلید رایگان انویدیا را از [build.nvidia.com](https://build.nvidia.com) بگیر و بگذار:
```
NVIDIA_API_KEY=nvapi-xxxxxxxx
```

**۵. دیتای خودت**

فایل‌های `.docx` را در پوشهٔ `scripts/` بریز. اگر خواستی، `metadata.xlsx` را با ستون‌های `file`، `title`، `url` بساز تا جواب‌ها به منبع لینک بخورند.

## اجرا

```bash
# ۱. ساخت ایندکس (یک بار، چند دقیقه طول می‌کشد)
python ingest.py

# ۲. اجرای رابط چت
python app.py
```

## عوض کردن مدل

اسم همهٔ مدل‌ها در `.env` است، نه در کد. چون انویدیا از استاندارد اوپن‌ای‌آی پیروی می‌کند، برای رفتن سراغ سرویس دیگر معمولاً فقط `NVIDIA_BASE_URL` و اسم مدل‌ها را عوض می‌کنی — کد دست‌نخورده می‌ماند.

اگر مدلی از دسترس خارج شد، فقط `.env` را عوض کن.

## نکته‌ها

- لایهٔ رایگان انویدیا ریت‌لیمیت دارد (حدود ۴۰ درخواست در دقیقه). ایجنت با عقب‌نشینی نمایی و زنجیرهٔ جایگزین مدل این را مدیریت می‌کند.
- کلید رایگان برای استفادهٔ شخصی و توسعه است. استفادهٔ تجاری به لایسنس نیاز دارد.
- امبدینگ لوکال روی سی‌پی‌یو اجرا می‌شود — بدون ریت‌لیمیت، بدون تاریخ انقضا، و بعد از دانلود اول (حدود ۲.۳ گیگ) آفلاین کار می‌کند.

## لایسنس

MIT

</div>
