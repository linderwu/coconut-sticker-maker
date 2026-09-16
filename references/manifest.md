# Manifest

Store one `manifest.json` inside each output folder. File names are sequential within that folder, independent of source drawing numbers. All external file paths are absolute. Do not reuse the same manifest concurrently.

```json
{
  "edition": "第二版貼圖",
  "source": "C:\\path\\source.jpg",
  "source_sha256": "actual SHA256",
  "background": "black",
  "items": [
    {
      "id": 1,
      "source_id": "19",
      "source_position": "左上",
      "caption": "你肩負著我們的未來",
      "scene": "椰子肩負責任，頭頂土產的思考泡泡",
      "notes": "Render 土產 inside the thought bubble only.",
      "status": "pending",
      "visual_checked": false
    }
  ]
}
```

`caption` is the exact approved display text, including line breaks or punctuation. It may be empty for a deliberately text-free reaction. Put secondary displayed labels verbatim in `scene`, distinguish them from non-rendered `notes`. The prompt adds common style constraints. After image generation `record` sets `file`, `generated_path`, `sha256`, `width`, `height`, `mode`, `prompt`, and `status=generated`. It does not set visual approval. A human or image-capable agent must inspect the actual PNG and update `visual_checked` and `visual_notes` truthfully.

`verify` reports errors for missing/extra numbered PNGs, gaps/duplicates, source changes, corrupt PNGs, altered hashes, too-small canvases, nonopaque background, nonblack borders, blank images and unreviewed items. It cannot prove caption correctness or character fidelity. Final PNGs keep the image tool's dimensions; there is no lossy resize or automatic background removal.
