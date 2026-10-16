# Global art news intake (V1)

GitHub Actions runs at **08:17, 14:17, 20:17 Europe/Istanbul** and can be manually triggered.

- Sources: `editorial/radar/sources.json` — candidate RSS/Atom feeds; availability must be validated by the first run.
- Collector: `scripts/collect_art_news.py` (Python standard library).
- Output: `editorial/radar/inbox.json` — a **research inbox**, not publishable articles.
- URL hash deduplication, original title/summary/link, source attribution, discovery timestamp, non-approval flags.
- No images downloaded. No copyrighted article bodies copied. No automatic site updates.
- A failed source does not stop other feeds. Errors are printed in Actions logs.
- Source feed availability, GitHub Actions write permissions, and first successful scheduled run **are not yet confirmed**.
- GitHub Pages is separate; content in this inbox must never be treated as editorially approved.
- Some feeds may reject automated fetching; remove or replace invalid sources after inspecting logs.

**Manual test:** Repository → Actions → Art news radar (editorial inbox) → Run workflow. Verify the run log and `editorial/radar/inbox.json`. If git push is denied, repository Settings → Actions → General → Workflow permissions must permit write access.
