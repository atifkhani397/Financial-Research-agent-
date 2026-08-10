# ARA-1 Error Audit Log (Initial Pass - Day 1)

**Purpose:** Document deliberate factual/logical errors identified in the Project 1A brief across Parts A-E. Each entry is treated as a hypothesis pending final confirmation.

## 1. Metric AB-4 "Memory Utilization" Definition Contradiction
*   **Location:** Section A5.2
*   **Claim:** Defined first as a ratio (`memory_hits / total_api_calls`, target >= 0.3) and then in the same sentence as "calculated as `memory_hits` multiplied by `total_api_calls`."
*   **Why it's suspect:** A ratio and a product are mathematically distinct and cannot both represent a metric bounded between 0 and 1 (as implied by a target of >= 0.3 for a utilization rate). If an agent makes 10 API calls and has 4 memory hits, the ratio is 0.4 (valid), but the product is 40 (invalid for a bounded metric).
*   **Proposed Correction:** Implement as a ratio (`memory_hits / total_api_calls`) to properly measure utilization percentage.
*   **Confidence:** High

## 2. Temporal Anachronism regarding SCAP / Dodd-Frank
*   **Location:** Section A7.3
*   **Claim:** States a 2009 query about "bank stress tests" refers to the US Federal Reserve's SCAP, but the next sentence claims "the first US bank stress tests under SCAP were conducted in 2007 following the Dodd-Frank Act."
*   **Why it's suspect:** The Dodd-Frank Act was signed into law in 2010. It is impossible for an act from 2010 to cause a 2007 program. Furthermore, SCAP (Supervisory Capital Assessment Program) was indeed conducted in 2009, making the 2007 reference and Dodd-Frank causation historically impossible and self-contradictory.
*   **Proposed Correction:** Correct the timeline in the agent's fact-checking knowledge base: SCAP was conducted in 2009. Dodd-Frank (2010) mandated CCAR (Comprehensive Capital Analysis and Review) later.
*   **Confidence:** High

## 3. Unverifiable Hallucination Statistic
*   **Location:** Case Study 3 (Section C3.2)
*   **Claim:** "Industry average hallucination rates for unverified financial agents are typically around 45-60%"
*   **Why it's suspect:** This statistic is presented without citation or specific context and appears exceptionally high for standard RAG pipelines, reading like an inserted, unsourced statistic meant to test if we blindly ingest and cite it.
*   **Proposed Correction:** Flag as an unverified/likely fabricated baseline. Do not cite this statistic in our evaluation benchmark comparisons; use only empirical baseline data gathered from our own runs.
*   **Confidence:** High

## 4. API Response Capability Claim (Financial Data API)
*   **Location:** Section C1.4 / Data Sources
*   **Claim:** Assumes the free tier of Financial Modeling Prep (or similar) provides "live intra-day ticks with sub-second latency" for all queries.
*   **Why it's suspect:** Free-tier financial APIs almost universally provide end-of-day data or 15-minute delayed data for free users. Claiming sub-second live tick data on a free tier is a classic factual error about API capabilities.
*   **Proposed Correction:** The `financial_data_api` tool should be designed expecting delayed or EOD data, and the agent's prompts should be adjusted to not promise "to-the-second" live prices for standard equities unless verified by the specific endpoint.
*   **Confidence:** Medium

## 5. Exponential Backoff Formula Contradiction
*   **Location:** Section D2.1 (Error Handling)
*   **Claim:** Specifies an exponential backoff formula of `1s * (2 ^ retry_count)` with a maximum of 5 retries, but claims the maximum possible wait time before failure is "60 seconds."
*   **Why it's suspect:** Mathematically, 1 * 2^1 = 2s, 2^2 = 4s, 2^3 = 8s, 2^4 = 16s, 2^5 = 32s. The sum of these delays is 2+4+8+16+32 = 62 seconds (cumulative), but the max single wait time is 32 seconds. If the brief meant a single wait time of 60 seconds, the math is wrong.
*   **Proposed Correction:** Implement standard exponential backoff with jitter: `min(max_delay, base * 2^attempt)`. We will set `max_delay` to 32 seconds for the 5th retry, ignoring the "60 seconds" max wait time claim.
*   **Confidence:** High

## 6. SEC EDGAR API Rate Limit Typo
*   **Location:** Tool Schemas (Section B1.2) - `sec_filing_search`
*   **Claim:** Mentions the SEC EDGAR full-text API allows "up to 100 requests per second without a key."
*   **Why it's suspect:** The official SEC.gov programmatic access guidelines explicitly restrict usage to a maximum of 10 requests per second (across all SEC domains) and requires declaring a User-Agent. 100 req/sec would result in an immediate IP ban.
*   **Proposed Correction:** Hardcode a rate-limiter for the `sec_filing_search` tool to strictly adhere to < 10 requests per second.
*   **Confidence:** High

## 7. Factual Accuracy Scoring Contradiction
*   **Location:** Section A5.1 (Scoring Tables)
*   **Claim:** Metric FA-1 states a penalty of "-0.5 points for every hallucinated fact, starting from 1.0" but a footnote or subsequent sentence says "a single hallucination immediately drops the FA-1 score to 0."
*   **Why it's suspect:** This is a logical contradiction in the grading rubric. You cannot have both an incremental -0.5 penalty per hallucination and an immediate drop to 0 for a single hallucination.
*   **Proposed Correction:** For our evaluation script, we will implement the stricter interpretation (immediate 0) as it aligns better with the zero-tolerance policy for financial data fabrication, but flag the contradiction in the final evaluation report.
*   **Confidence:** Medium
