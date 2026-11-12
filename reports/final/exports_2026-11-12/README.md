# Local draft exports — 12 November 2026

**DRAFT_FOR_AUTHOR_REVIEW / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

Open `CulinaryState_report_DRAFT.pdf` (10 pages) or `CulinaryState_slides_DRAFT.pdf` (13 slides). Matching standalone HTML is available. Contributions, actual presentation slot/length and final author edits remain pending. These files are reviewable drafts, not an approved submission. Original failed gates are preserved.

`manifest.json` binds source, HTML, PDF and extracted-text hashes, renderer versions and scope. `build_html.py` preserves the actual local HTML build script; run it from the project root with Markdown 3.7 at its recorded temporary dependency path only when creating a new dated export directory (change its output path first). PDFs were printed with Chrome headless, `--disable-background-networking --no-first-run --no-pdf-header-footer`, a new temporary `--user-data-dir`, and `--print-to-pdf` pointing to the local HTML. Never reuse a person's browser profile.

The v2 scan covers current Markdown, visible HTML and the byte-identical extracted PDF text copies here. There are zero 12-word matches against locally available adapter fields across 612,782 indexed recipe records plus four licensed paper texts. 177 Gutenberg segment texts are absent. No image/OCR, paraphrase or short-excerpt clearance is claimed. See `reports/s179/local_corpus_draft_text_scan_2026-11-12_v2.json` and manifest for precise hashes; changes require a new scan.

Local strict demo: use the project Python environment to run `python tools/run_local_demo_v2.py`. It binds `127.0.0.1:8765`, uses public-filtered data by default, and runs no model/server job. Exact declared condition context is not inferred; missing context refuses numeric retention output. The original demo launcher remains available for historical reproduction.
