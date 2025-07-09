# QMDNS

QMDNS is a Python command-line utility for measuring the performance and characteristics of DNS servers. This tool helps you identify the fastest and most reliable DNS resolvers for your network by testing response times, success rates, and DNSSEC support.

## ✨ Key Features

*   **Comprehensive Performance Metrics**: Measures average, median, 90th percentile (p90), and 95th percentile (p95) response times in milliseconds.
*   **Success Rate Analysis**: Calculates the percentage of successful queries and categorizes different types of errors (Timeout, NoAnswer, NoNameservers, Other).
*   **DNSSEC Validation Check**: Optionally verifies if DNS servers support DNSSEC (Domain Name System Security Extensions) validation.
*   **Flexible Input**: Test against a default list of popular DNS servers and domains, or provide your own custom lists via text files.
*   **Configurable Tests**: Adjust the number of queries per domain, warm-up queries, concurrent workers, and query timeouts.
*   **Multiple Output Formats**: Display results in a human-readable table directly in the terminal, or export them to CSV or JSON files for further analysis.
*   **Colorized Output**: Enhances readability of terminal output with color-coded performance indicators.

## 📦 Installation

To get started with the DNS Speed Test Tool, follow these steps:

1.  **Clone the Repository (or download the script):**
    If you have Git, you can clone the repository:
    ```bash
    git clone https://github.com/xQuantoM/QMDNS.git
    cd your-repo-name/dns_tests
    ```
    Alternatively, you can just download `dns_speed_test.py` and `ROADMAP.md` into a directory.

2.  **Create and Activate a Python Virtual Environment (Recommended):**
    It's highly recommended to use a virtual environment to manage dependencies and avoid conflicts with your system's Python packages.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows, use `.\.venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    With your virtual environment activated, install the required Python libraries:
    ```bash
    pip install dnspython
    ```

## 🛠�� Usage

Run the script from your terminal. Ensure your virtual environment is activated if you created one.

```bash
python dns_speed_test.py [OPTIONS]
```

### Basic Usage

Run a test with default DNS servers and domains:
```bash
python dns_speed_test.py
```

Enable DNSSEC validation checks:
```bash
python dns_speed_test.py --dnssec
```

### Customizing Servers and Domains

You can provide your own lists of DNS servers and domains in plain text files (one entry per line).

`my_servers.txt`:
```
8.8.4.4
9.9.9.10
1.0.0.1
```

`my_domains.txt`:
```
example.com
google.org
wikipedia.net
```

Run the test with custom lists:
```bash
python dns_speed_test.py --servers my_servers.txt --domains my_domains.txt
```

### Adjusting Test Parameters

*   `-q`, `--queries`: Number of queries per domain (default: 3).
*   `--warmup-queries`: Number of untimed warm-up queries before testing (default: 1).
*   `-w`, `--workers`: Number of concurrent workers (threads) for testing (default: 10).
*   `-t`, `--timeout`: DNS query timeout in seconds (default: 2.0).
*   `-l`, `--lifetime`: Total time for a query attempt in seconds (default: 2.0).

Example: 5 queries per domain, 2 warm-up queries, 20 workers, 1-second timeout:
```bash
python dns_speed_test.py -q 5 --warmup-queries 2 -w 20 -t 1.0
```

### Output Formats

*   `--output-format`: Choose `table` (default), `json`, or `csv`.
*   `--output-file`: Specify a file path to save JSON or CSV results.

Save results to a CSV file:
```bash
python dns_speed_test.py --output-format csv --output-file results.csv
```

Save results to a JSON file:
```bash
python dns_speed_test.py --output-format json --output-file results.json
```

### Disabling Colors

If your terminal doesn't support ANSI colors or you prefer plain text output:
```bash
python dns_speed_test.py --no-color
```

## 📊 Sample Output

```
--- DNS Speed Test Results ---
Rank  DNS Server         Success    Avg (ms)           Median (ms)        p90 (ms)           p95 (ms)           Std Dev     DNSSEC     Timeouts  
----------------------------------------------------------------------------------------------------------------------------------------------------
1     1.1.1.1            100%       15.23              15.00              16.50              17.00              0.87        Yes        0         
2     8.8.8.8            100%       22.50              22.00              24.00              25.00              1.12        Yes        0         
3     9.9.9.9            98%        35.10              34.50              38.00              39.00              2.50        Yes        1         
4     208.67.222.222     95%        55.75              54.00              60.00              62.00              4.10        No         2         

--- Recommendation ---
Fastest server: 1.1.1.1 (Avg: 15.23 ms, p90: 16.50 ms) (Supports DNSSEC)
```

## 🗺️ Roadmap

The future development plans for this tool are outlined in the [ROADMAP.md](ROADMAP.md) file.

## 🤝 Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute code, please open an issue or a pull request on the GitHub repository.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
