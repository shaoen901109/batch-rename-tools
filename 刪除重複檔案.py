
'''
此腳本用於刪除指定資料夾及其所有子資料夾中的多餘副本檔案。
這些檔案的檔名通常包含「 - 複製」或「 (數字)」等後綴。
'''
import os
import re

def remove_duplicate_files_recursive():
    """
    遞迴刪除指定資料夾及其子資料夾中的重複檔案。
    重複檔案是透過檔名後綴（如 ' - 複製' 或 ' (1)', ' (2)' 等）來識別的。
    """
    folder_path = input("請輸入要清理的資料夾路徑：")

    if not os.path.isdir(folder_path):
        print(f"錯誤：找不到資料夾 '{folder_path}'")
        return

    print(f"正在掃描資料夾及其所有子資料夾：{folder_path}")

    # 用於匹配 ' (數字)' 後綴的正規表達式
    copy_pattern = re.compile(r' \(\d+\)$')
    # Windows 檔案總管建立副本時使用的後綴
    copy_suffix = " - 複製"

    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            base_name, extension = os.path.splitext(filename)
            original_file_path = ""

            # 檢查是否以 ' - 複製' 結尾
            if base_name.endswith(copy_suffix):
                original_base_name = base_name[:-len(copy_suffix)]
                original_filename = original_base_name + extension
                original_file_path = os.path.join(dirpath, original_filename)

            # 檢查是否有 ' (數字)' 後綴
            else:
                match = copy_pattern.search(base_name)
                if match:
                    original_base_name = base_name[:match.start()]
                    original_filename = original_base_name + extension
                    original_file_path = os.path.join(dirpath, original_filename)

            # 如果找到了原始檔案，則刪除此重複檔案
            if original_file_path and os.path.exists(original_file_path):
                try:
                    os.remove(file_path)
                    print(f"已刪除重複檔案：{file_path}")
                except OSError as e:
                    print(f"刪除檔案 '{file_path}' 時發生錯誤：{e}")

    print("\n清理完成。")

if __name__ == "__main__":
    remove_duplicate_files_recursive()
