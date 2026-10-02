# Vireo Audio Support Intelligence — 3-Minute Video Walkthrough Script

**Track:** Forward Deployed Engineer  
**Dataset:** Set A (Vireo Audio Support Tickets)  
**Total Target Duration:** 2 minutes 45 seconds – 2 minutes 55 seconds (Hard limit: < 3:00)  

---

## Video Breakdown & Timing Cue Sheet

```
+----------------+-------------------------------------------------------------+
| Timestamp      | Visual / Screen Action         | Talking Points             |
+----------------+-------------------------------------------------------------+
| 0:00 - 0:30    | Terminal / README.md           | Context, Client & Problem  |
| 0:30 - 1:15    | Terminal: Digest script run    | Weekly Digest Demo         |
| 1:15 - 1:55    | Terminal: Leaderboard script   | Fair Tiered Leaderboard    |
| 1:55 - 2:35    | outputs/07_business_memo.md    | Business Goal & Finances   |
| 2:35 - 3:00    | Terminal: pytest / evaluate.py | Validation & Wrap-up       |
+----------------+-------------------------------------------------------------+
```

---

## Detailed Script & Spoken Words

### Section 1: Introduction & Operational Context (0:00 – 0:30)
**Visual:** Show the repository on screen (`README.md` or terminal).
> "Hi everyone, I’m presenting the Support Intelligence Suite built for Vireo Audio. 
> 
> When founder and CEO Priya Raman asked for a weekly customer complaint digest and an agent leaderboard, Support Ops Lead Neha immediately flagged a vital operational policy: *'Please don't rank the warranty team on ticket counts — their cases take days.'*
> 
> My goal was to deliver an automated, production-grade tool that gives Priya complete visibility into operational issues and costs, while strictly respecting team boundaries and operating at zero external API cost."

---

### Section 2: Weekly Customer Complaint Digest (0:30 – 1:15)
**Visual:** Run `python scripts/04_generate_digest.py` in the terminal and open `outputs/weekly_digest.md`.
> "Let’s run the Weekly Digest generator for our reference week, 2026-W26.
> 
> In seconds, the deterministic engine processes all 199 tickets from that week, generating both human-readable Markdown and structured JSON telemetry.
> 
> Looking at the digest:
> 1. It surfaces the **Top 5 Complaint Themes**—led by audio connectivity, battery charging, and delivery tracking.
> 2. It calculates **Week-over-Week changes**: ticket volume rose by 19.16%, with repeat contacts increasing to 33.67%.
> 3. It isolates **Hardware Concentrations**: our Pulse 2 wireless earbuds account for 40.2% of all complaints this week.
> 4. Finally, it provides an **Operational Cost Accounting**, capturing ₹198,632 in direct variable costs, including SLA breach penalties and refunds."

---

### Section 3: Policy-Governed Agent Leaderboard (1:15 – 1:55)
**Visual:** Run `python scripts/05_agent_leaderboard.py` and open `outputs/agent_leaderboard.md`.
> "Next is the Weekly Agent Leaderboard. Rather than a naive global ranking that harms morale, this tool enforces Vireo Support Policy Sections 1 and 6.
> 
> - **Tier 1 Frontline Agents** are ranked by weekly closed volume, with productivity benchmarks across chat, email, voice, and social.
> - **Tier 2 Warranty and Escalations Agents** are placed on a dedicated, non-ranked monitoring roster. They are evaluated on resolution quality, active investigation load, and SLA adherence—never rushed ticket counts.
> - Operational teams like Logistics and Billing are tracked separately. This gives leadership fair, actionable visibility without perverse incentives."

---

### Section 4: Business Goal & Financial Impact (1:55 – 2:35)
**Visual:** Open `outputs/07_business_memo.md`.
> "In my one-page business memo to Priya, the findings translate directly into a concrete business goal stated as a number and money.
> 
> Across 11,875 historical tickets, we identified that **Repeat Contacts** (1,412 tickets / 11.89% by Policy Method A) consume ₹367,030 in direct handling costs and drive over ₹840,000 in broader operational friction.
> 
> Furthermore, hardware defects in just two models—**Pulse 2** and **Nexa 2**—account for ₹3.87 million, or over 60% of all refund and replacement drain.
> 
> We model three neutral goal scenarios: for example, a 20% reduction in repeat contacts delivers ₹73,406 in direct support handling savings and ₹847,050 in total operational cost impact."

---

### Section 5: Validation, Engineering & Wrap-Up (2:35 – 3:00)
**Visual:** Run `python -m pytest tests/ -q` showing 47 passed, then conclude.
> "For validation, the production engine is 100% deterministic—zero external LLM calls, zero hallucination risk, and zero API costs. 
> 
> Audited against an independent 120-ticket human gold standard, the system achieved 96.7% accuracy on repeat signals and 80% on primary issues, with 8 of 8 policy assertions passing.
> 
> As you can see, the complete test suite of 47 automated tests passes cleanly. The repository is completely reproducible on a clean machine with a single pip install.
> 
> Thank you for your time!"
