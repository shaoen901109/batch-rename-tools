English | [繁體中文](README.zh-TW.md)

> 📖 **Step-by-step tutorial (Traditional Chinese):** https://shao-en.com/blog/batch-rename-tools-guide.html — not sure how to set it up? Hand the article to Claude or ChatGPT and let it walk you through.

# batch-rename-tools

A small set of standalone Python scripts for batch-renaming and cleaning up files. Each script is interactive (it asks for a folder path and options) and uses only the Python standard library. The script file names and prompts are in Traditional Chinese.

> **Warning:** these scripts rename (or delete) real files and most cannot be undone. Back up your folder first.

## Scripts

- **批量照片檔名按時間命名.py** — Renames the images in one folder (not subfolders) to sequential numbers, ordered by last-modified time from oldest to newest. You enter the start number and the number of digits (e.g. 5 gives `00001.jpg`). Recognised extensions: jpg, jpeg, png, bmp, tif, tiff, dng, cr2, arw, nef, webp. Shows the first and last file and asks for `y` before renaming. If a target name already exists, that file is skipped.
- **批量照片檔名按時間命名_由新到舊.py** — Same, but newest first: the newest photo gets the start number. At the confirmation prompt, `y` starts, `r` reverses the order (oldest first), anything else cancels.
- **批量檔名加數工具.py** — For files whose base name ends in digits, adds a number to that trailing number while keeping the zero-padding width (e.g. `DJI_0001.JPG` + 1000 becomes `DJI_1001.JPG`). Takes the folder as the first command-line argument or asks for it, then asks for the amount to add. Files without trailing digits, and names that would collide with an existing file, are skipped. Hidden files (starting with `.`) are ignored. There is no confirmation step.
- **檔名長度截斷工具.py** — Scans a folder and all subfolders for file and folder names longer than a limit (default 255; the prompt suggests 143 for encrypted shared folders) and shortens them, keeping the extension. Length can be counted in UTF-8 bytes (default) or characters. Name collisions get `~1`, `~2`, ... appended. It shows a preview, asks for `y` before renaming, and writes a CSV log (`檔名截斷紀錄_<timestamp>.csv`) next to the script. Written with Synology Drive Client file-name limits in mind.
- **刪除重複檔案.py** — Recursively deletes files whose base name ends in ` - 複製` or ` (number)` **only if** the original file (same name without that suffix and with the same extension) exists in the same folder. Deletion is permanent (`os.remove`), with no preview or confirmation.

## Requirements

- Python 3 (standard library only, no packages to install).
- Windows is the intended platform (the truncation tool adds the `\\?\` long-path prefix on Windows); the other scripts use plain `os` calls.

## Usage

```
python 批量照片檔名按時間命名.py
python 批量照片檔名按時間命名_由新到舊.py
python 批量檔名加數工具.py [folder]
python 檔名長度截斷工具.py
python 刪除重複檔案.py
```

Run a script, then follow the prompts. Paths wrapped in quotes (as copied from Explorer) are accepted by most scripts.

## Notes

- Back up first. Renames and deletions are not undone automatically.
- Photo scripts sort by last-modified time; copying files can change that, so check the first/last preview.
- Try on a copy of a folder before using on real data.

## Credits

This tool uses only the Python standard library, no third-party packages.

Developed with the help of [Claude Code](https://claude.com/claude-code) (Anthropic).

## Author

- Website: https://shaoenstudio.com
- Email: shaoenstudio@gmail.com
- GitHub: [@shaoen901109](https://github.com/shaoen901109)

## License

MIT, see [LICENSE](LICENSE).
