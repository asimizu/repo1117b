# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
	ApiClient, Configuration, MessagingApi,
	ReplyMessageRequest, PushMessageRequest,
	TextMessage, PostbackAction
)
from linebot.v3.webhooks import (
	FollowEvent, MessageEvent, PostbackEvent, TextMessageContent
)
import os
import smtplib
from email.mime.text import MIMEText
import json

def send_gmail(mail_from, mail_to, mail_subject, mail_body):


    """ メッセージのオブジェクト """
    msg = MIMEText(mail_body, "plain", "utf-8")
    msg['Subject'] = mail_subject
    msg['From'] = mail_from
    msg['To'] = mail_to

    # エラーキャッチ
    try:
        """ SMTPメールサーバーに接続 """
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)  # SMTPオブジェクトを作成。smtp.gmail.comのSMTPサーバーの587番ポートを設定。
        smtpobj.ehlo()                                 # SMTPサーバとの接続を確立
        smtpobj.set_debuglevel(True) # enable debug output
        smtpobj.starttls()                             # TLS暗号化通信開始
        gmail_addr = "yamaharu9876@gmail.com"       # Googleアカウント(このアドレスをFromにして送られるっぽい)
        app_passwd = "bxvykhiunzvojfvk"       # アプリパスワード
        smtpobj.login(gmail_addr, app_passwd)          # SMTPサーバーへログイン

        """ メール送信 """
        smtpobj.sendmail(mail_from, mail_to, msg.as_string())

        """ SMTPサーバーとの接続解除 """
        smtpobj.quit()

    except Exception as e:
	print("Cloudn't send mail")
	app.logger.info(("Cloudn't send mail")
        print(e)
    
    return "メール送信完了"

## .env ファイル読み込み
from dotenv import load_dotenv
load_dotenv()

## 環境変数を変数に割り当て
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

## Flask アプリのインスタンス化
app = Flask(__name__)

## LINE のアクセストークン読み込み
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

## コールバックのおまじない
@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)

	return 'OK'

## 友達追加時のメッセージ送信
@handler.add(FollowEvent)
def handle_follow(event):
	## APIインスタンス化
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	## 返信
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text='Thank You!')]
	))
	
## オウム返しメッセージ
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
	## APIインスタンス化
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	## 受信メッセージの中身を取得
	received_message = event.message.text

	## APIを呼んで送信者のプロフィール取得
	profile = line_bot_api.get_profile(event.source.user_id)
	display_name = profile.display_name
	print(f"user_id:{event.source.user_id}")

	## 返信メッセージ編集
	reply = f'{display_name}さんのメッセージ\n{received_message}'

	## オウム返し
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text=reply)]
	))
	""" メール設定 """
	mail_from = "yamaharu9876@gmail.com"       # 送信元アドレス
        mail_to = "asimizu@gmail.com"         # 送信先アドレス(To)
	mail_subject = "from LINE"                   # メール件名
	mail_body = event.message.text                      # メール本文
	
	""" send_gmail関数実行 """
    	result = send_gmail(mail_from, mail_to, mail_subject, mail_body)
	print(result)


## 起動確認用ウェブサイトのトップページ
@app.route('/', methods=['GET'])
def toppage():
	return 'Hello world!'

## ボット起動コード
if __name__ == "__main__":
	## ローカルでテストする時のために、`debug=True` にしておく
	app.run(host="0.0.0.0", port=8000, debug=True)
