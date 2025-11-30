import os
import sys
from moviepy.editor import *
import tkinter as tk
from tkinter import filedialog
import traceback

# ================= 設定區 (Mac 專用修訂版) =================
# PyInstaller 會把程式打包成 exe，資源會放在 _MEIPASS
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # exe 所在資料夾
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
# 1. 設定中文字型
# Mac 建議使用 'Arial Unicode MS' 或 'PingFang TC'
FONT_PATH = os.path.join(BASE_DIR, "resources", "PingFang.ttc")  # 請確定這個字型檔存在

LOGO_FILENAME = os.path.join(BASE_DIR, "resources", "logo.png")

texts_to_add = [
    {"text": "LIND ID: burceet", "offset_y": 150, "color": "red","align": "center"},
    {"text": "【台南,高雄,嘉義,屏東市,大台北到府維修】", "offset_y": 280, "color": "yellow","fontsize":55,"align": "left"},
    # 可以再加更多
]
# ========================================================

def process_all_folders(base_folder="data"):
    print(f"🔍 走訪資料夾: {os.walk(base_folder)}")
    """走訪 data 下所有子資料夾，找到可合併的影片並處理"""
    for root, dirs, files in os.walk(base_folder):
        # 跳過最外層，避免直接在 data 裡處理
        if root == base_folder:
            continue

        print(f"\n📁 正在檢查資料夾: {root}")

        # 切換到子資料夾
        os.chdir(root)

        vid1, vid2 = find_video_files()
        if vid1 and vid2:
            print(f"➡ 找到影片: {vid1}, {vid2}")
            # 執行你的 main()（你要改成能接受 路徑 參數）
            remix_movie()
        else:
            print("❌ 沒有找到可合併的影片，跳過此資料夾")

        # 回到上一層
        os.chdir("../../")

def find_video_files():
    """搜尋當前目錄下符合關鍵字的影片"""
    # 忽略隱藏檔案
    files = [f for f in os.listdir('.') if not f.startswith('.') and f.endswith(('.mp4', '.mov', '.avi', '.mkv'))]
    
    video1_path = next((f for f in files if "_未完成" in f), None)
    video2_path = next((f for f in files if "_已完成" in f), None)
    
    return video1_path, video2_path

def parse_video_name(filename):
    """
    從影片檔名中取出：
    1. 型號（第一段）
    2. 問題描述（第二段）
    
    檔名格式：
    型號_問題_已完成.mp4
    型號_問題_未完成.mp4
    """

    name, _ = os.path.splitext(filename)  # 去掉 .mp4
    parts = name.split("_")

    if len(parts) < 3:
        return None, None  # 格式不符

    model = parts[0]
    issue = parts[1]

    return model, issue

def create_corner_text(text, duration, fontsize=50, color='red', position=('right', 'top')):
    """建立右上角的標籤文字 (未完成/已完成)"""
    # 使用紅色字體或顯眼顏色，加粗邊框
    txt_clip = TextClip(text, font=FONT_PATH, fontsize=fontsize, color=color, stroke_color='white', stroke_width=2)
    # 2. 建立背景紅框（矩形）
    padding = 20  # 內縮距離，你可以調整
    box = ColorClip(
        size=(txt_clip.w + padding, txt_clip.h + padding),
        color=(255, 0, 0)   # 紅色
    ).set_duration(duration)
    # 3. 文字放到紅框中間
    txt = txt_clip.set_position(("center", "center")).set_duration(duration)
    # 4. 合併成一個Composite（紅框底 + 文字）
    boxed = CompositeVideoClip([box, txt])
    # 進場動畫（淡入 + 放大）
    def intro_effect(t):
        scale = 0.6 + 0.4 * min(1, t / 0.5)   # 0.5 秒完成放大
        return scale
    animated = boxed.resize(intro_effect).fadein(0.5)

    # 設定邊距 margin 讓文字不要貼死邊緣
    txt_clip = animated.set_position(position).set_duration(duration).margin(right=20, top=20, opacity=0)
    return txt_clip

def create_product_text(text, duration, video_clip, fontsize=80, color='white', offset_y=0, x_pos=None):
    if video_clip:
        w, h = video_clip.size
    else:
        w, h = 1920, 1080

    txt_clip = TextClip(
        text,
        font=FONT_PATH,
        fontsize=fontsize,
        color=color,
        stroke_color=color,
        stroke_width = 4
    )
    print(f"-----{text}----")
    print(x_pos)
    # 決定水平位置
    if x_pos is None:
        print(f"{text}>>> 水平置中文字")
        x = (w - txt_clip.w) / 2  # 預設置中
    else:
        x = x_pos - 10  # 調整為距左邊10px
    y = (h - txt_clip.h) / 2 + offset_y
    txt_clip = txt_clip.set_position((x, y)).set_duration(duration)
    return txt_clip
def remix_movie():
    print(">>> 正在搜尋影片檔案...")
    vid1_path, vid2_path = find_video_files()
    if not vid1_path or not vid2_path:
        print("錯誤：找不到包含 '_未完成' 或 '_已完成' 的影片檔。")
        print(f"當前搜尋目錄: {os.getcwd()}")
        return
    model2, issue2 = parse_video_name(vid2_path) if vid2_path else (None, None)

    print(f"找到第一部: {vid1_path}")
    print(f"找到第二部: {vid2_path}")
    print(f"影片型號: {model2}, 問題描述: {issue2}")
    # 輸入全程顯示的文字
    global_television_text_content = model2
    global_status_text_content = issue2

    try:
        # 1. 載入影片
        clip1 = VideoFileClip(vid1_path)
        clip2 = VideoFileClip(vid2_path)
        
        # 2. 統一影片寬高 (以第一部為準)
        w, h = clip1.size
        if clip2.size != clip1.size:
            print(">>> 正在調整第二部影片尺寸以匹配第一部...")
            clip2 = clip2.resize(newsize=(w, h))

        # 3. 製作個別影片的右上角標籤
        print(">>> 製作右上角標籤 (未完成/已完成)...")
        # 第一部影片：右上角顯示 "未完成"
        text_label1 = create_corner_text("故障影片", clip1.duration, position=('right', 'top'))
        video1_comp = CompositeVideoClip([clip1, text_label1])

        # 第二部影片：右上角顯示 "已完成"
        text_label2 = create_corner_text("已完成", clip2.duration, position=('right', 'top'))
        video2_comp = CompositeVideoClip([clip2, text_label2])

        # 4. 串接影片 (直接連接，中間無黑畫面)
        print(">>> 正在串接兩部影片...")
        base_concat = concatenate_videoclips([video1_comp, video2_comp])

        # 5. 製作全程顯示的文字與 Logo
        layers = [base_concat] # 底層是串接好的影片

        # 加入全程文字 (使用者輸入的那段)
        if global_television_text_content:
            print(f">>> 加入電視機產品名稱: {global_television_text_content}")
            texts_to_add.append({"text": global_television_text_content, "offset_y": -200, "color": "green"})

        if global_status_text_content:
            print(f">>> 加入電視機狀態文字: {global_status_text_content}")
            texts_to_add.append({"text": global_status_text_content, "offset_y": -50, "color": "blue"})


        for item in texts_to_add:
            align = item.get("align", "center")
            if align == "center":
                # 水平置中
                x = (clip1.w - TextClip(item["text"], font=FONT_PATH, fontsize=item.get("fontsize", 80)).w) / 2
            elif align == "left":
                # 靠左
                x = 0  # 距左邊 5px
            else:
                x = (clip1.w - TextClip(item["text"], font=FONT_PATH, fontsize=item.get("fontsize", 80)).w) / 2
            
            txt_clip = create_product_text(
                text=item["text"],
                duration=base_concat.duration,
                video_clip=clip1,
                offset_y=item.get("offset_y", 0),
                color=item.get("color", "white"),
                fontsize=item.get("fontsize", 80),
                x_pos=x  # 新增 x_pos 參數
            )
            layers.append(txt_clip)

        # 加入 Logo
        if os.path.exists(LOGO_FILENAME):
            print(">>> 加入右下角 Logo...")
            logo = ImageClip(LOGO_FILENAME)
            logo_width = w * 0.15
            logo = logo.resize(width=logo_width)
            # 設定 Logo 位置與持續時間
            logo = logo.set_position(lambda t: (w - logo.w - 20, h - logo.h - 20))  # 右下角，距離邊緣20px
            logo = logo.set_duration(base_concat.duration)
            layers.append(logo)

        # 6. 合成最終影片
        print(">>> 正在合成最終圖層...")
        final_video = CompositeVideoClip(layers)

        # 7. 輸出
        print(f">>> 正在輸出檔案至 {model2}...")
        final_video.write_videofile(f"1_{model2}_合併完成.mp4", codec='libx264', audio_codec='aac', fps=24)
        
        print(">>> 全部完成！")

    except Exception as e:
        print(f"\n======== 發生錯誤 ========")
        print(f"錯誤訊息: {e}")
        print("============================")
        print("常見解法：")
        print("1. 確保已安裝 ImageMagick (brew install imagemagick)")
        print("2. 檢查中文字型是否存在 (Mac 預設 'Arial Unicode MS')")
        print("3. 如果報錯 ImageMagick binary not found，請確認 moviepy 設定檔指向正確的 convert 路徑")

if __name__ == "__main__":
    print("=== 影片合併與標籤製作工具 ===")
    print(">>> 請準備好包含影片的資料夾，並確認影片檔名格式正確")
    print(">>> 影片檔名範例: 型號_問題_未完成.mp4, 型號_問題_已完成.mp4")
    print(">>> 程式將會走訪指定資料夾下的所有子資料夾，尋找並處理影片")
    print(">>> 處理完影片後會生成1_型號_合併完成.mp4的檔案")
    print(">>> 執行過程中請勿終止城市，以免產生不完整的檔案")
    # base_folder = input(">>> 請輸入資料夾位置: ")
    # input(">>> 按下任意鍵開始處理所有資料夾中的影片...")
    # 隱藏 Tkinter 主視窗
    root = tk.Tk()
    root.withdraw()

    # 選擇資料夾
    base_folder = filedialog.askdirectory(title="請選擇資料夾")
    if not base_folder:
        print("沒有選擇資料夾，程式結束")
        sys.exit(0)

    try:
        process_all_folders(base_folder)
    except Exception as e:
        print("程式發生錯誤：", e)
        traceback.print_exc()
    finally:
        input("程式結束，按任意鍵退出...")