import os
import sys
import time

def get_image_files(folder_path):
    """
    取得資料夾內所有圖片檔案，並包含完整路徑
    """
    # 定義常見的圖片格式 (包含無人機與相機常見的 RAW 檔)
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.dng', '.cr2', '.arw', '.nef', '.webp')
    
    files = []
    # 掃描資料夾
    try:
        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(valid_extensions):
                    files.append(entry.path)
    except FileNotFoundError:
        print(f"錯誤：找不到資料夾路徑 '{folder_path}'")
        sys.exit()
    except PermissionError:
        print(f"錯誤：沒有權限存取資料夾 '{folder_path}'")
        sys.exit()
        
    return files

def rename_images():
    print("=== 照片依時間排序 (由新到舊) 批次重新命名工具 ===")
    print("說明：此工具會依照檔案的「最後修改時間」排序。")
    print("規則：時間【最新】的照片 = 起始號碼 (例如 1)，越舊的照片號碼越大。")
    print("警告：此操作不可逆，建議先備份資料夾內的照片！\n")

    # 1. 獲取使用者輸入
    folder_path = input("請輸入照片資料夾路徑 (例如 D:\\Project\\Site_Analysis): ").strip('"') # 去除可能複製到的引號
    
    if not os.path.exists(folder_path):
        print("錯誤：資料夾不存在！")
        return

    try:
        start_num = int(input("請輸入起始號碼 (例如 1): "))
        padding = int(input("請輸入編號位數 (例如 5，代表 00001): "))
    except ValueError:
        print("錯誤：請輸入有效的整數數字！")
        return

    # 2. 獲取檔案並排序
    print("\n正在掃描檔案...")
    files = get_image_files(folder_path)
    
    if not files:
        print("該資料夾中沒有找到圖片檔案。")
        return

    # 依據檔案的最後修改時間 (getmtime) 進行排序
    # 設定 reverse=True，變成 大 (新) -> 小 (舊)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    count = len(files)
    print(f"共找到 {count} 張照片。")

    # 顯示第一張與最後一張的詳細資訊供確認
    if count > 0:
        t_first = os.path.getmtime(files[0])
        t_last = os.path.getmtime(files[-1])
        date_first = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t_first))
        date_last = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t_last))

        print(f"\n[預覽排序結果 (由新到舊)]")
        print(f"第一張 (最新 -> {start_num:0{padding}d}): {os.path.basename(files[0])}")
        print(f"  └─ 修改時間: {date_first}")
        print(f"最後一張 (最舊 -> {start_num+count-1:0{padding}d}): {os.path.basename(files[-1])}")
        print(f"  └─ 修改時間: {date_last}")
    
    confirm = input("\n確認排序正確並開始命名嗎？(輸入 y 開始 / r 反轉順序變成舊到新 / 其他鍵取消): ")
    
    if confirm.lower() == 'r':
        files.reverse()
        print("已切換順序！(現在變為：舊 -> 新)")
        # 更新預覽資訊給使用者看
        print(f"現在第一張是 (最舊): {os.path.basename(files[0])}")
        
    elif confirm.lower() != 'y':
        print("已取消操作。")
        return

    # 3. 執行重新命名
    print("\n開始執行重新命名...")
    renamed_count = 0
    current_num = start_num

    for old_path in files:
        folder = os.path.dirname(old_path)
        filename = os.path.basename(old_path)
        file_ext = os.path.splitext(filename)[1] # 取得副檔名 (例如 .jpg)
        
        # 格式化新檔名，例如：00001.jpg
        new_filename = f"{current_num:0{padding}d}{file_ext}"
        new_path = os.path.join(folder, new_filename)

        # 避免新檔名跟舊檔名一樣
        if old_path == new_path:
            print(f"[跳過] {filename} 檔名已符合")
            current_num += 1
            continue

        # 檢查新檔名是否已經存在
        if os.path.exists(new_path):
            print(f"[錯誤] 無法重新命名 {filename} -> {new_filename}，因為目標檔案已存在。")
        else:
            try:
                os.rename(old_path, new_path)
                renamed_count += 1
            except Exception as e:
                print(f"[失敗] {filename}: {e}")
        
        current_num += 1

    print(f"\n完成！成功重新命名 {renamed_count} 張照片。")

if __name__ == "__main__":
    rename_images()
    input("\n按 Enter 鍵離開...")