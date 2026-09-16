---
name: coconut-sticker-maker
description: Use when turning hand-drawn coconut character sheets (椰子貼圖／小島居民) into separate finished sticker PNGs matching 第一版貼圖, or producing later numbered editions from those sketches. Not for merely cropping a scan or unrelated sticker styles.
---

# 椰子手稿轉同款貼圖

將手稿中的獨立構圖重新彩繪為同系列 PNG；不是裁切、去背或逐像素重建第一版。AI 重繪不保證和既有作品逐像素相同。要重做第一版13個既有主題時，先讀 [references/first-edition.md](references/first-edition.md) 的實際對照；不要誤稱原稿可唯一決定全部既有台詞。

## 已驗證的風格

先用 `view_image` 看輸入手稿與至少一張相關的 `assets/` 參考圖。
- 青綠色橢圓／水滴椰子；需要成熟椰子時用棕金色。短枝條手腳、可愛圓眼、紅潤臉頰。
- 圓潤粗黑描線、輕水彩／紙感上色，角色及字都有乾淨厚白外框。
- 第一版是 **不透明純黑背景 RGB PNG**，不是透明 PNG。沿用黑底，除非使用者另外要求透明。
- 一張檔案一個構圖；白外框、手腳、道具、文字完整入鏡，四邊留約 6–8% 安全空間；長邊至少 1024 px。不擅自改為 LINE 上架尺寸、附主圖或上傳。

參考圖：`assets/green-coconut.png`（一般角色）、`assets/brown-coconut.png`（成熟椰子／墨鏡）、`assets/costume-coconut.png`（裝扮與道具）。只借用風格，不複製參考圖的動作或文案。

## 操作流程

1. 清點源圖和目的資料夾。保留原始圖及既有版本，不覆寫已存在的成品。
2. 逐構圖建立目的資料夾的 `manifest.json`，欄位見 [references/manifest.md](references/manifest.md)。以原稿圈號排序；沒有連續圈號時，按稿面分區記錄位置再排序。不要拿最大圈號當數量。
3. 區分真正要印的文字與備註：排除日期、頁碼、圈號、箭頭、品牌筆記及「同18」「加線條」等製作指示。斜線分隔的替代文案不可全部塞進成品；必要時選一個並記錄。關鍵字看不清時問使用者，不默默改寫。`椰` 的諧音保留。
4. 先跑 `sticker_pack.py prompt MANIFEST ID` 取得單張完整提示。用內建 `image_gen.imagegen`，每張獨立呼叫；傳原稿及一至兩張適合的風格圖作 `referenced_image_paths`。有本機路徑時不使用 `num_last_images_to_include`。產圖前先看過所用參考圖。
5. 成圖後目視比對角色、文字（逐字）、主要動作、白邊、黑底、完整留白；不合格只針對該張修正。用 `sticker_pack.py record MANIFEST ID GENERATED_PATH` 保存工具實際輸出的 PNG 至 `01.png`、`02.png`…，並保留來源與完整 prompt。這個 helper **只複製和檢查檔案，不改圖**。
6. 檔案可用但尚未目視檢查時不能填寫 `visual_checked=true`。目視通過後可在 manifest 該項填 `visual_checked=true` 與 `visual_notes`；若文字有疑慮記為未通過。
7. 跑 `sticker_pack.py verify MANIFEST`；數量、檔名、PNG、尺寸、邊界、雜湊、黑底與目視狀態全過才稱整版完成。工具失敗時保存 pending/error 狀態，回報實際完成數，不拿草稿裁切圖冒充重繪成品。

## 執行與續作

```powershell
$tool = "$HOME\.codex\skills\coconut-sticker-maker\scripts\sticker_pack.py"
python $tool prompt 'C:\完整路徑\第二版貼圖\manifest.json' 1
python $tool record 'C:\完整路徑\第二版貼圖\manifest.json' 1 'C:\工具回傳\實際成圖.png'
python $tool verify 'C:\完整路徑\第二版貼圖\manifest.json'
```

需要 Python 3.11+ 及 Pillow；沒有 Pillow 可用 `uv run <script> ...`（內含依賴宣告）。本機 helper 不呼叫付費 API；圖片使用內建 image_gen，不要求 API key，不改走自製影像演算法。

續作先查 manifest 和實際檔案，只補缺圖；不要重生已驗收項。若有多個獨立版本且可用 subagents，可每位負責一個版本（不共寫同一份 manifest）；主代理仍要核對結果。`verify` 的檔案檢查不能替代目視／中文字校對。

交付目的資料夾路徑、張數與至少一张預覽，說明黑底不是透明、是否仍有待確認文字。只在使用者要求透明或另種風格時偏離上述既有成品規格。
