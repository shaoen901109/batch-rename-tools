# -*- coding: utf-8 -*-
"""
檔名長度截斷工具（for Synology Drive Client）

掃描指定資料夾底下所有檔案與子資料夾，把名稱超過上限的部分刪掉。
- 檔案會保留副檔名，只截主檔名
- 截斷後若與同資料夾的其他名稱撞名，自動加上 ~1、~2 ...
- 先列出預覽，確認後才真的改名；改名結果會寫成 CSV 紀錄檔
"""
import csv
import os
import sys
from datetime import datetime

DEFAULT_LIMIT = 255
MAX_EXT_LENGTH = 32   # 超過這個長度就不當成副檔名
PREVIEW_COUNT = 30


def to_long_path(path):
    """Windows 加上 \\\\?\\ 前綴，避開 260 字元的路徑長度限制。"""
    path = os.path.abspath(path)
    if os.name != "nt" or path.startswith("\\\\?\\"):
        return path
    if path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path[2:]
    return "\\\\?\\" + path


def to_display_path(path):
    if path.startswith("\\\\?\\UNC\\"):
        return "\\\\" + path[8:]
    if path.startswith("\\\\?\\"):
        return path[4:]
    return path


def measure(text, by_bytes):
    if by_bytes:
        return len(text.encode("utf-8", "surrogatepass"))
    return len(text)


def cut(text, limit, by_bytes):
    """從頭保留不超過 limit 的部分，不會把一個字切成兩半。"""
    if limit <= 0:
        return ""
    if not by_bytes:
        return text[:limit]
    used = 0
    for i, ch in enumerate(text):
        used += len(ch.encode("utf-8", "surrogatepass"))
        if used > limit:
            return text[:i]
    return text


def shorten(name, limit, by_bytes, is_dir, tail=""):
    stem, ext = (name, "") if is_dir else os.path.splitext(name)
    if len(ext) > MAX_EXT_LENGTH or " " in ext:
        stem, ext = name, ""
    room = limit - measure(ext, by_bytes) - measure(tail, by_bytes)
    new_name = cut(stem, room, by_bytes) + tail + ext
    # Windows 不允許名稱以空白或句點結尾
    return new_name.rstrip(" .")


def build_plan(root, limit, by_bytes):
    plan, errors, scanned = [], [], 0
    # 由深到淺走訪，之後照同樣順序改名，上層資料夾改名才不會讓下層路徑失效
    for folder, dirnames, filenames in os.walk(root, topdown=False, onerror=errors.append):
        taken = {n.casefold() for n in dirnames + filenames}
        entries = [(d, True) for d in dirnames] + [(f, False) for f in filenames]
        for name, is_dir in entries:
            scanned += 1
            if scanned % 2000 == 0:
                print(f"\r  已掃描 {scanned} 個項目...", end="", flush=True)
            if measure(name, by_bytes) <= limit:
                continue
            taken.discard(name.casefold())
            new_name = shorten(name, limit, by_bytes, is_dir)
            n = 0
            while not new_name or new_name.casefold() in taken:
                n += 1
                new_name = shorten(name, limit, by_bytes, is_dir, f"~{n}")
            taken.add(new_name.casefold())
            plan.append((folder, name, new_name, is_dir))
    print(f"\r  已掃描 {scanned} 個項目。    ")
    return plan, errors


def brief(name):
    return name if len(name) <= 60 else name[:35] + " … " + name[-20:]


def show_plan(plan, root, by_bytes, count):
    unit = "位元組" if by_bytes else "字元"
    for i, (folder, old, new, is_dir) in enumerate(plan[:count], 1):
        rel = os.path.relpath(folder, root)
        print(f"\n{i}. [{'資料夾' if is_dir else '檔案'}] 位於：{brief(rel)}")
        print(f"   原：{brief(old)}（{measure(old, by_bytes)} {unit}）")
        print(f"   新：{brief(new)}（{measure(new, by_bytes)} {unit}）")
    if count < len(plan):
        print(f"\n... 還有 {len(plan) - count} 項未顯示")


def apply_plan(plan):
    results = []
    for folder, old, new, is_dir in plan:
        try:
            os.rename(os.path.join(folder, old), os.path.join(folder, new))
            status = "成功"
        except OSError as e:
            status = f"失敗：{e}"
        results.append((to_display_path(folder), "資料夾" if is_dir else "檔案", old, new, status))
    return results


def write_log(results):
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(log_dir, f"檔名截斷紀錄_{datetime.now():%Y%m%d_%H%M%S}.csv")
    with open(log_path, "w", newline="", encoding="utf-8-sig", errors="replace") as f:
        writer = csv.writer(f)
        writer.writerow(["所在資料夾", "類型", "原名稱", "新名稱", "結果"])
        writer.writerows(results)
    return log_path


def ask_folder():
    while True:
        raw = input("請輸入要掃描的資料夾路徑：").strip().strip('"').strip("'")
        if not raw:
            continue
        root = to_long_path(raw)
        if os.path.isdir(root):
            return root
        print("  找不到這個資料夾，請重新輸入。")


def ask_mode():
    print("\n長度的計算方式：")
    print("  [1] UTF-8 位元組（預設。NAS 檔案系統實際是以位元組計算，中文字一個佔 3 位元組）")
    print("  [2] 字元數")
    while True:
        raw = input("請選擇 (1/2，直接 Enter = 1)：").strip()
        if raw in ("", "1"):
            return True
        if raw == "2":
            return False


def ask_limit():
    while True:
        raw = input(f"長度上限（直接 Enter = {DEFAULT_LIMIT}；加密共用資料夾請輸入 143）：").strip()
        if not raw:
            return DEFAULT_LIMIT
        if raw.isdigit() and int(raw) >= 16:
            return int(raw)
        print("  請輸入 16 以上的整數。")


def main():
    print("=== 檔名長度截斷工具（Synology Drive Client）===\n")
    root = ask_folder()
    by_bytes = ask_mode()
    limit = ask_limit()

    print(f"\n開始掃描：{to_display_path(root)}")
    plan, errors = build_plan(root, limit, by_bytes)

    if errors:
        print(f"\n有 {len(errors)} 個資料夾無法讀取（已略過）：")
        for e in errors[:10]:
            print(f"  {to_display_path(e.filename or '')}：{e.strerror}")

    if not plan:
        print("\n沒有任何名稱超過上限，不需要處理。")
        return

    print(f"\n共有 {len(plan)} 個名稱超過上限，預計修改如下：")
    show_plan(plan, root, by_bytes, PREVIEW_COUNT)

    while True:
        hint = "y = 執行改名 / a = 顯示全部 / 其他 = 取消" if len(plan) > PREVIEW_COUNT else "y = 執行改名 / 其他 = 取消"
        answer = input(f"\n確定要改名嗎？({hint})：").strip().lower()
        if answer == "a" and len(plan) > PREVIEW_COUNT:
            show_plan(plan, root, by_bytes, len(plan))
            continue
        break
    if answer != "y":
        print("已取消，沒有修改任何檔案。")
        return

    results = apply_plan(plan)
    failed = [r for r in results if r[4] != "成功"]
    print(f"\n完成：成功 {len(results) - len(failed)} 個，失敗 {len(failed)} 個。")
    for folder, kind, old, new, status in failed[:20]:
        print(f"  [{kind}] {brief(old)} → {status}")
    try:
        print(f"改名紀錄已存到：{write_log(results)}")
    except OSError as e:
        print(f"紀錄檔寫入失敗：{e}")


if __name__ == "__main__":
    # 檔名可能含有終端機編碼無法顯示的字元，避免 print 時直接當掉
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n已中止。")
