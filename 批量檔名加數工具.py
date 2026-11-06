# -*- coding: utf-8 -*-
import os
import sys
import re  # 匯入正則表達式模組，用來靈活抓取數字

def universal_batch_rename(folder_path, number_to_add):
    """
    通用版批次檔名加數工具。
    不限制檔名開頭，只要主檔名是以「數字結尾」的檔案，
    就會將該數字加上指定的數值。

    邏輯：
    - 'DJI_0001.JPG' + 1000 -> 'DJI_1001.JPG'
    - 'IMG_5500.png' + 100  -> 'IMG_5600.png'
    - 'render_v2_005.jpg' + 10 -> 'render_v2_015.jpg'
    - '001.mp4' + 50 -> '051.mp4'
    """
    print(f"--- 開始處理 ---")
    print(f"目標資料夾：{folder_path}")
    print(f"數字增量：{number_to_add}")
    print("-" * 30)

    try:
        if not os.path.isdir(folder_path):
            print(f"錯誤：找不到資料夾 '{folder_path}'。")
            return

        files = os.listdir(folder_path)
        # 排序檔案，確保處理順序符合邏輯
        files.sort()
        
        total_files = len(files)
        renamed_count = 0
        skipped_count = 0

        # 正則表達式：
        # ^(.*?)  -> 群組1: 抓取開頭的任意字元 (非貪婪模式)，這就是前綴
        # (\d+)$  -> 群組2: 抓取結尾的一串數字，這就是我們要改的部分
        pattern = re.compile(r'^(.*?)(\d+)$')

        for filename in files:
            # 排除系統檔案或隱藏檔
            if filename.startswith('.'):
                continue

            base_name, extension = os.path.splitext(filename)

            # 使用正則表達式去匹配檔名
            match = pattern.search(base_name)

            if match:
                # 如果匹配成功 (代表檔名結尾有數字)
                prefix_part = match.group(1) # 數字前面的文字 (可能為空)
                number_part = match.group(2) # 抓到的數字字串

                try:
                    original_number = int(number_part)
                    new_number = original_number + number_to_add
                    
                    # 保持原本的位數補零 (Padding)
                    # 例如原本是 '001' (長度3)，變成 '1001' 時會自動擴展，但變成 '002' 時會保持3位
                    padding = len(number_part)
                    
                    # 組合新檔名：前綴 + 新數字 + 副檔名
                    new_base_name = f"{prefix_part}{new_number:0{padding}d}"
                    new_filename = new_base_name + extension

                    old_filepath = os.path.join(folder_path, filename)
                    new_filepath = os.path.join(folder_path, new_filename)

                    # 檢查新檔名是否已存在
                    if os.path.exists(new_filepath):
                        print(f"跳過：'{filename}' -> 新檔名 '{new_filename}' 已存在。")
                        skipped_count += 1
                        continue
                    
                    # 執行改名
                    os.rename(old_filepath, new_filepath)
                    print(f"成功：'{filename}' -> '{new_filename}'")
                    renamed_count += 1

                except Exception as e:
                    print(f"錯誤：處理 '{filename}' 時發生問題：{e}")
                    skipped_count += 1
            else:
                # 如果檔名結尾不是數字 (例如 'Image.jpg' 或 'DJI_Test.mov')
                # 這裡選擇不報錯，僅在總結時統計，以免洗版
                # 如果您希望看到哪些檔案被忽略，可以把下面這行註解打開
                # print(f"忽略：'{filename}' (結尾沒有數字)")
                skipped_count += 1

        print("-" * 30)
        print(f"處理完成！")
        print(f"共掃描：{total_files} 個檔案")
        print(f"成功修改：{renamed_count} 個")
        print(f"未修改/忽略：{skipped_count} 個 (包含非數字結尾的檔案)")
        
        if renamed_count == 0:
            print("\n*** 注意：沒有任何檔案被修改 ***")
            print("請確認您的檔案名稱結尾是否包含數字 (例如 Photo001.jpg)。")

    except Exception as e:
        print(f"發生未預期的錯誤：{e}")

# --- 主程式區 ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_folder = sys.argv[1]
    else:
        # 考慮到 Windows 路徑可能包含引號，做一些清理
        raw_input = input("請輸入照片資料夾路徑：").strip()
        target_folder = raw_input.strip('"').strip("'")

    while True:
        try:
            offset_str = input(f"請輸入要增加的數字 (例如 100)：")
            if not offset_str: continue
            offset_number = int(offset_str)
            break
        except ValueError:
            print("請輸入有效的整數。")

    universal_batch_rename(target_folder, offset_number)
    
    print("\n按 Enter 鍵結束...")
    input()