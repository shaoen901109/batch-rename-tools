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
    print("=== 照片依時間排序批次重新命名工具 ===")
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

    # 依據檔案的最後修改時間 (getmtime) 進行排序 (由舊到新)
    # 如果照片是剛複製進去的，修改時間可能會變，這時候可以用 getctime (建立時間)
    # 但在 Windows 上，複製檔案通常會更新建立時間而保留修改時間，故使用 getmtime 相對準確
    files.sort(key=lambda x: os.path.getmtime(x))

    count = len(files)
    print(f"共找到 {count} 張照片。")
    print(f"第一張 (最舊): {os.path.basename(files[0])}")
    print(f"最後一張 (最新): {os.path.basename(files[-1])}")
    
    confirm = input("\n確認要開始重新命名嗎？(輸入 y 開始，其他鍵取消): ")
    if confirm.lower() != 'y':
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

        # 避免新檔名跟舊檔名一樣 (剛好就是該號碼)
        if old_path == new_path:
            print(f"[跳過] {filename} 檔名已符合")
            current_num += 1
            continue

        # 檢查新檔名是否已經存在 (避免覆蓋)
        if os.path.exists(new_path):
            print(f"[錯誤] 無法重新命名 {filename} -> {new_filename}，因為目標檔案已存在。")
            # 這裡可以選擇停止或跳過，這裡選擇跳過以免破壞其他檔案
        else:
            try:
                os.rename(old_path, new_path)
                # 為了讓使用者看到進度，可以選擇性列印，大量檔案時建議註解掉下面這行
                # print(f"已更名: {filename} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"[失敗] {filename}: {e}")
        
        current_num += 1

    print(f"\n完成！成功重新命名 {renamed_count} 張照片。")

if __name__ == "__main__":
    rename_images()
    # 讓視窗停留，方便使用者看到結果
    input("\n按 Enter 鍵離開...")