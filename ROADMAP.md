# DNS Speed Test Tool: The Path to Perfect

This document outlines the roadmap for evolving the DNS Speed Test tool into a professional-grade, feature-complete utility.

---

### Category 1: Unquestionable Accuracy & Reliability

*The foundation of a perfect testing tool is data you can trust completely.*

- [x] **Add 90th/95th Percentile Timings:** Calculate and display percentile-based timings (p90, p95) to provide a better measure of consistent performance.
- [x] **Implement Optional Warm-up Queries:** Add a flag (`--warmup-queries`) to send untimed requests before measurement to get more stable and realistic timing results.
- [x] **Add DNSSEC Validation Check:** Test if servers support DNSSEC, adding a critical security dimension to the results.
- [ ] **Add Geo-Location Data:** Include an option to look up the physical location of servers to provide context for latency results.
- [x] **Stricter Input Validation:** Pre-validate all server IPs and domain names to prevent errors during a long test run.
- [ ] **Advanced Health Checks:** Implement checks for issues like DNS hijacking or poisoning to ensure servers are returning correct results.

---

### Category 2: Professional User Experience (UX)

*A perfect tool is not just powerful, but also intuitive and easy to use.*

- [ ] **Interactive Progress Bar:** Replace per-server print statements with a clean, real-time progress bar (e.g., using `tqdm`).
- [ ] **Graphical Chart Output:** Add an option to generate a bar chart of the results, either saved to a file (`matplotlib`) or rendered in the terminal (`plotext`).
- [ ] **Configuration File Support:** Allow users to specify all options in a config file (e.g., `config.yaml`) for easy, repeatable test runs.
- [ ] **More Granular Error Reporting:** Expand the output table to show counts for each specific error type (NoAnswer, Refused, etc.), not just Timeouts.

---

### Category 3: Comprehensive Features

*A perfect tool anticipates the user's needs with advanced functionality.*

- [ ] **Historical Performance Tracking:** Save results to a local file (`history.json`) and add a `--compare` flag to track performance changes over time.
- [ ] **Dynamic Server Lists:** Implement a feature to fetch a fresh, curated list of public DNS servers from a trusted online source.

---

### Category 4: Code Quality & Distribution

*A perfect tool is robust, maintainable, and easily accessible to everyone.*

- [ ] **Full Unit Test Coverage:** Create a comprehensive test suite to guarantee that future changes do not break existing functionality.
- [ ] **Package for PyPI (`pip`):** Package the script so it can be easily installed worldwide with `pip install dns-speed-test`.
- [ ] **Automated Linting & Formatting:** Set up tools to enforce a consistent, high-quality code style across the project.
- [ ] **Refactor for Library Usage:** Structure the code so the core testing functions can be imported and used by other Python applications.