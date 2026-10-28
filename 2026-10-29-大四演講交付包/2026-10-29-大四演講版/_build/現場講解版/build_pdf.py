# -*- coding: utf-8 -*-
"""把《現場講解版.html》裡的 43 頁投影片轉成一份 PDF（只有投影片，沒有講稿）。

用法：python build_pdf.py <演講版資料夾>   （不要加 -I，核對與 35 頁版要用 PyMuPDF）
產出：<演講版資料夾>/2026-10-29-大四演講投影片.pdf（43 頁）
　　　<演講版資料夾>/2026-10-29-大四演講投影片_正式版35頁.pdf（給校方，不含附錄與預備示例）

做法：抽出每一頁 <section class="slide">，去掉講者註記，排成一頁一張 1280×720 的列印頁，
再叫 Chrome（沒有就用 Edge）無頭模式印成 PDF。字型會一起嵌進 PDF，別台電腦看也一樣。
"""
import pathlib
import re
import subprocess
import sys
import tempfile

folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2]).resolve()
src = folder / "現場講解版.html"
out = folder / "2026-10-29-大四演講投影片.pdf"
html_text = src.read_text(encoding="utf-8")

# ---------- 1. 抽出 CSS 與每一頁 ----------
style = re.search(r"<style>(.*?)</style>", html_text, re.S).group(1)
# 圖片在網頁裡是開頁後由 JS 填進 <img data-img>，這裡先把 base64 直接塞回 src
IMG = dict(re.findall(r"(\w+):'(data:image/[^']+)'", re.search(r"const IMG=\{(.*?)\};", html_text, re.S).group(1)))
assert set(IMG) == {"horse", "chart"}, IMG.keys()
slides = {}
for m in re.finditer(r'<section class="slide[^"]*" data-no="(\d+)"[^>]*>(.*?)</section>', html_text, re.S):
    no, body = int(m.group(1)), m.group(2)
    body = re.sub(r'<aside class="notes"[^>]*>.*?</aside>', "", body, flags=re.S)
    body = re.sub(r'data-img="(\w+)"', lambda i: f'src="{IMG[i.group(1)]}"', body)
    slides[no] = body
assert 'data-img=' not in "".join(slides.values())
assert sorted(slides) == list(range(1, 44)), f"頁數不對：{sorted(slides)}"

# ---------- 2. 組成列印專用頁 ----------
PRINT_CSS = """
@page{size:1280px 720px;margin:0}
html,body{margin:0;padding:0;height:auto;overflow:visible;background:#fff;width:1280px}
*{animation:none!important;transition:none!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.stage{position:relative;left:auto;top:auto;transform:none;width:1280px;height:720px;overflow:hidden;break-after:page;page-break-after:always}
.stage:last-child{break-after:auto;page-break-after:auto}
.slide{display:block;position:absolute;inset:0}
"""
pages = "\n".join(
    f'<div class="stage"><section class="slide active" data-no="{no}">{slides[no]}</section></div>'
    for no in range(1, 44)
)
print_html = (
    '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
    "<title>AI 時代企業行銷策略｜投影片</title>"
    f"<style>{style}</style><style>{PRINT_CSS}</style></head><body>{pages}</body></html>"
)

# ---------- 3. 叫瀏覽器印成 PDF ----------
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
browser = next((b for b in BROWSERS if pathlib.Path(b).exists()), None)
assert browser, "找不到 Chrome 或 Edge"

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    page_file = tmp / "print.html"
    page_file.write_text(print_html, encoding="utf-8")
    cmd = [
        browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--user-data-dir={tmp / 'profile'}",
        "--no-pdf-header-footer",  # 別加 --virtual-time-budget／--run-all-compositor-stages-before-draw，會卡住不結束
        f"--print-to-pdf={out}", page_file.as_uri(),
    ]
    if out.exists():
        out.unlink()
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        p.wait(timeout=120)
    except subprocess.TimeoutExpired:
        p.kill()  # Chrome 有時印完 PDF 卻不結束；PDF 有產生就照用
    if not out.exists() or out.stat().st_size < 100_000:
        raise SystemExit("PDF 沒有產生")

# ---------- 4. 核對（PyMuPDF 裝在使用者套件區，python -I 看不到，跳過就手動翻一遍） ----------
try:
    import fitz  # PyMuPDF
except ImportError:
    print(f"已產生 {out}（{out.stat().st_size/1e6:.1f} MB），沒裝 PyMuPDF 所以跳過核對")
    raise SystemExit(0)

doc = fitz.open(out)
w, h = doc[0].rect.width, doc[0].rect.height
text = "".join(p.get_text() for p in doc)
print(f"已產生 {out.name}：{len(doc)} 頁，每頁 {w/72:.2f}×{h/72:.2f} 英寸，{out.stat().st_size/1e6:.1f} MB")
assert len(doc) == 43, "頁數不是 43"
assert abs(w / h - 16 / 9) < .01, "不是 16:9"
assert "志宏老師" in text and "Zell" not in text, "署名不對"
blank = [i + 1 for i, p in enumerate(doc) if len(p.get_text().strip()) < 4]
if blank:
    print("  [核對] 幾乎沒有文字的頁：", blank)
imgs = {i + 1: len(p.get_images()) for i, p in enumerate(doc) if p.get_images()}
assert imgs.get(5) and imgs.get(27), f"第 5／27 頁的圖片沒進 PDF：{imgs}"

# ---------- 5. 給校方的版本：只留正式 1–35 頁，附錄與預備示例不給 ----------
out34 = folder / "2026-10-29-大四演講投影片_正式版35頁.pdf"
sub = fitz.open()
sub.insert_pdf(doc, from_page=0, to_page=34)
sub.save(out34, garbage=4, deflate=True)
print(f"已產生 {out34.name}：{len(sub)} 頁，{out34.stat().st_size/1e6:.1f} MB")
