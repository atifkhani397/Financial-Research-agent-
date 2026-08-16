# Project Rules — ARA-1 Financial Research Agent

All research reports synthesized by the agent MUST follow `rules.md`:
1. No unicode hyphens (`\u2011`, `\u2010`), en dashes (`–`), or em dashes (`—`). Use standard ASCII hyphens (`-`).
2. No black square dots or non-standard bullet symbols (`•`, `■`, `▪`). Use standard Markdown bullets (`- `).
3. No curly quotes (`‘’`, `“”`), ellipses (`…`), zero-width spaces (`\u200b`), or thin spaces (`\u202f`).
4. Clean ASCII formatting for numbers, currency (`$`), and percentages (`%`).
5. Proper Markdown heading hierarchy (`#`, `##`, `###`).
6. All quantitative metrics formatted in clean Markdown tables.
7. Zero hallucinations — state `Data not available` if missing.
8. No raw JSON, Python dicts, or tool call trace signatures in output.
