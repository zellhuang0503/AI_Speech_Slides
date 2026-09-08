# -*- coding: utf-8 -*-
"""把 emails/ 內的 5 封示範信寄到 via9110@gmail.com。
用法：
  1. 在寄件用的 Gmail 帳號開啟兩步驟驗證，建立「應用程式密碼」（Google 帳戶 → 安全性 → 應用程式密碼）。
  2. 執行：python3 send_emails.py 寄件帳號@gmail.com 應用程式密碼
  信件寄出後，Gmail 會顯示為「寄件者：你的帳號」，示範時請用主旨與內容即可；
  若想保留假寄件者名稱，改用 Thunderbird / Apple Mail 匯入 .eml 再拖進 Gmail。
"""
import sys, smtplib, glob
from email import message_from_binary_file
from email.message import EmailMessage

if len(sys.argv) != 3:
    print(__doc__); sys.exit(1)
user, pwd = sys.argv[1], sys.argv[2]
TO = "via9110@gmail.com"
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(user, pwd)
    for path in sorted(glob.glob("emails/*.eml")):
        src = message_from_binary_file(open(path, "rb"))
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = TO
        msg["Subject"] = src["Subject"]
        msg.set_content(f"（示範信件，原寄件者：{src['From']}）\n\n" + src.get_content(), charset="utf-8")
        s.send_message(msg)
        print("sent:", src["Subject"])
