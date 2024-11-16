import tkinter as tk
from tkinter import scrolledtext, ttk
from backend_logic_v10 import generate_response
import threading
import os

# グローバルフラグ
stop_flag = False

# 処理を停止する関数
def stop_process():
    global stop_flag
    stop_flag = True
    status_label.config(text="処理が停止されました。")
    send_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# メッセージを送信する関数
def send_message():
    global stop_flag
    stop_flag = False

    user_input = user_entry.get()
    if user_input:
        status_label.config(text="処理中...")
        send_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        window.update_idletasks()

        def run_task():
            try:
                relevant_document, response_text, similarity_score_embedding = generate_response(user_input)

                # 処理が停止されている場合、出力しない
                if stop_flag:
                    return

                chat_log.insert(tk.END, f"ユーザー: {user_input}\n", "user")
                chat_log.insert(tk.END, "-"*50 + "\n")
                chat_log.insert(tk.END, f"関連する過去問: {relevant_document}\n", "document")
                chat_log.insert(tk.END, "-"*50 + "\n")
                chat_log.insert(tk.END, f"AIの回答: {response_text}\n", "response")
                chat_log.insert(tk.END, "-"*50 + "\n")
                chat_log.insert(tk.END, f"埋め込みモデルによる類似性スコア: {similarity_score_embedding}\n", "response")
                chat_log.insert(tk.END, "-"*50 + "\n")

                status_label.config(text="完了")
            except Exception as e:
                status_label.config(text=f"エラー: {str(e)}")
            finally:
                send_button.config(state=tk.NORMAL)
                stop_button.config(state=tk.DISABLED)

        # 別スレッドで実行
        threading.Thread(target=run_task).start()

# 入力とログをクリアする関数
def clear_text():
    user_entry.delete(0, tk.END)
    chat_log.delete(1.0, tk.END)
    status_label.config(text="入力がクリアされました。")
    send_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# アプリケーションを閉じる関数
def close_app():
    window.quit()
    window.destroy()

# ログを保存する関数
# ログを保存する関数
def save_log():
    log_text = chat_log.get(1.0, tk.END).strip()

    if not log_text:
        status_label.config(text="ログが空です。")
        return

    # 既存の log.txt の内容を読み込む
    if os.path.exists("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as f:
            existing_log = f.read()
    else:
        existing_log = ""

    # 現在のログが既存のログに重複していないか確認
    if log_text in existing_log:
        status_label.config(text="重複したログが見つかりました。保存は行われませんでした。")
        return

    # 重複がなければログを保存
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(log_text + "\n" + "=" * 80 + "\n")

    status_label.config(text="ログが保存されました。")

# メインウィンドウの設定
window = tk.Tk()
window.title("法子アシスタント")
window.geometry("900x560")  # ウィンドウサイズを大きく設定

# モニターの中央にウィンドウを表示する
window.update_idletasks()  # ウィンドウサイズを取得するために更新
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = 900
window_height = 560

# 中央に表示するための座標を計算
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# フォント設定
font_style = ("Meiryo", 16)

# チャットログエリア
chat_log = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=90, height=12, font=font_style)
chat_log.pack(padx=10, pady=10)

# ユーザー入力エリア
user_entry = tk.Entry(window, width=80, font=font_style)
user_entry.pack(padx=10, pady=5)

# グローバルフラグ
stop_flag = False

# 処理を停止する関数
def stop_process():
    global stop_flag
    stop_flag = True
    status_label.config(text="処理が停止されました。")
    send_button.config(state=tk.NORMAL, fg="green")
    stop_button.config(state=tk.DISABLED, fg="black")

# メッセージを送信する関数
def send_message():
    global stop_flag
    stop_flag = False

    user_input = user_entry.get()
    if user_input:
        status_label.config(text="処理中...")
        send_button.config(state=tk.DISABLED, fg="black")
        stop_button.config(state=tk.NORMAL, fg="red")
        window.update_idletasks()

        def run_task():
            try:
                relevant_document, response_text, similarity_score_embedding = generate_response(user_input)

                # 処理が停止されている場合、出力しない
                if stop_flag:
                    return

                chat_log.insert(tk.END, f"ユーザー: {user_input}\n", "user")
                chat_log.insert(tk.END, "-"*50 + "\n")
                chat_log.insert(tk.END, f"関連する過去問: {relevant_document}\n", "document")
                chat_log.insert(tk.END, "-"*50 + "\n")
                chat_log.insert(tk.END, f"AIの回答: {response_text}\n", "response")
                chat_log.insert(tk.END, "-"*50 + "\n")
                chat_log.insert(tk.END, f"埋め込みモデルによる類似性スコア: {similarity_score_embedding}\n", "response")
                chat_log.insert(tk.END, "-"*50 + "\n")

                status_label.config(text="完了")
            except Exception as e:
                status_label.config(text=f"エラー: {str(e)}")
            finally:
                send_button.config(state=tk.NORMAL, fg="green")
                stop_button.config(state=tk.DISABLED, fg="black")

        # 別スレッドで実行
        threading.Thread(target=run_task).start()

# ボタンエリア
button_frame = tk.Frame(window)
button_frame.pack(pady=5)

# 保存ボタン
save_button = tk.Button(button_frame, text="保存", command=save_log, font=font_style)
save_button.grid(row=0, column=0, padx=5)

# 送信ボタン（デフォルトで緑色）
send_button = tk.Button(button_frame, text="送信", command=send_message, font=font_style, fg="green")
send_button.grid(row=0, column=1, padx=5)

# 停止ボタン（デフォルトで赤色、無効状態は黒色）
stop_button = tk.Button(button_frame, text="停止", command=stop_process, state=tk.DISABLED, font=font_style, fg="black")
stop_button.grid(row=0, column=2, padx=5)

# クリアボタン
clear_button = tk.Button(button_frame, text="クリア", command=clear_text, font=font_style)
clear_button.grid(row=0, column=3, padx=5)

# 閉じるボタン
close_button = tk.Button(button_frame, text="閉じる", command=close_app, font=font_style)
close_button.grid(row=0, column=4, padx=5)

# ステータスバー
status_label = ttk.Label(window, text="待機中", font=font_style)
status_label.pack(pady=5)

# テキストスタイル設定
chat_log.tag_config("user", foreground="blue")
chat_log.tag_config("document", foreground="green")
chat_log.tag_config("response", foreground="black")

# GUIループの開始
window.mainloop()
