# YouTube Downloader 神器
## 本地運行．無限下載．絕無廣告

<img width="712" height="844" alt="截圖 2026-09-30 22 20 42" src="https://github.com/user-attachments/assets/c5375082-3653-478f-ba2c-e0cc687e90a1" />

## 📌 應用程式功能 (Features)
- **影片下載**：輸入 YouTube 網址即可輕鬆下載高畫質影片 (支援 MP4 格式)。
- **純音訊下載**：可選擇僅擷取音訊 (WAV 格式)，適合音樂、Podcast 收藏。
- **預覽功能**：自動解析網址並呈現影片縮圖及完整標題，確認無誤再下載。
- **彈性畫質選擇**：自動列出該影片所有可用的解析度，並為您標示推薦的最佳畫質。
- **自動化環境配置**：程式內建檢查並自動下載 FFmpeg 機制，免去繁瑣的終端機手動設定。

## ⚙️ 核心架構與特色 (Architecture & Highlights)
- **現代化 UI**：採用 Python 的 `customtkinter` 與 `tkinter` 打造，提供具設計感且直覺的圖形化使用者介面 (GUI)，並支援系統外觀主題。
- **強大的下載核心**：底層整合 `yt-dlp` 進行精準的影片資訊解析與高速下載，兼顧穩定性與速度。
- **多執行緒設計 (Multithreading)**：解析與下載任務皆在背景執行，確保主介面在作業時仍能流暢操作、不卡頓。
- **為 macOS 量身優化**：針對 macOS 用戶特別完善了依賴工具 (FFmpeg) 的自動下載與存取權限處理，並將下載好的檔案統一儲存至使用者的 `Downloads` 資料夾，隨裝即用。

## 📥 如何下載與安裝 (Installation)

### 步驟一：前往 Releases 頁面
進入 GitHub `Youtube_Downloader` 專案頁面後，選擇右側欄位的 **Releases**：
<img width="1839" height="1196" alt="截圖 2026-09-30 22 23 46" src="https://github.com/user-attachments/assets/72a9eb75-8c7a-494a-af3a-b9a3c41585c8" />

### 步驟二：下載 MacOS 專用的 .zip 壓縮檔
點擊最新版本 **Assets** 下的 `.zip` 檔案並進行下載：
<img width="1839" height="1196" alt="截圖 2026-09-30 22 25 29" src="https://github.com/user-attachments/assets/2c14995c-6809-4e0c-85a8-ac84ca31a57c" />

### 步驟三：解壓縮並安裝
下載完成後，解壓縮該 `.zip` 檔案，便會出現 `Youtube Downloader.app`。直接將其拖曳或複製到您的 `/Applications` (應用程式) 資料夾中即可開始使用！

---
*Developed by 蘇廷融*
