import tkinter as tk
from tkinter import scrolledtext, ttk
from backend_logic_v10 import generate_response
import threading

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

# メインウィンドウの設定
window = tk.Tk()
window.title("法子アシスタント")

# チャットログエリア
chat_log = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
chat_log.pack(padx=10, pady=10)

# ユーザー入力エリア
user_entry = tk.Entry(window, width=70)
user_entry.pack(padx=10, pady=5)

# ボタンエリア
button_frame = tk.Frame(window)
button_frame.pack(pady=5)

# 送信ボタン
send_button = tk.Button(button_frame, text="送信", command=send_message)
send_button.grid(row=0, column=0, padx=5)

# 停止ボタン
stop_button = tk.Button(button_frame, text="停止", command=stop_process, state=tk.DISABLED)
stop_button.grid(row=0, column=1, padx=5)

# クリアボタン
clear_button = tk.Button(button_frame, text="クリア", command=clear_text)
clear_button.grid(row=0, column=2, padx=5)

# 閉じるボタン
close_button = tk.Button(button_frame, text="閉じる", command=close_app)
close_button.grid(row=0, column=3, padx=5)

# ステータスバー
status_label = ttk.Label(window, text="待機中")
status_label.pack(pady=5)

# テキストスタイル設定
chat_log.tag_config("user", foreground="blue")
chat_log.tag_config("document", foreground="green")
chat_log.tag_config("response", foreground="black")

# GUIループの開始
window.mainloop()
