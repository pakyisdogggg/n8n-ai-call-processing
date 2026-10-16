# Technical review and honest status

These observations come from static inspection of the provided n8n JSON, not a full live test.

## Verified export facts

- 41 nodes, inactive workflow, no pinned execution data in the submitted file.
- The source filter checks whether trimmed `automation_status` is empty.
- A single-item loop branches into processing and returns item outcomes to the loop; the `done` output aggregates statistics.
- HTTP enrichment has a delayed retry branch and a manual-review fallback.
- A result is appended to Google Sheets before its source row is updated to `processed`.

## Findings / suggested changes before production

1. **Idempotency gap (high).** A successful `Append_Result` followed by failure of `Mark_Processed` can create a second destination row on a later retry. Filtering blank `automation_status` is not exactly-once protection. Prevent concurrent executions; use a durable source identifier and a reconciliation procedure.
2. **Incomplete error coverage (high).** HTTP enrichment has explicit retry/error routing, but the exported OpenAI and Google Sheets write nodes are not all provided with error fallbacks. A hard failure can interrupt a batch and leave rows in `processing`.
3. **Date reference in duplicate check (high).** In `Code | Check_Duplicate`, `$('If | Validate_Project').first().json.call_date` can reference the first item of that node's execution, instead of the current call in all circumstances. Prefer passing the current call date explicitly with the item being processed and test across multiple calls/dates.
4. **Status aggregation edge cases (medium).** Run statistics strips leading non-letter/non-number characters. That does not normalize `2️⃣дубль` (leading digit) or `🛑в стоп-лист` (extra `в`), so `duplicate` and `stop_list` can remain 0 despite successful processing. Use an explicit canonical mapping from display labels to status keys.
5. **Project classification ambiguity (medium).** The project-resolver prompt still contains `if multiple projects match, manual_review`, which may contradict later discussions about equivalent project names. Test the current reference list and document the intended tie-breaking rule.
6. **LLM prompt validation (medium).** An example in the supplied transcript-classification prompt omits a comma between `reason_code` and `reason_text` (an invalid JSON example). One output `Parse_Classification` fallback recovers from invalid results, but prompt examples should be corrected and model output validated.
7. **Unresolved technical errors in statistics (medium).** The DataTech error updater uses `automation_status=manual_review`; the shared `Set_Run_Result` classifies outcomes using that status. Therefore technical errors currently contribute to `manual_review`, not necessarily `errors`. The statistics schema should either count both or carry a distinct `run_result=error`.
8. **Client-name matching assumptions (medium).** The custom API parser assumes particular name layouts and prefers frequency/longest value. Validate on synthetic or permissioned test data; a common name is not necessarily the correct identity.
9. **Input and source row integrity (medium).** The `phone` is configured as Number and some expressions use `row_number`; changes in input schema, sorting or missing values can cause mismatches. Validate missing values before `.trim()`, and preserve phone strings where required.
10. **Source sheet importability (expected).** Live URLs and Sheets identifiers have deliberately been replaced with placeholders; the exported JSON must be configured before it can run.
11. **Wait and retry behavior (test).** A Wait node resumes execution and the retry request references an earlier call item. Confirm n8n item linking and body evaluation end-to-end, especially after error branches.
12. **Provider/capacity/consent (operations).** Verify the right to use customer data with the selected third-party APIs and any data-retention obligations; no real transcripts or identifiers are included in this portfolio package.

## Suggested test scenarios

- Empty `automation_status` enters the loop; `processed`, `manual_review`, `processing`, `error` do not.
- A missing phone or transcription leads to a source comment and manual review.
- A valid inbound-call project is resolved; an unknown project goes to manual review.
- A stop-list transcript takes precedence over a business duplicate.
- Same phone+project on the previous business day is marked business duplicate.
- Duplicate case across Friday→Monday; malformed dates; holidays (if specified by business).
- First enrichment request 503 then retry succeeds.
- First and second enrichment requests 503 → manually reviewed and next call proceeds.
- OpenAI invalid JSON → `INVALID_MODEL_RESPONSE` manual review.
- `Append_Result` succeeds but marking source processed fails → no blind append on retry.
- Unknown `processing` entries can be reconciled safely after crashes.
- Status reports include `2️⃣дубль` and `🛑в стоп-лист` accurately.

> Before publication: confirm rights to disclose business logic. Before production: add monitored error handling, no-overlap control and reliable write reconciliation.
