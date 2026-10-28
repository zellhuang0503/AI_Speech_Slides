# -*- coding: utf-8 -*-
"""把 10/29 演講的投影片、講者提示、示範步驟、背景資料整併成單一 HTML。
原始檔一律只讀不改；輸出 現場講解版.html。"""
import base64, html, pathlib, re, sys

SRC = pathlib.Path(sys.argv[1])
OUT = SRC / "現場講解版.html"
esc = html.escape


def read(p):
    return (SRC / p).read_text(encoding="utf-8-sig")


# ---------- 1. 投影片 ----------
idx = read("index.html")
slides = re.findall(r'<section class="slide[^"]*" id="slide-(\d+)" aria-label="[^"]*">(.*?)</section>', idx, re.S)
assert len(slides) == 37, len(slides)
slide_html = {int(k): v for k, v in slides}
# 對外署名：教學場合用「志宏老師」（封面 1 處＋頁尾 21 處；示範對話裡的角色名 Zell 不動）
SIGN = re.compile(r"Zell[｜　]梵亞行銷顧問")
assert sum(len(SIGN.findall(v)) for v in slide_html.values()) == 22
# 示範對話的角色名也用「志宏老師」（第 8、9、14、15 頁共 6 處）
ROLE = re.compile(r"Zell ?(?=[給追修：])")
assert [k for k, v in slide_html.items() for _ in ROLE.findall(v)] == [8, 8, 9, 14, 14, 15]
# v2 起投影片改由 slides_v2.py 重新排版；原 index.html 只拿來核對「文字與數字沒有掉」
orig_lines = {}
for k, v in slide_html.items():
    v = ROLE.sub("志宏老師", SIGN.sub("志宏老師", v))
    assert "Zell" not in v, k
    lines = re.findall(r'<div class="text" style="([^"]*)">(.*?)</div>', v)
    orig_lines[k] = [html.unescape(re.sub(r"<br>", "", t)) for st, t in lines
                     if "top:32px" not in st and "left:1190px" not in st and "top:674px" not in st]

# ---------- 2. 要講的話：現場逐字稿（口語、可照念；講者提示.md 保留為原始備忘） ----------
md_notes = read("現場逐字稿.md")
parts = re.split(r"^## (\d+)｜(.+)$", md_notes, flags=re.M)
notes = {}
for i in range(1, len(parts), 3):
    no, title, body = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
    lines = [l.strip() for l in body.strip().split("\n") if l.strip()]
    time, rest = lines[0], lines[1:]
    notes[no] = {"title": title, "time": time, "lines": rest}
assert len(notes) == 38
assert all(re.match(r"\d\d:\d\d–\d\d:\d\d", notes[n]["time"]) for n in range(1, 36)), "正式頁第一行要是時間"
for n, v in notes.items():
    assert "Zell" not in "".join(v["lines"]), n

# 一行的三種寫法：【標籤】→ 小標；（…）整行 → 提醒（灰字，不念）；其餘 → 要念的話
def say_line(l):
    if l.startswith("【") and l.endswith("】"):
        return f'<h4 class="lbl">{esc(l[1:-1])}</h4>'
    if l.startswith("（") and l.endswith("）"):
        return f'<p class="cue">{esc(l)}</p>'
    return f"<p>{esc(l)}</p>"


# ---------- 3. 資料檔（簡易 markdown → HTML） ----------
NUM = re.compile(r"^[−\-]?[\d,\.]+%?元?$")

def table(rows):
    rows = [r for r in rows if not re.match(r"^\|[\s\-:|]+\|$", r)]
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    h = "<tr>" + "".join(f"<th>{esc(c)}</th>" for c in cells[0]) + "</tr>"
    b = "".join("<tr>" + "".join(f'<td{" class=num" if NUM.match(c) else ""}>{esc(c)}</td>' for c in r) + "</tr>" for r in cells[1:])
    return f'<div class="tw"><table><thead>{h}</thead><tbody>{b}</tbody></table></div>'

def md(text):
    out, lines, i = [], text.strip("\n").split("\n"), 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i]); i += 1
            out.append(table(rows)); continue
        for tag, pat in (("ul", r"^- "), ("ol", r"^\d+\. ")):
            if re.match(pat, l):
                items = []
                while i < len(lines) and re.match(pat, lines[i]):
                    items.append(re.sub(pat, "", lines[i])); i += 1
                out.append(f"<{tag}>" + "".join(f"<li>{esc(x)}</li>" for x in items) + f"</{tag}>")
                break
        else:
            if l.startswith("# "):
                out.append(f'<p class="src">{esc(l[2:])}</p>')
            elif l.startswith("## "):
                out.append(f"<h5>{esc(l[3:])}</h5>")
            elif l.strip():
                out.append(f"<p>{esc(l)}</p>")
            i += 1
    return "\n".join(out)

def section(text, head):
    """取 08 檔某個 ## 段落"""
    m = re.search(rf"^## {re.escape(head)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert m, head
    return m.group(1)

f01, f02, f03, f04, f05 = (read(f"示範資料/{n}") for n in (
    "01_初始品牌資料.md", "02_歷史活動與定義.md", "03_講者第二輪補充卡.md", "04_活動會議逐字稿.txt", "05_示範二起點方案.md"))
f06, f07, f08 = (read(f"示範資料/{n}") for n in ("06_示範一_新對話貼上包.txt", "07_示範二_新對話貼上包.txt", "08_標準參考輸出.md"))

SPEAKER_ONLY = ("講者分支：", "追問：", "參考判斷：")
# 第二輪貼給 AI 的只要店長確認；講者分支與參考判斷不能貼進去
card2_paste = "店長補充確認｜虛構教學模擬，不是真實店家或成效\n" + "\n".join(
    l for l in f03.split("\n")[3:] if l.strip() and not l.startswith(SPEAKER_ONLY))
assert "參考判斷" not in card2_paste and "12筆" in card2_paste
# 示範二貼給 AI 的版本：去講者專用三行，也去「任務：」那行（任務由老闆用語音交辦，見第 16 頁第一輪）；格式與不編造的規則保留
pack2 = "\n".join(l for l in f07.split("\n") if not l.startswith(SPEAKER_ONLY + ("任務：",))).rstrip() + chr(10) * 2 + (
    "先讀資料，不要先回答。任務等我用語音說明再回答。") + chr(10)
assert "參考判斷" not in pack2 and "會議逐字稿" in pack2 and "任務：" not in pack2 and "不編造網址" in pack2
assert "12筆" not in f06  # 第一輪包不能含容量答案
# 示範一貼給 AI 的版本：只留資料，任務兩行拿掉（任務由老闆用語音交代，見第 10 頁第一輪）
pack1_paste = chr(10).join(l for l in f06.split(chr(10)) if not l.startswith(("任務：", "先一句結論"))).rstrip() + chr(10) * 2 + (
    "先讀資料，不要先回答。任務等我用語音說明再回答；回答時先一句結論，再列理由，不要猜測還沒給你的資訊。") + chr(10)
assert "任務：" not in pack1_paste and "12筆" not in pack1_paste and "歷史CSV" in pack1_paste

def pack(key, text, label):
    return (f'<p><button class="copy" data-pack="{key}">{label}</button></p>'
            f'<pre class="pack" data-pack="{key}">{esc(text)}</pre>')

LIB = [
    ("lib-check", "開場前檢查", None),
    ("lib-howto", "本檔操作說明", None),
    ("lib-brand", "品牌與商品成本（原 01）", md(f01)),
    ("lib-history", "歷史三次活動（原 02／CSV）", md(f02)),
    ("lib-pack1", "示範一貼上包（原 06；貼給 AI 的版本不含任務兩行，任務改用講的）", pack("pack1", pack1_paste, "複製示範一貼上包")),
    ("lib-card2", "第二輪：店長確認（原 03）", md(f03) + '<h5>貼給 AI 的版本（不含講者分支與參考判斷）</h5>' + pack("card2", card2_paste, "複製店長確認")),
    ("lib-plan2", "示範二起點方案（原 05）", md(f05)),
    ("lib-meeting", "活動會議逐字稿（原 04）", md(f04)),
    ("lib-pack2", "示範二貼上包（原 07；貼給 AI 的版本不含講者三行與任務那行，任務改用講的）", pack("pack2", pack2, "複製示範二貼上包")),
    ("lib-ref1", "參考答案：示範一（原 08）", md(section(f08, "示範一：比較與修正"))),
    ("lib-ref2", "參考答案：示範二（原 08）", md(section(f08, "示範二：決議、提案與待分工"))),
    ("lib-budget", "預算與衡量（原 08）", md(section(f08, "預算與衡量"))),
    ("lib-success", "示範成功評估（原 08）", md(section(f08, "示範成功評估"))),
]

def checklist(items):
    return "<ul class=check>" + "".join(f"<li><label><input type=checkbox> {x}</label></li>" for x in items) + "</ul>"

CHECK_HTML = (
    '<p>2026/10/29，09:20–11:50，英才樓R313。所有現場項目均待講者與主辦實測；桌面檢查不能替代教室後排確認。勾選只存在這台電腦的瀏覽器。</p>'
    "<h5>開場前</h5>" + checklist([
        "整個資料夾複製到演講電腦（本檔已內含圖片與全部示範資料，單獨帶這一個檔也能跑）。用 Chrome 或 Edge 開「現場講解版.html」。",
        "確認電腦與投影機線材、轉接頭、畫面比例；Windows 鍵＋P 選「延伸」。從後排看第7、12、27頁與AI回答的字級。",
        "電腦、手機網路及備用連線實測；AI帳號已登入、當天額度與所需功能可用，兩段資料能貼上。",
        "若用語音，測試麥克風輸入、辨識及音箱播放；講者說話與AI聲音都讓後排聽見。示範步驟每一句都有「複製」鈕可改用貼上。",
        "關閉私人通知、私人分頁與不必要視窗。投影只顯示本次公開教學素材。",
        "示範一新對話只貼「示範一貼上包」；第二輪才補店長確認。不要先貼含答案的Excel或參考答案。",
        "示範二另開新對話貼「示範二貼上包」。若與第一段即時選擇不同，明說採用預備方案繼續演示。",
        "預備示例在本檔第39–43頁；全部現場操作，沒有錄影。",
        "與主辦確認10:20休息、10:40復場、11:35問答、11:48最後一題、11:50結束。",
    ]) +
    "<h5>現場分支</h5><ul>"
    "<li>AI超過45秒未完成：停止連續催問，跳到預備示例（示範一第39頁、示範二第41頁）；明說這是預先準備的示例。</li>"
    "<li>AI答對：請它指明依據、說出仍缺什麼，再給新條件。不要假裝它犯錯。</li>"
    "<li>AI答錯：回原始資料指出錯在哪，要求修正並重算相關部分。</li>"
    "<li>時間落後：保留一次容量修正與一次承諾查證，縮短逐列數據解說；不壓縮20分鐘休息或拖過11:50。</li>"
    "<li>無人提問：用第35頁的三個備案。無須要求學生操作、交作業或購買工具。</li>"
    "</ul><p>本包只提供分析、活動方案與待審稿；不代表發布、發送、投放、核准或獲得營收。圖表第27頁明示來源不足，只供查證討論。</p>"
)
HOWTO_HTML = (
    "<ul>"
    "<li><b>這個畫面＝講者畫面</b>：左邊是投影片和下一頁，右邊是要講的話、示範步驟、背景資料。</li>"
    "<li><b>有延伸螢幕時（建議）</b>：按 <kbd>O</kbd> 或「投影視窗」鈕（連上後會出現綠點）→ 跳出只有投影片的視窗 → 拖到投影幕 → 在那個視窗按 <kbd>F</kbd> 全螢幕。兩個視窗同步換頁，簡報筆在任一視窗都能用。</li>"
    "<li><b>只能鏡像（同畫面）時</b>：按 <kbd>N</kbd> 只顯示投影片，再按 <kbd>N</kbd> 回講者畫面。也可以事先 <kbd>Ctrl</kbd>+<kbd>P</kbd> 印出整份講稿。</li>"
    "<li><b>示範時（Codex Live 語音）</b>：把 Codex 視窗拖到投影幕；講者畫面留在筆電。先把貼上包給它，之後照「逐輪對話」用講的：每一輪有「我說／EVA 大概會答／我接著」。它答得跟參考不一樣沒關係，對就肯定，錯就追問。每一句都有「複製」鈕可改用貼的。</li>"
    "<li><b>換頁</b>：<kbd>→</kbd> <kbd>空白</kbd> <kbd>PageDown</kbd> 下一頁；<kbd>←</kbd> <kbd>PageUp</kbd> 上一頁；<kbd>Home</kbd> 首頁；<kbd>End</kbd> Q&amp;A。正常播放停在第35頁。</li>"
    "<li><b>講稿字太小</b>：按上方「字＋」「字−」，或鍵盤 <kbd>+</kbd> <kbd>-</kbd>。這台電腦會記住你選的大小。</li>"
    "<li><b>第 27 頁的圖太小</b>：按 <kbd>Z</kbd> 或點一下圖，整張圖放大到滿版；再按一次縮回。投影視窗會跟著放大。</li>"
    "<li><b>其他</b>：<kbd>A</kbd> 附錄（36–43）；<kbd>R</kbd> 從附錄回原頁；<kbd>D</kbd> 全部資料；<kbd>C</kbd> 開場前檢查；<kbd>F</kbd> 全螢幕；<kbd>Esc</kbd> 關資料。</li>"
    "</ul>"
)
LIB[0] = ("lib-check", "開場前檢查", CHECK_HTML)
LIB[1] = ("lib-howto", "本檔操作說明", HOWTO_HTML)

# ---------- 4. 每頁的示範步驟與背景資料 ----------
def say(t, copy=True):
    return f'<span class="say">{esc(t)}</span>' + ('<button class="copy">複製</button>' if copy else "")

BRANCH = lambda jump, label: (
    '<div class="branch"><b>卡住或意外時</b><ul>'
    f'<li>等超過45秒、讀不到資料、答案太長 → 不連續重問。說：{say("以下是事先準備的參考結果，我們仍一起檢查", False)} '
    f'<button class="jump" data-jump="{jump}">跳到預備示例（{label}）</button></li>'
    "<li>AI一次答對 → 請它指出依據、列未確認事項，再換一個條件追問；不要為戲劇效果硬說它答錯。</li>"
    "<li>時間落後 → 保留一次容量修正及一次承諾查證，略過逐列預算解說。10:20仍休息、10:40重開、11:50結束。</li>"
    "</ul></div>")

# 一輪對話＝我說（語音直接念；也有複製鈕）→ EVA 大概會答（參考答案摘要，不必逐字相同）→ 我接著怎麼做
def rd(me, ai, fix, extra=""):
    return (f'<div class="rd"><div class="me"><b>我說</b>{say(me)}{extra}</div>'
            f'<div class="ai"><b>EVA 大概會答</b>{ai}</div>'
            f'<div class="fx"><b>我接著</b>{fix}</div></div>')

DEMO = {
    9: ("示範一｜準備（本頁1分鐘）", [
        "Codex Live 開一個<b>新對話</b>，不要沿用舊的。",
        '先把「示範一貼上包」給它（貼上或附檔）：只有品牌資料＋三次活動數字，<b>不含</b>任務、<b>不含</b>店長確認。任務在下一頁第一輪用講的。<button class="copy" data-pack="pack1">複製示範一貼上包</button>',
        "資料給完就開口。接下來全部用講的，下一頁有每一輪的對話。",
    ], ""),
    10: ("示範一｜逐輪對話（10分鐘，5 輪）", [
        rd("EVA，我是課後咖啡的老闆。剛剛給你的兩份資料，一份是我們店的基本資料，一份是今年辦過的三次活動的數字，你先看一下。我下個月想再辦一場，十一月二號到十三號，平日下午。活動預算最多六千元，這六千是拿來打廣告、做素材、印店內告示的，咖啡的材料成本另外算。我的目標是帶進一百五十位新客人，貼文如果能紅更好。先不要急著寫文案，我們先討論。你幫我仔細分析判斷，這三個方案到底該用哪一個。",
           "先給一句結論：建議 C 雙人分享券小規模試行（或有理由地選 B）。理由：C 有 30% 回購、首次訂單貢獻最高；B 每位新客花的活動費最低；A 觸及最高但新客最少。會提醒：150 位要看店裡接得下多少、新客怎麼認定。",
           "牠沒先給結論，就說「你先講結論，選哪一個，再講理由」。牠如果直接說 150 位沒問題，問「一百五十這個數字，你是從哪裡算出來的？」"),
        rd("針對 A、B、C 三個方案，請幫我仔細比較與分析一下，各自最擅長的是哪些部分。",
           "A 看到的人最多，24,000 次觸及；B 每位新客花的活動費最低，4,000 元除以 72 位是 55.56 元；C 新客回來的比例最高，60 位有 18 位回來是 30%。也會提醒：三次活動的月份、渠道、客群不同，不能直接比輸贏。",
           "對到第 8 頁三張券。牠報數字時聽有沒有講「除以什麼」。沒講就問「你說 B 一位新客五十五塊，這是怎麼算出來的？」牠自己講清楚了，就說「好，這個算法我同意」。"),
        rd("我補充一件事。我剛問過店長，店裡下午人手就那樣，照顧原本客人之餘，每天最多只能再多接十二筆訂單。我打算保守一點，每天只開放十個名額，留兩筆當緩衝。另外提醒你，雙人套餐是兩個人一起來喝，但我們的會員系統只認付錢的那一位，同行的那位不算新客。這樣算起來，我原本想要的一百五十位新客，到底做得到做不到？做不到的話，合理的目標該訂多少？",
           "10 名額 × 10 天 ＝ 最多 100 筆訂單，150 位新客做不到。建議改成試行目標：80 筆訂單、60 位新客、18 位 30 天內回來。會說明 75% 新客、30% 回購是比照 C 的假設，不是保證；最後一批要觀察到 12/13。",
           "牠自己把「訂單」和「人數」分開了，就說「你有注意到這一點，很好」。只有牠把兩杯算成兩位新客時，才問「兩杯就等於兩位新客嗎？」接著追問「八十筆、六十位，哪個是算出來的，哪個是你估的？」要牠分清楚：一百筆是店長確認的上限，八十、六十是目標，七成五和三成是假設。這就是第 11 頁的三個章。",
           '<button class="copy" data-pack="card2">複製店長確認（備用：牠聽不清數字時貼給牠）</button>'),
        rd("再問你一個。假設活動結束，最後做了八十筆訂單，但新客只有四十八位。這樣我算成功還是失敗？我要怎麼跟店長講？",
           "訂單達標，新客沒達標：48 除以 60 是 80%。不能只挑達標的那項報喜。建議回頭看渠道、新舊客比例、招募方式；回購要等 12/13 觀察窗滿了再判斷。",
           "牠一刀切說「成功」或「失敗」，就問「哪一項達標？哪一項沒有？」牠如果順口報了回購率，問「十一月十三號那天，三十天還沒到的人你怎麼算？」"),
        rd("好。那就先照 C 方案小規模試，目標八十筆、六十位新客。這還是草案，我要再跟店長核對過才算定案。你幫我整理成一段摘要，我等一下帶去跟店長討論。",
           "一段摘要：選 C 試行、上限 100 筆、目標 80 筆／60 位新客／18 位回購、哪些是假設、還要跟店長確認什麼。",
           "牠一路選的是 B 而且理由合理，就肯定牠，然後對學生明說「第二段為了示範一致，用事先準備好的 C 方案繼續」。不要假稱牠剛剛選了 C。"),
    ], BRANCH(39, "示範一")),
    15: ("示範二｜準備（本頁1分鐘）", [
        "Codex Live <b>另開新對話</b>，不要被第一段的差異拖著走。",
        '把「示範二貼上包」給它（品牌資料＋店長確認＋起點方案＋會議逐字稿；<b>不含</b>任務，任務在下一頁第一輪用講的）。<button class="copy" data-pack="pack2">複製示範二貼上包</button>',
        "對學生說明：從事先準備的方案開始；這一段只擬稿，不發布、不寄給任何人。",
    ], ""),
    16: ("示範二｜逐輪對話（7分鐘，6 輪）", [
        rd("EVA，我們昨天開了活動會議，紀錄我剛給你了，還有上次定下來的試行方案。會議上講了很多事，我有點亂。你先幫我整理一下：哪些是我已經拍板的，哪些是行銷提的、還要我核准的，哪些是講到了但還沒有人接的。整理完之後，順便幫我寫一段對外的活動文案，一百二十字以內，再加三題客人常問的問答。我提醒你一下，會議上沒確定的事，不要幫我寫成確定的。",
           "一張表：事項、責任、期限、完成標準、狀態。每天 10 名額＝已決定方向；文案 FAQ 草稿＝行銷 10/28；品項備貨核銷＝店長 10/29；4,500 元預算＝提案待核；完整文案與預算＝店主 10/30 前核准；回購追蹤＝未定。再加一段文案、三題 FAQ。",
           "不逐字念表。只抽「回購追蹤」那一列，看牠寫誰負責。"),
        rd("回購追蹤這件事，會議上是誰接的？",
           "沒人接。店長只答應每天的核銷數，回購追蹤負責人未定；建議上線前要定下來。",
           "牠擅自寫「行銷負責」，就問「這是會議上講好的嗎？我怎麼沒印象。」要牠改回未定。牠本來就寫未定，改問「那還有哪些事是沒人接的？」"),
        rd("文案我看一下。行銷在會議上說想寫「保證有位」、「帶朋友來算兩位新客」，我當場說先不要。你寫的這段，有沒有哪一句是我還沒點頭的？有的話先標出來，不要先替我答應客人。",
           "指出會議上行銷想寫「保證有位、兩位新客」，店主說先不要。文案改成「內用依現場座位」、「每日活動名額 10 組」；指定品項、領券和核銷方式「以核准後活動頁為準」。",
           "對照第 17 頁三個章：方向已定、待核准、尚未發布。牠如果寫了「最後機會」「大家搶購」這種話，問「這句客人看了會以為什麼？我們做得到嗎？」"),
        rd("還有，領券的網頁行銷明天才交草稿，根本還沒上線。你這三題問答，客人看了會不會以為現在就可以領券？會的話改掉。",
           "FAQ 第三題改成「機制由店長確認、店主核准後公布」，不放連結。",
           "牠編了網址或寫「點此領券」，要牠刪掉。沒有的東西不能寫成有。"),
        rd("再問一個。活動十一月十三號結束，我想當天就看成效。那天能不能直接算出三十天回購率？算不出來的話，最快什麼時候可以？",
           "不能。每個人的截止日是首次核銷日加 30 天，最後一批到 12/13。還沒滿 30 天的人，不能算成「沒回購」。",
           "這是第 18 頁的時間軸。牠說 11/13 可以先報，問「十三號當天才來的客人，你觀察了幾天？」"),
        rd("好，今天先到這。你最後幫我整理一下：到現在為止，哪些東西已經做出來了，哪些事情其實還沒發生？我要跟店長講清楚，免得店長以為活動已經定了。",
           "已產出：分析、計畫、執行表、待審文案與 FAQ。還沒發生：核准、備貨、人員分工、真正投放與執行。",
           "念牠最後那句給學生聽，然後回投影片第 17 頁。"),
    ], BRANCH(41, "示範二")),
}
EXTRA = {
    36: '<div class="demo"><h3>預備示例</h3><p><button class="jump" data-jump="39">示範一預備示例（第39頁）</button> '
        '<button class="jump" data-jump="41">示範二預備示例（第41頁）</button></p></div>',
}
BG = {
    6: ["lib-brand"], 7: ["lib-history"], 8: ["lib-ref1"],
    9: ["lib-pack1", "lib-history"], 10: ["lib-ref1", "lib-card2", "lib-success"],
    11: ["lib-card2"], 12: ["lib-budget", "lib-plan2"], 14: ["lib-ref2"],
    15: ["lib-pack2", "lib-meeting"], 16: ["lib-ref2", "lib-meeting", "lib-success"],
    17: ["lib-ref2"], 18: ["lib-budget"],
}

# ---------- 5. 投影片（v2 排版）＋預備示例 39–43 ----------
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import slides_v2

ref1_rows = [l for l in section(f08, "示範一：比較與修正").split("\n") if l.startswith("|")]
ref2_rows = [l for l in section(f08, "示範二：決議、提案與待分工").split("\n") if l.startswith("|")]
ref2_txt = section(f08, "示範二：決議、提案與待分工")
copy_line = re.search(r"120字內文案[^\n]*\n(.+)", ref2_txt).group(1).strip()
faq = re.findall(r"^\d\. (.+)$", ref2_txt, re.M)
assert len(faq) == 3 and copy_line.startswith("課後")

slide_html = slides_v2.build(ref1_rows, ref2_rows, copy_line, faq)
assert sorted(slide_html) == list(range(1, 44))

# 核對：原 37 頁每一行的數字都要在，中文字至少九成還在（只換排版，不掉內容）
def plain(h):
    return re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", h)))
for no, lines in orig_lines.items():
    new = plain(slide_html[no + 1 if no >= 2 else no])  # 原版第 2 頁起後移一頁（新增自我介紹）
    for line in lines:
        nums = re.findall(r"\d[\d,.:]*\d|\d", line)
        miss = [x for x in nums if x not in new]
        han = [c for c in line if "一" <= c <= "鿿"]
        cover = sum(c in new for c in han) / max(1, len(han))
        if miss or (han and cover < .9):
            print(f"  [核對] 第{no}頁：{line}｜缺數字 {miss}｜中文保留 {cover:.0%}")

BACKUP = {39: ("預備示例｜示範一", "三個方案，用同一把尺比較"), 40: ("預備示例｜示範一", "策略修訂前後"),
          41: ("預備示例｜示範二", "決議、提案與待分工"), 42: ("預備示例｜示範二", "待審文案與 FAQ（未發布）"),
          43: ("預備示例｜示範二", "AI 做完，活動尚未完成")}
for no, (kick, head) in BACKUP.items():
    notes[no] = {"title": f"{kick}：{head}", "time": "備援，不計入正式時程",
                 "lines": ["（AI 沒回應或超過45秒時才用。不要把它說成現場生成。）",
                           "以下是事先準備的參考結果，我們仍然一起檢查。"]}
notes[39]["lines"].append("這張表把三個方案用同一把尺量。大家挑一欄看：這個數字用的是哪個分母？B 贏在哪裡？C 贏在哪裡？")
notes[41]["lines"].append("我們不逐列念，抽一列就好。看「回購追蹤」這列：負責人寫的是未定。沒有決定的事，AI 不能擅自派人，人也不能。")
notes[43]["lines"].append("（看完按 R 回到原本那一頁，繼續正式流程。）")

# ---------- 6. 組裝 ----------
def aside(no):
    n = notes[no]
    say_html = "".join(say_line(l) for l in n["lines"])
    demo = ""
    if no in DEMO:
        title, steps, branch = DEMO[no]
        demo = f'<div class="demo"><h3>{title}</h3><ol class="steps">' + "".join(f"<li>{s}</li>" for s in steps) + f"</ol>{branch}</div>"
    demo += EXTRA.get(no, "")
    bg = " ".join(BG.get(no, []))
    return f'<aside class="notes" data-bg="{bg}"><div class="say-block">{say_html}</div>{demo}</aside>'

deck = []
for no in range(1, 44):
    n = notes[no]
    deck.append(f'<section class="slide" data-no="{no}" data-title="{esc(n["title"])}" data-time="{esc(n["time"])}">'
                f'{slide_html[no]}{aside(no)}</section>')

library = "".join(f'<article id="{i}" data-title="{esc(t)}"><h4>{esc(t)}</h4>{c}</article>' for i, t, c in LIB)
toc = "".join(f'<a href="#{i}">{esc(t)}</a>' for i, t, _ in LIB)

img = {k: "data:image/{};base64,{}".format(ext, base64.b64encode((SRC / "assets" / f).read_bytes()).decode())
       for k, f, ext in (("horse", "Horse_drawn_US_Mail_car.jpg", "jpeg"), ("chart", "得到App_2026-03-01_19-06-44.png", "png"))}

tpl = (pathlib.Path(__file__).parent / "live_template.html").read_text(encoding="utf-8")
out = (tpl.replace("<!--DECK-->", "\n".join(deck))
          .replace("<!--LIBRARY-->", library)
          .replace("<!--TOC-->", toc)
          .replace("/*IMG*/", "const IMG={horse:'%s',chart:'%s'};" % (img["horse"], img["chart"])))
OUT.write_text(out, encoding="utf-8")
print("wrote", OUT, len(out) // 1024, "KB")
