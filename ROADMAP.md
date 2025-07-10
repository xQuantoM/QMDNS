# DNS Speed Test Tool: The Path to Perfect

This document outlines the roadmap for evolving the DNS Speed Test tool into a professional-grade, feature-complete utility.

---

### Category 1: Unquestionable Accuracy & Reliability

*The foundation of a perfect testing tool is data you can trust completely.*

- [x] **Add 90th/95th Percentile Timings:** Calculate and display percentile-based timings (p90, p95) to provide a better measure of consistent performance.
- [x] **Implement Optional Warm-up Queries:** Add a flag (`--warmup-queries`) to send untimed requests before measurement to get more stable and realistic timing results.
- [x] **Add DNSSEC Validation Check:** Test if servers support DNSSEC, adding a critical security dimension to the results.
- [x] **Reliability-First Ranking**: Servers are now ranked based on their success rate first, then by speed.
- [x] **Use `time.perf_counter()` for Timing**: Use a monotonic clock for accurate measurements.
- [x] **Add TCP Fallback for DNSSEC**: Make DNSSEC checks more reliable.
- [x] **Stricter Input Validation:** Pre-validate all server IPs and domain names to prevent errors during a long test run.
- [ ] **Add Geo-Location Data:** Include an option to look up the physical location of servers to provide context for latency results.
- [ ] **Advanced Health Checks:** Implement checks for issues like DNS hijacking or poisoning to ensure servers are returning correct results.

---

### Category 2: Professional User Experience (UX)

*A perfect tool is not just powerful, but also intuitive and easy to use.*

- [x] **Interactive Mode by Default**: Run the script without any arguments to launch a simple, interactive wizard.
- [x] **Quick Test Mode**: Use the `--quick` flag to test only the major, trusted DNS providers.
- [x] **Simple & Detailed Output**: Choose between a simple, one-line recommendation (`--simple`) or a detailed comparison table.
- [x] **Interactive Progress Bar:** Replace per-server print statements with a clean, real-time progress bar.
- [x] **Terminal-Aware Progress Bar**: Make the progress bar robust to terminal resizing.
- [x] **Handle `KeyboardInterrupt` (Ctrl+C)**: Ensure the script exits gracefully.
- [x] **Fix Table Alignment**: Correctly align columns, even with ANSI color codes.
- [x] **More Granular Error Reporting:** Expand the output table to show counts for each specific error type (NoAnswer, Refused, etc.), not just Timeouts.
- [ ] **Graphical Chart Output:** Add an option to generate a bar chart of the results, either saved to a file (`matplotlib`) or rendered in the terminal (`plotext`).
- [ ] **Configuration File Support:** Allow users to specify all options in a config file (e.g., `config.yaml`) for easy, repeatable test runs.

---

### Category 3: Comprehensive Features

*A perfect tool anticipates the user's needs with advanced functionality.*

- [ ] **Historical Performance Tracking:** Save results to a local file (`history.json`) and add a `--compare` flag to track performance changes over time.
- [ ] **Dynamic Server Lists:** Implement a feature to fetch a fresh, curated list of public DNS servers from a trusted online source.

---

### Category 4: Code Quality & Distribution

*A perfect tool is robust, maintainable, and easily accessible to everyone.*

- [x] **Use `ipaddress` Module for Validation**: Use the standard library for robust IPv4 validation.
- [x] **Use `parser.error()` for Argument Validation**: Improve command-line argument handling.
- [ ] **Full Unit Test Coverage:** Create a comprehensive test suite to guarantee that future changes do not break existing functionality.
- [ ] **Package for PyPI (`pip`):** Package the script so it can be easily installed worldwide with `pip install dns-speed-test`.
- [ ] **Automated Linting & Formatting:** Set up tools to enforce a consistent, high-quality code style across the project.
- [ ] **Refactor for Library Usage:** Structure the code so the core testing functions can be imported and used by other Python applications.

---

### Category 5: Documentation & Community

*A perfect tool is well-documented and welcoming to contributors.*

- [x] **Create a `README.md`:** Write a clear, comprehensive README with installation instructions, usage examples, and a feature list.
- [x] **Create a `ROADMAP.md`:** This file!
- [ ] **Add Inline Code Comments:** Add comments to explain complex logic and make the codebase easier to understand.
- [ ] **Set Up a Contribution Guide:** Create a `CONTRIBUTING.md` with clear guidelines for bug reports, feature requests, and pull requests.

---

By focusing on these five categories, we can transform this script from a functional tool into a polished, professional utility that users can rely on.
