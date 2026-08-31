"""
ساخت ایندکس — ایجنت هژی

فایل‌های ورد اسکریپت‌ها را می‌خواند، تکه‌تکه می‌کند، امبد می‌کند
و در کروما ذخیره می‌کند.

ساختار پوشه:
    scripts/
        هر فایل .docx یک ویدیو
    metadata.csv   (اختیاری ولی توصیه‌شده)
        file,title,url

اگر metadata.csv نباشد، اسم فایل به‌عنوان عنوان ویدیو استفاده می‌شود.

مهم: این مرحله چند دقیقه طول می‌کشد. روی دوربین اجرایش نکن.
قبل از ضبط بزنش، و در ویدیو فقط کدش را نشان بده.

اجرا:
    python ingest.py
"""

import csv
import os
import time
from pathlib import Path

from docx import Document as Docx
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from config import embedder, CHROMA_DIR, COLLECTION

SCRIPTS_DIR = Path("scripts")
META_CSV = Path("metadata.csv")
META_XLSX = Path("metadata.xlsx")

# اسکریپت گفتاری پاراگراف‌بندی طبیعی دارد، ولی تیتر ندارد.
# ۹۰۰ کاراکتر یعنی حدود یک دقیقه حرف — واحد معنایی خوبی است.
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

SEPARATORS = ["\n\n", "\n", "؟ ", ". ", "، ", " ", ""]


# اکسل روی ویندوز فارسی معمولا با cp1256 ذخیره می‌کند، نه یوتی‌اف-۸
ENCODINGS = ["utf-8-sig", "utf-8", "cp1256", "cp1252"]


def _read_text(path):
    """فایل را با هر کدگذاری که کار کند بخوان."""
    for enc in ENCODINGS:
        try:
            text = path.read_text(encoding=enc)
            if enc not in ("utf-8-sig", "utf-8"):
                print(f"  [!] metadata.csv با کدگذاری {enc} خوانده شد.")
            return text
        except (UnicodeDecodeError, LookupError):
            continue
    raise SystemExit("metadata.csv با هیچ کدگذاری خوانده نشد.")


def _rows_from_xlsx():
    """اکسل را مستقیم بخوان. هیچ مشکل کدگذاری‌ای ندارد."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise SystemExit("برای خواندن اکسل این را نصب کن:  pip install openpyxl")

    wb = load_workbook(META_XLSX, read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []

    header = [str(c).strip().lower() if c else "" for c in rows[0]]
    out = []
    for r in rows[1:]:
        if not any(r):
            continue
        out.append({header[i]: (str(r[i]).strip() if i < len(r) and r[i] else "")
                    for i in range(len(header))})
    print(f"metadata.xlsx خوانده شد — {len(out)} ردیف")
    return out


def _rows_from_csv():
    import io
    text = _read_text(META_CSV)
    first = text.splitlines()[0] if text.splitlines() else ""
    delim = ";" if first.count(";") > first.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    out = [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
           for row in reader]
    print(f"metadata.csv خوانده شد — {len(out)} ردیف")
    return out


def read_metadata():
    """اسم فایل → (عنوان ویدیو، لینک). اول اکسل، بعد سی‌اس‌وی."""
    if META_XLSX.exists():
        rows = _rows_from_xlsx()
    elif META_CSV.exists():
        rows = _rows_from_csv()
    else:
        print("فایل متادیتا نبود. اسم فایل به‌عنوان عنوان استفاده می‌شود.")
        return {}

    if rows and "file" not in rows[0]:
        raise SystemExit(
            "ستون file پیدا نشد.\n"
            f"ستون‌هایی که هست: {list(rows[0].keys())}\n"
            "سه ستون لازم است با همین اسم‌ها: file  title  url"
        )

    meta = {}
    for r in rows:
        name = r.get("file", "")
        if name:
            meta[name] = (r.get("title", ""), r.get("url", ""))
    return meta


def read_docx(path):
    doc = Docx(path)
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(parts)


def load_all():
    if not SCRIPTS_DIR.exists():
        raise SystemExit("پوشهٔ scripts پیدا نشد. بسازش و فایل‌های ورد را داخلش بگذار.")

    meta = read_metadata()
    files = sorted(SCRIPTS_DIR.glob("*.docx"))
    files = [f for f in files if not f.name.startswith("~$")]  # فایل موقت ورد

    if not files:
        raise SystemExit("هیچ فایل .docx در پوشهٔ scripts نیست.")

    docs = []
    for f in files:
        text = read_docx(f)
        if len(text) < 200:
            print(f"  [!] {f.name} تقریبا خالی است، رد شد.")
            continue

        title, url = meta.get(f.name, (f.stem, ""))
        if not title:
            title = f.stem

        docs.append(Document(
            page_content=text,
            metadata={"title": title, "url": url, "file": f.name},
        ))
        print(f"  {f.name}  →  {len(text.split()):,} کلمه  |  {title}")

    return docs


def main():
    print("=" * 60)
    print("  ساخت ایندکس اسکریپت‌های هژی")
    print("=" * 60)

    docs = load_all()
    print(f"\n{len(docs)} ویدیو خوانده شد.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,
    )
    chunks = splitter.split_documents(docs)

    # شمارهٔ تکه را نگه می‌داریم تا بعدا بشود به دقیقهٔ تقریبی نگاشتش
    per_video = {}
    for c in chunks:
        t = c.metadata["title"]
        per_video[t] = per_video.get(t, 0) + 1
        c.metadata["chunk"] = per_video[t]

    print(f"{len(chunks):,} تکه ساخته شد.")
    print(f"میانگین {len(chunks) / len(docs):.0f} تکه برای هر ویدیو.\n")

    print("در حال بارگذاری مدل امبدینگ ...")
    emb = embedder()

    if os.path.exists(CHROMA_DIR):
        print("ایندکس قبلی پاک می‌شود ...")
        import shutil
        shutil.rmtree(CHROMA_DIR)

    print("در حال امبد کردن. این مرحله چند دقیقه طول می‌کشد ...\n")
    t = time.time()

    store = Chroma(
        collection_name=COLLECTION,
        embedding_function=emb,
        persist_directory=CHROMA_DIR,
    )

    BATCH = 64
    for i in range(0, len(chunks), BATCH):
        store.add_documents(chunks[i:i + BATCH])
        done = min(i + BATCH, len(chunks))
        print(f"  {done:,} / {len(chunks):,}", end="\r", flush=True)

    dt = time.time() - t
    print(f"\n\nتمام شد در {dt / 60:.1f} دقیقه.")
    print(f"ایندکس در {CHROMA_DIR} ذخیره شد.")

    # یک تست سریع
    print("\n" + "-" * 60)
    print("تست بازیابی:")
    hits = store.similarity_search("امبدینگ چیست", k=3)
    for h in hits:
        print(f"  [{h.metadata['title']} — تکهٔ {h.metadata['chunk']}]")
        print(f"    {h.page_content[:90]} ...")


if __name__ == "__main__":
    main()
