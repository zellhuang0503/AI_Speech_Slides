# -*- coding: utf-8 -*-
"""10/29 演講投影片 v2：大講堂字級＋圖示、圖解、表格。
文字內容沿用原 index.html（署名與角色名已改「志宏老師」），只改呈現方式。
每頁輸出 1280×720 的 HTML 片段，CSS 在 live_template.html。"""
import html
import re

esc = html.escape

# ---------- 圖示（線條風格，24×24） ----------
ICONS = {
    "phone": '<rect width="14" height="20" x="5" y="2" rx="2"/><path d="M12 18h.01"/><path d="M12 13.6 9.9 11.6a1.4 1.4 0 0 1 2.1-1.9 1.4 1.4 0 0 1 2.1 1.9z"/>',
    "coffee": '<path d="M10 2v2"/><path d="M14 2v2"/><path d="M6 2v2"/><path d="M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1h14a4 4 0 1 1 0 8h-1"/>',
    "repeat": '<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/>',
    "filesearch": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><circle cx="11.5" cy="14.5" r="2.5"/><path d="m13.3 16.3 1.7 1.7"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "user": '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "spark": '<path d="M12 3l1.9 5.6L19.5 10.5 13.9 12.4 12 18l-1.9-5.6L4.5 10.5l5.6-1.9z"/><path d="M19 15v4"/><path d="M17 17h4"/>',
    "bot": '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "trend": '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    "badge": '<path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path d="m9 12 2 2 4-4"/>',
    "table": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M12 3v18"/>',
    "megaphone": '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    "ruler": '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.41 2.41 0 0 1 0-3.4l2.6-2.6a2.41 2.41 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "hourglass": '<path d="M5 22h14"/><path d="M5 2h14"/><path d="M17 22v-4.17a2 2 0 0 0-.59-1.42L12 12l-4.41 4.41A2 2 0 0 0 7 17.83V22"/><path d="M7 2v4.17a2 2 0 0 0 .59 1.42L12 12l4.41-4.41A2 2 0 0 0 17 6.17V2"/>',
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "flask": '<path d="M10 2v7.31"/><path d="M14 9.3V2"/><path d="M8.5 2h7"/><path d="M14 9.3a6.5 6.5 0 1 1-4 0"/><path d="M5.52 16h12.96"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "ban": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
    "store": '<path d="M3 9 4.5 4h15L21 9"/><path d="M3 9h18v1.5a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0Z"/><path d="M5 13v8h14v-8"/><path d="M10 21v-5h4v5"/>',
    "bars": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "msg": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "list": '<path d="M11 6h10"/><path d="M11 12h10"/><path d="M11 18h10"/><path d="m3 6 1.5 1.5L7 5"/><path d="m3 12 1.5 1.5L7 11"/><path d="m3 18 1.5 1.5L7 17"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
}


def I(name):
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


CUP = ('<svg class="cup" viewBox="0 0 220 220" aria-hidden="true">'
       '<g class="steam" fill="none" stroke="#B7802F" stroke-width="7" stroke-linecap="round">'
       '<path d="M80 64c-12-12 12-20 0-34"/><path d="M108 58c-12-12 12-20 0-34"/><path d="M136 64c-12-12 12-20 0-34"/></g>'
       '<ellipse cx="108" cy="192" rx="94" ry="16" fill="#E4D3B2"/>'
       '<path d="M168 106a26 26 0 0 1 0 52h-10" fill="none" stroke="#2E5A36" stroke-width="14"/>'
       '<path d="M40 92h136v34a68 68 0 0 1-136 0z" fill="#2E5A36"/>'
       '<ellipse cx="108" cy="92" rx="68" ry="12" fill="#3B2A1E"/>'
       '<path d="M60 122a50 50 0 0 0 26 44" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="8" stroke-linecap="round"/>'
       '</svg>')

ARROW = '<div class="arw rise" style="--d:{d}"><svg viewBox="0 0 48 48"><path d="M8 24h30M27 12l12 12-12 12"/></svg></div>'

CASE = "虛構教學模擬，不是真實店家或成效｜輸出待審"
ME = "志宏老師"
PREP = "預先準備的示例，非現場生成｜虛構教學模擬，不是真實店家或成效"
K1, K2 = "看見 AI 的行銷能力", "人的定位與技能"


def frame(no, kick, title, body, foot, cls="", right=""):
    tt = f'<h1 class="tt">{title}</h1>' if title else ""
    hr = f'<div class="hr">{right}</div>' if right else ""
    prog = f'<i class="prog" style="--p:{no / 35:.4f}"></i>' if no <= 35 else ""
    return (f'<div class="fr {cls}"><header class="hd"><div class="kick">{kick}</div>{hr}{tt}</header>'
            f'<div class="bd">{body}</div><footer class="ft"><span>{foot}</span><b>{no:02d}</b></footer>{prog}</div>')


def stamp(text, tone=""):
    return f'<span class="stamp {tone}">{text}</span>'


def card(icon, text, sub="", d=0, cls=""):
    head = f'<span class="h">{text}</span><small>{sub}</small>' if sub else text
    return f'<div class="card rise {cls}" style="--d:{d}">{I(icon)}<p>{head}</p></div>'


def row3(*cards):
    return '<div class="row3">' + "".join(card(*c, d=i) for i, c in enumerate(cards)) + "</div>"


def flow(*cards):
    out = []
    for i, c in enumerate(cards):
        if i:
            out.append(ARROW.format(d=2 * i - 1))
        out.append(c(2 * i) if callable(c) else card(*c, d=2 * i))
    return '<div class="flow">' + "".join(out) + "</div>"


def role_card(icon, who, text, ai=False):
    return lambda d: (f'<div class="card rise" style="--d:{d}"><div class="role{" ai" if ai else ""}">'
                      f'<span class="av">{I(icon)}</span>{who}</div><p>{text}</p></div>')


def rows(items, cls=""):
    out = []
    for i, it in enumerate(items):
        icon, text = it[0], it[1]
        extra = it[2] if len(it) > 2 else ""
        out.append(f'<div class="rw rise {cls}" style="--d:{i}"><span class="ib">{I(icon)}</span><span>{text}</span>{extra}</div>')
    return '<div class="rows">' + "".join(out) + "</div>"


def chat(me, ai):
    return ('<div class="chat">'
            f'<div class="msg rise" style="--d:0"><div class="who2"><span class="av">{I("user")}</span>志宏老師</div><div class="bub">{me}</div></div>'
            f'<div class="msg r rise" style="--d:4"><div class="who2"><span class="av">{I("spark")}</span>EVA</div><div class="bub">{ai}</div></div>'
            '</div>')


def bars(title, unit, data, color):
    top = max(v for _, v, _ in data)
    out = []
    for i, (k, v, label) in enumerate(data):
        r = v / top
        inside = " in" if r > .7 else ""
        out.append(f'<div class="bar" style="--d:{i}"><b>{k}</b><div class="tr"><i style="--v:{r:.4f};background:{color}"></i>'
                   f'<em class="{inside.strip()}" style="--v:{r:.4f}">{label}</em></div></div>')
    return f'<div class="bars"><h3>{title}<small>{unit}</small></h3>{"".join(out)}</div>'


def ticket(letter, name, strength, num, unit, d, formula=""):
    return (f'<div class="tk rise" style="--d:{d}"><div class="stb">{letter}</div>'
            f'<div class="tx"><div class="nm">{name}</div><div class="st">{strength}</div>'
            + (f'<div class="fm">{formula}</div>' if formula else "") + "</div>"
            f'<div class="nu"><b>{num}</b><small>{unit}</small></div></div>')


def chips(items, on):
    return '<div class="chips">' + "".join(
        f'<span class="{"on" if t == on else ""}">{I(ic) if ic else ""}{t}</span>' for ic, t in items) + "</div>"


def zigzag(n=22, depth=16):
    pts = ["0 0", "100% 0"]
    for i in range(n, -1, -1):
        y = f"calc(100% - {depth}px)" if i % 2 == 0 else "100%"
        pts.append(f"{i * 100 / n:.3f}% {y}")
    return "polygon(" + ",".join(pts) + ")"


def slide_table(md_rows, size, num_cols=()):
    rows_ = [r for r in md_rows if not re.match(r"^\|[\s\-:|]+\|$", r)]
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows_]
    th = "".join(f'<th class="{"num" if j in num_cols else ""}">{esc(c)}</th>' for j, c in enumerate(cells[0]))
    body = "".join("<tr>" + "".join(f'<td class="{"num" if j in num_cols else ""}">{esc(c)}</td>' for j, c in enumerate(r)) + "</tr>"
                   for r in cells[1:])
    return f'<table class="tb rise" style="font-size:{size}px"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


SKILLS = [("store", "商業理解"), ("target", "問題定義"), ("bars", "數字判讀"), ("bot", "AI 協作"), ("msg", "溝通落實")]
KMAP = [(None, "已知的已知"), (None, "已知的未知"), (None, "未知的未知")]


def skill(no, on, title, lines):
    icon = dict((t, ic) for ic, t in SKILLS)[on]
    body = (f'<div class="skl"><div class="disc rise" style="--d:0">{I(icon)}</div><div class="blt">'
            + "".join(f'<p class="rise" style="--d:{i + 1}">{t}</p>' for i, t in enumerate(lines)) + "</div></div>")
    return frame(no, K2, title, body, ME, right=chips(SKILLS, on))


def build(ref1_rows, ref2_rows, copy_line, faq):
    S = {}
    S[1] = frame(1, K1, None, f'''<div class="cov">
<div class="rise" style="--d:0"><h1><span>AI 時代</span><br>企業行銷策略</h1><p class="who">{I("user")}志宏老師</p></div>
<div class="rise" style="--d:2"><div class="etk"><div class="d">2026.10.29</div><div class="t">09:20–11:50</div>
<div class="p">{I("pin")}英才樓 R313</div></div></div></div>''', ME, "c-cover")

    # 自我介紹（依官網「關於我們」2026-10 版）
    career = [("廣告", "靈獅、智威湯遜"), ("科技", "富爾特科技"), ("連鎖通路", "歐德、全廉<br>系統家具"), ("印刷製造", "健豪印刷"), ("梵亞行銷", "2016 創辦<br>AI 轉型顧問")]
    S[2] = frame(2, "講者", "志宏老師是誰？", '<div class="me"><div class="tl">' + "".join(
        f'<div class="pt rise{" hi" if i == 4 else ""}" style="--d:{i}"><div class="d">{d}</div><div class="dot"></div><p>{p}</p></div>'
        for i, (d, p) in enumerate(career)) + '</div><div class="now">'
        f'<div class="rise" style="--d:5"><b>30<small>年</small></b><span>行銷資歷<br>25 歲入行</span></div>'
        f'<div class="rise" style="--d:6"><b>14<small>堂</small></b><span>台中教大 AI 課<br>教了三年半</span></div>'
        f'<div class="rise" style="--d:7"><b>100<small>+期</small></b><span>AI 每日晨報<br>自己寫的引擎</span></div>'
        '</div></div>', "現任：梵亞行銷創辦人兼執行總監｜百年連鎖餐飲品牌總經理的 AI 私人教練")

    S[3] = frame(3, K1, "客戶最後買到的是什麼？", row3(
        ("phone", "一則好看的<br>貼文？"), ("coffee", "一次值得付費<br>的體驗？"), ("repeat", "一次願意再來<br>的理由？")), ME)

    S[4] = frame(4, K1, "AI 可以參與行銷的整段工作", flow(
        ("filesearch", "讀資料", "找出值得<br>解決的問題"), ("scale", "比較方案", "整理成本<br>與限制"), ("pen", "起草", "內容、排程<br>與檢核表")), ME)

    S[5] = frame(5, K1, "工具換了，做法也要跟著變", f'''<div class="ims">
<img class="rise" style="--d:0;width:560px" data-img="horse" alt="約 1913 年，楠塔基特島郵差 Clinton Folger 用馬拖著汽車穿過禁行汽車的市區">
<div class="quote rise" style="--d:2">只把舊流程做快一點，<br>依舊是用<em>錯誤的方法</em><br>在解決問題。</div></div>''',
        "約 1913 年，美國楠塔基特島：市區禁行汽車，郵差只好用馬拖車｜照片：Nantucket Historical Association")

    S[6] = frame(6, K1, "一場咖啡品牌的行銷活動", f'''<div class="case">
<div class="shop rise" style="--d:0">{CUP}<h3>課後咖啡</h3><p>大學附近的午後空檔</p></div>
<div><div class="goal rise" style="--d:2">{I("target")}想帶來首次消費，再觀察回購</div>
<div class="menu rise" style="--d:2">單杯 90 元（材料 30）｜雙人套餐 180 元（材料 80）<br>活動 11/2–11/13，十個平日下午 14:00–17:00</div>
<div class="ask rise" style="--d:3"><div class="lb">老闆期待</div><div class="ns">
<div><b>6,000</b><span>元</span></div><div><b>150</b><span>位新客</span></div></div></div></div></div>''', CASE)

    # 第 7 頁：三次活動的原始紀錄（出自示範資料 02）。先讓人看懂活動是什麼，再看數字
    hist = [("A", "到店抽獎券", "買一杯 90 元，可抽獎", "6,000", "24,000", "24", "3"),
            ("B", "單杯折價券", "一杯 90 元折成 75 元", "4,000", "8,000", "72", "9"),
            ("C", "雙人分享券", "兩杯＋餅乾 220 變 180 元", "5,000", "6,000", "60", "18")]
    S[7] = frame(7, K1, "先讀資料，再想活動", '<table class="tb hist rise" style="--d:0;font-size:27px"><thead><tr>'
                 '<th>活動</th><th>怎麼玩</th><th class="num">活動費<small>元</small></th><th class="num">看到的人<small>次</small></th>'
                 '<th class="num">新客<small>人</small></th><th class="num">30天回來<small>人</small></th></tr></thead><tbody>'
                 + "".join(f'<tr><td><b class="lt">{a}</b>{n}</td><td>{how}</td><td class="num">{c}</td><td class="num">{r}</td>'
                           f'<td class="num hi">{nw}</td><td class="num">{rp}</td></tr>' for a, n, how, c, r, nw, rp in hist)
                 + '</tbody></table><p class="take rise" style="--d:2"><mark>觸及最多的 A，新客最少</mark></p>', CASE)

    S[8] = frame(8, K1, "活動方案必須有所取捨", '<div class="tks">'
                 + ticket("A", "到店抽獎券", "看到的人最多", "24,000", "次觸及", 0, "但每位新客花了 250 元（6,000 ÷ 24）")
                 + ticket("B", "單杯折價券", "每帶進一位新客，花最少活動費", "55.56", "元／位新客", 1, "4,000 元 ÷ 72 位新客；A 是 250 元，C 是 83.33 元")
                 + ticket("C", "雙人分享券", "新客回來的比例最高", "30%", "30 天內回來", 2, "60 位新客有 18 位回來；A、B 都只有 12.5%")
                 + f'</div><div class="warn rise" style="--d:3">{I("alert")}月份、渠道與客群不同，不能推因果</div>', CASE)

    live = '<span class="live"><i></i>現場示範</span>'
    S[9] = frame(9, K1, "示範一：從資料選方案" + live, flow(
        role_card("user", "志宏老師", "給目標、<br>客群與限制"), role_card("spark", "EVA", "比較選項，<br>提出理由", True),
        role_card("user", "志宏老師", "追問依據<br>與資源取捨")), CASE)

    S[10] = frame(10, K1, "「你為什麼選這個方案？」", chat(
        "先給結論，再列出證據。",
        '<div class="lead">建議先試 C。</div>'
        '<div class="tag"><b>已知</b>C 的 60 位新客有 18 位回來，30%。資料裡有。</div>'
        '<div class="tag"><b>假設</b>這次辦 C，回購也會有三成。我估的。</div>'
        '<div class="tag"><b>待確認</b>店裡每天能多接幾筆。要問店長。</div>'), CASE)

    S[11] = frame(11, K1, "選擇的理由，要能被追問", f'''<div class="ladder">
<div class="lad rise" style="--d:0">{stamp("期待", "c")}<div class="lb">初始期待</div><div class="bg">150</div><div class="un">位新客</div></div>
{ARROW.format(d=1)}
<div class="lad rise" style="--d:2">{stamp("店長確認", "m")}<div class="lb">實際容量</div><div class="bg">12</div><div class="un">筆／日<br>規劃 10 名額</div><div class="how">10 名額 × 10 天<br>＝ 上限 100 筆</div></div>
{ARROW.format(d=3)}
<div class="lad rise" style="--d:4">{stamp("假設")}<div class="lb">修訂試行</div>
<div class="mi"><b>80</b><span>筆</span></div><div class="mi"><b>60</b><span>新客</span></div><div class="mi"><b>18</b><span>位30天回購</span></div>
<div class="how">上限 100 筆內先試 80｜60 ＝ 80 × 75%｜18 ＝ 60 × 30%（照 C）</div></div>
</div>''', CASE)

    S[12] = frame(12, K1, "資源花在哪裡，策略就在哪裡", f'''<div class="rcp">
<div class="rc-w rise" style="--d:0"><div class="rc" style="clip-path:{zigzag()}">
<div class="rh"><span>課後咖啡｜活動預算</span>{stamp("提案", "c")}</div>
<div class="li"><span>廣告</span><i></i><b>3,000</b></div>
<div class="li"><span>素材</span><i></i><b>1,000</b></div>
<div class="li"><span>告示</span><i></i><b>500</b></div>
<div class="li sum"><span>提案支出</span><i></i><b>4,500 元</b></div>
<div class="li mut"><span>保留</span><i></i><b>1,500 元</b></div>
</div></div>
<div class="call rise" style="--d:2">{stamp("非淨利")}<div class="lb">如果做到 80 筆</div>
<div class="how">收入 80 × 180 ＝ 14,400<br>− 材料 80 × 80 ＝ 6,400<br>− 活動費 4,500</div><div class="lb2">活動餘額</div>
<div class="bg">3,500<small>元</small></div></div></div>''', CASE)

    S[13] = frame(13, K1, "目標與保證是兩回事", row3(
        ("target", "目標", "希望達到的結果<em>例：帶來 60 位新客</em>"), ("trend", "預估", "在假設下推算的結果<em>例：80 筆 × 75% ＝ 60 位</em>"),
        ("badge", "承諾", "已確認能交付的內容<em>例：每日 10 組套餐</em>"))
        + '<div class="cert rise" style="--d:3"><span>確定程度 低</span><i></i><span>高</span></div>', CASE)

    S[14] = frame(14, K1, "一個方案，需要多種交付物", row3(
        ("table", "執行表", "誰、何時、<br>做完算什麼"), ("megaphone", "對外文案", "能說什麼，<br>不能保證什麼"), ("ruler", "衡量表", "如何知道<br>活動有沒有用")), CASE)

    S[15] = frame(15, K1, "示範二：把方案變成行動" + live, flow(
        role_card("user", "志宏老師", "給方案與<br>會議紀錄"), role_card("spark", "EVA", "整理交辦<br>與待審文案", True),
        role_card("user", "志宏老師", "修正承諾<br>與衡量方式")), CASE)

    S[16] = frame(16, K1, "「這句話，我們真的能說嗎？」", chat("哪些是決議，哪些仍待核准？", "文案可以起草；未定責任仍要列出。"), CASE)

    S[17] = frame(17, K1, "修正後，才是可審閱的版本", rows([
        ("check", "每日 10 組；內用依現場座位", stamp("方向已定", "m")),
        ("hourglass", "指定品項、怎麼領券、怎麼兌換", stamp("待核准")),
        ("doc", "所有內容均為待審稿", stamp("尚未發布", "c"))]), CASE)

    S[18] = frame(18, K1, "有結果，還要能解釋結果", '''<div class="tags rise" style="--d:0"><span>訂單</span><span>新客</span><span>回購</span><em>分開記錄</em></div>
<div class="tl"><div class="pt rise" style="--d:1"><div class="d">11/2</div><div class="dot"></div><p>活動開始</p></div>
<div class="pt rise" style="--d:2"><div class="d">11/13</div><div class="dot"></div><p>活動結束，<br>回購仍在追蹤</p></div>
<div class="pt hi rise" style="--d:3"><div class="d">12/13</div><div class="dot"></div><p>最後一批滿 30 天<br>（11/13 ＋ 30 天）</p></div></div>''', CASE)

    S[19] = frame(19, K1, None, '''<div class="stm"><span class="ghost">?</span>
<h2 class="rise" style="--d:0">AI 能做這麼多，<br>企業還需要<em>人</em>做什麼？</h2><p class="rise" style="--d:3">先把這個問題留著。</p></div>''', ME, "dark")

    S[20] = frame(20, "中場休息", None, f'''<div class="brk"><div class="rise" style="--d:0">{CUP}</div>
<div><h2 class="rise" style="--d:1">休息 20 分鐘</h2><div class="back rise" style="--d:2"><b>10:40</b><span>回來</span></div>
<p class="rise" style="--d:3">下半場：人的定位與要練的技能</p></div></div>''', ME)

    S[21] = frame(21, K2, "回看剛才的兩段對話", f'''<div class="duo">
<div class="card rise" style="--d:0">{I("bot")}<p>AI 做了很多執行工作。</p></div>
<div class="card hi rise" style="--d:2"><span class="qm">?</span>{I("user")}<p>人在哪些地方<br>改變了結果？</p></div></div>''', ME)

    S[22] = frame(22, K2, "人與 AI 協作的三明治原則", '''<div class="sand"><div class="lys">
<div class="ly br t rise" style="--d:0"><b>人：</b>給目標、背景、限制與標準</div>
<div class="ly f rise" style="--d:1"><b>AI：</b>執行、整理、計算與起草<span class="sub">工作量最大的一層，全部交給 AI；人只做兩頭最重要的事</span></div>
<div class="ly br b rise" style="--d:2"><b>人：</b>查證、判斷、修正，再交回 AI</div></div>
<div class="loop rise" style="--d:3"><svg viewBox="0 0 170 350"><path d="M24 322C152 322 152 28 24 28"/><path d="M52 6 24 28l28 22"/></svg></div></div>''', ME)

    S[23] = frame(23, K2, "企業仍需要有人對結果負責", rows([
        ("target", "判斷哪個問題值得解決"), ("scale", "在資源與風險之間做選擇"), ("shield", "確認承諾，協調完成，承擔後果")]), ME)

    S[24] = frame(24, K2, "已知的已知", rows([
        ("filesearch", "資料裡明確寫了什麼？"), ("help", "這個數字是事實，還是教學假設？"), ("ruler", "定義、期間與單位是否一致？")]),
        ME, right=chips(KMAP, "已知的已知"))
    S[25] = frame(25, K2, "已知的未知", rows([
        ("help", "已經知道缺哪項資訊"), ("users", "列出誰能確認、何時確認"), ("hourglass", "沒有確認，就保留條件")]),
        ME, right=chips(KMAP, "已知的未知"))
    S[26] = frame(26, K2, "未知的未知", rows([
        ("bulb", "AI 可以提出你沒想到的盲點"), ("flask", "新提醒先當假說"), ("search", "再找證據，必要時小規模驗證")]),
        ME, right=chips(KMAP, "未知的未知"))

    S[27] = frame(27, K2, "一張看起來很有說服力的圖", '<div class="ims">'
                  '<img class="rise zoomable" style="--d:0;height:480px" data-img="chart" alt="待核對的圖表｜原圖 Feb 2026｜來源與口徑未核實">'
                  + rows([("calendar", "圖中標示 Feb 2026"), ("ban", "無可追溯的原始統計來源"), ("alert", "不能當作最新全球使用現況")], "a")
                  + "</div>", "待核對的圖表｜原圖 Feb 2026｜來源與口徑未核實")

    S[28] = frame(28, K2, "五項值得練的能力", '<div class="five">' + "".join(
        f'<div class="rise" style="--d:{i}"><span class="ib">{I(ic)}</span>{t}</div>' for i, (ic, t) in enumerate(
            [("store", "商業理解"), ("target", "問題定義"), ("bars", "資料與<br>數字判讀"), ("bot", "AI 協作<br>與查證"), ("msg", "溝通落實")]))
        + "</div>", ME)

    S[29] = skill(29, "商業理解", "商業理解：知道為誰創造價值", ["顧客想解決什麼問題？", "公司想改變什麼結果？", "這個活動如何把兩者接起來？"])
    S[30] = skill(30, "問題定義", "問題定義：把模糊要求說清楚", ["把「幫我做行銷」改成一份任務", "說清楚背景、目標與不能做的事", "先約定好成果如何判斷"])
    S[31] = skill(31, "數字判讀", "數字判讀：看懂分母與代價", ["人次、訂單、會員不能混為一談", "營收、毛利、活動費用要分開", "目標不是預測，觀察不是因果"])
    S[32] = skill(32, "AI 協作", "AI 協作：每一輪都能被檢查", ["請它區分依據、推論與待確認", "挑重要數字與承諾回到原資料", "記下修正，讓下一輪更接近需求"])
    S[33] = skill(33, "溝通落實", "溝通落實：讓別人接得住", ["有負責人、期限與完成證據", "待審稿與已核准內容要分開", "遇到變化，回報並重排"])

    S[34] = frame(34, K2, None, '''<div class="stm">
<h2 class="rise" style="--d:0">把事情做出來，<br>也把<em>為什麼</em>說清楚</h2><p class="rise" style="--d:3">先理解，再協作；做完之後，再檢查。</p></div>''', ME, "dark")

    S[35] = frame(35, "提問與交流", None, f'''<div class="qa"><div class="q rise" style="--d:0">Q&amp;A</div><div class="qs">
<div class="rise" style="--d:1">{I("help")}哪一段最像你未來會遇到的工作？</div>
<div class="rise" style="--d:2">{I("help")}哪一個 AI 結果，<br>你最不敢直接相信？</div></div></div>''', ME, "dark")

    S[36] = frame(36, "備援附錄", "備援：示範沒有回應時", rows([
        ("megaphone", "明說：接下來是預先準備的示例"), ("scale", "對照同一份輸入、推理與修正"), ("ban", "不把預備結果冒充現場生成")]), ME)

    S[37] = frame(37, "備援附錄", "附錄：原版急單判斷", '<div class="row3 stat">' + "".join(
        f'<div class="card rise" style="--d:{i}"><div class="bg">{n}<small>{u}</small></div><p>{t}</p></div>' for i, (n, u, t) in enumerate(
            [("3,000", "件", "急單<br>先檢查接單條件"), ("500", "kg", "補料<br>每件成本 70.64 元"), ("91.80", "元", "售價<br>毛利 21.16 元")]))
        + "</div>", "原版虛構教學案例｜2026/9/12｜非咖啡活動數據")

    S[38] = frame(38, "備援附錄", "附錄：會後整理的方法", rows([
        ("list", "決議與建議分開"), ("calendar", "責任、期限、標準可以追蹤"), ("hourglass", "未確認事項保留在清單上")]), ME)

    # ---------- 預備示例 39–43 ----------
    prep = stamp("預先準備")
    S[39] = frame(39, "預備示例｜示範一", "三個方案，用同一把尺比較",
                  slide_table(ref1_rows, 27, num_cols=(1, 2, 3))
                  + '<p class="fine rise" style="--d:2">固定支出／新客不是增量 CAC；扣固定費後不是淨利。觸及不可跨活動加總；月份、渠道、客群不同，不能當因果實驗。</p>',
                  PREP, right=prep)
    steps39 = ["初始期待：6,000元、150位新客，也希望貼文很紅。",
               "EVA比較：A觸及較高；B固定支出/新客較低；C觀察到較高回購與貢獻。不能推論因果。",
               "志宏老師第二輪補充：額外最多12筆/日，規劃10名額留2緩衝，每筆最多識別一位首次付款會員。",
               "參考修訂：全期100筆上限，試行80筆／60新客／18位30天再次付費；目標不是保證。",
               "檢查：若80筆但48新客，訂單達標、新客未達。最後回購觀察到12/13。"]
    S[40] = frame(40, "預備示例｜示範一", "策略修訂前後", '<div class="steps2">' + "".join(
        '<p class="rise" style="--d:{}"><span><b>{}：</b>{}</span></p>'.format(i, *map(esc, s.split("：", 1))) for i, s in enumerate(steps39))
        + "</div>", PREP, right=prep)
    S[41] = frame(41, "預備示例｜示範二", "決議、提案與待分工", slide_table(ref2_rows, 21).replace('class="tb rise"', 'class="tb dense rise"'), PREP, right=prep)
    S[42] = frame(42, "預備示例｜示範二", "待審文案與 FAQ（未發布）",
                  f'<div class="cpy rise" style="--d:0"><div class="lb">120字內文案（待審）</div>{esc(copy_line)}</div><ol class="faq">'
                  + "".join('<li class="rise" style="--d:{}"><b>{}？</b>{}</li>'.format(i + 1, *map(esc, q.split("？", 1))) for i, q in enumerate(faq))
                  + "</ol>", PREP, right=prep)
    S[43] = frame(43, "預備示例｜示範二", "AI 做完，活動尚未完成", rows([
        ("check", "<b>已產出：</b>分析、計畫、執行表、待審文案與FAQ。"),
        ("hourglass", "<b>仍待做：</b>指定品項、備貨、核銷方式、責任分工、預算與文案核准。"),
        ("help", "<b>志宏老師追問：</b>回購負責人是會議決議嗎？領券機制已核准嗎？"),
        ("pen", "<b>參考修正：</b>責任未定就列未定；不保證有位、不把同行者算新客、不編上線網址。"),
        ("ban", "<b>沒有真的投放、發布、發送或成交；</b>這裡展示的是預先準備的示例。")], "sm"), PREP, right=prep)
    return S
