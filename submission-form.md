# Submission Form — Task 1 V3

## Your Info

- **Name:** Kuruva Surendra Kumar
- **Email:** surendrakuruva571@gmail.com
- **Track:** Forward Deployed Engineer
- **Dataset:** Set A (Vireo Audio)

## Repository

- **Public GitHub URL:** https://github.com/Surendra571/vireo-support-intelligence
- **Commit hash of submitted version:** 76fbb5a9ddd30ee11b7c799b92de9721212f6566

## Video Walkthrough

- **Link:** https://drive.google.com/file/d/1aUoMC1mVpkz-gjy55qo1gMWDgVweaI8s/view?usp=sharing
- **Duration:** 3:56

## Business Goal

- **What is your stated business goal? (must be a number + money):**

  Reduce repeat-contact cases identified by the Method A analytical proxy by a measurable percentage while monitoring the associated direct support-handling cost.

  One modeled scenario is a **20% reduction** in Method A repeat-contact cases, from **1,412 baseline cases to approximately 1,130 cases**, corresponding to **₹73,406 of modeled potential avoided handling cost over the 18-month historical baseline**.

- **Baseline value:**
  
  **1,412 Method A repeat-contact proxy cases (11.89% of 11,875 deduplicated tickets), associated with ₹367,030 in observed direct handling cost over 18 months.**

- **Target value:**

  **Approximately 1,130 cases**, representing a 20% reduction from the baseline.

- **Projected impact (annualized if applicable):**

  **₹48,937 annualized modeled potential avoided handling cost** based on the 20% Method A scenario.

  This is a modeled capacity/handling-cost impact, not guaranteed cash savings.

## Validation Method

- **How did you validate your AI tool's output?**

  I used deterministic automated tests, data-integrity checks, policy assertions, and a labeled gold-sample evaluation. The production classifier uses deterministic rules and does not make external LLM API calls.

  The gold-label evaluation measured repeat-signal classification, primary-issue classification, customer-intent classification, resolution-type classification, and exact matching across the evaluated fields. I also validated the deterministic support-policy assertions.

- **Sample size:**

  **120 tickets** in the gold-label benchmark.

- **Measured accuracy / error rate:**

  - Repeat Signal Classification: **96.67% (116/120)**
  - Primary Issue Classification: **80.00% (96/120)**
  - Customer Intent Classification: **72.50% (87/120)**
  - Resolution Type Classification: **61.67% (74/120)**
  - Exact Match across all evaluated fields: **36.67% (44/120)**
  - Deterministic Policy Assertions: **8/8 passed (100%)**

- **Primary error types observed:**

  The main limitations were ambiguous or compound support messages, sparse ticket text, and difficulty assigning a single primary classification when a customer described multiple issues. Resolution-type classification was also less accurate than repeat-signal and primary-issue classification.

## Self-Evaluation

1. **Business value & problem selection: 5/5**

   The solution translates the support request into measurable operational and financial metrics while distinguishing observed costs from modeled potential impact.

2. **Data discipline & methodology: 5/5**

   The implementation includes data profiling, deduplication, join validation, timestamp handling, explicit assumptions, deterministic calculations, and documented analytical proxies.

3. **System design & engineering: 5/5**

   The solution is modular, reproducible, tested, and designed around deterministic processing. It includes the weekly digest, tier-aware leaderboard, validation framework, and clean-machine setup instructions.

4. **AI judgment & validation: 5/5**

   I used a deterministic classifier rather than adding an unnecessary external LLM dependency, documented its limitations, and evaluated it against a 120-ticket labeled benchmark with policy assertions.

5. **Communication & handoff: 5/5**

   The repository includes the business memo, README, validation report, demo script, submission documentation, and operational handoff notes.

## Feedback on the Assignment

- **How long did you spend?**

  Approximately **5 hours**, with additional time spent on final validation, reproducibility, and submission cleanup.

- **What was ambiguous?**

  The brief intentionally left some definitions open, particularly how to identify repeat contacts and how to interpret the requested business impact. I treated these as analytical decisions, documented the assumptions, and avoided presenting proxies as confirmed facts.

- **What did you enjoy?**

  I enjoyed connecting messy support-ticket data with business outcomes and turning the analysis into a simple operational tool rather than building an unnecessarily large platform.
