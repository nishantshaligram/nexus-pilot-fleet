# Architecture: Two-Key Triad Consensus Protocol

Fleet eliminates single-agent hallucinations by separating duties into an independent **Triad Lifecycle**.

---

## 1. The Triad Roles

1. **Author Agent (Coder):**
   - Model Tier: `gemini-1.5-flash` / `claude-3-5-haiku`
   - Role: Implements business logic and drafts initial tests in its isolated worktree.
2. **Reviewer Agent (Security & Architecture Auditor):**
   - Model Tier: `gemini-1.5-pro` / `claude-3-5-sonnet`
   - Role: Audits code diffs against project conventions, security policies (OWASP, SQL injection, token leaks), and grants **Key 1**.
3. **Verifier Agent (Sandbox Test Runner):**
   - Model Tier: `gemini-2.0-flash`
   - Role: Compiles code and executes automated test suites in a clean sandbox. Verification succeeds only if exit code is `0`, granting **Key 2**.

---

## 2. State Machine

```text
[PENDING]
    │ (Dependencies satisfied)
    ▼
[IN_PROGRESS] (Author writing code in worktree)
    │ (submit_task_for_review)
    ▼
[REVIEW] (Reviewer auditing diff)
    ├──(request_task_revisions)──▶ [IN_PROGRESS]
    │ (approve_review_key1)
    ▼
[VERIFYING] (Verifier executing test suite)
    ├──(test failure)────────────▶ [IN_PROGRESS]
    │ (verify_tests_key2)
    ▼
[MERGED] (Both Key 1 & Key 2 granted -> Integrated)
```
