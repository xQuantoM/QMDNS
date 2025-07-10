# QMDNS

QMDNS is a user-friendly Python command-line utility for measuring the performance and characteristics of DNS servers. This tool helps you identify the fastest and most reliable DNS resolvers for your network by testing response times, success rates, and DNSSEC support.

It's designed to be simple for beginners—just run it without any arguments for a guided setup—while still offering powerful options for advanced users.

## ✨ Key Features

*   **Interactive & Simple by Default**: Run the script without any arguments to launch a simple, interactive wizard. No command-line knowledge needed!
*   **Reliability-First Ranking**: Servers are ranked based on their success rate first, then by speed. You can trust the recommendation to be both fast *and* reliable.
*   **Quick Test Mode**: Use the `--quick` flag to test only the major, trusted DNS providers (Google, Cloudflare, Quad9) for a fast and accurate recommendation.
*   **Simple & Detailed Output**: Choose between a simple, one-line recommendation (`--simple`) or a detailed comparison table.
*   **Comprehensive Performance Metrics**: Measures average, median, 90th percentile (p90), and 95th percentile (p95) response times.
*   **Robust DNSSEC Validation**: Reliably checks for DNSSEC support with a TCP fallback.
*   **Flexible Input**: Test against a default list of popular DNS servers or provide your own custom lists via text files.
*   **Multiple Export Formats**: Export full results to CSV or JSON for further analysis.
*   **Graceful Error Handling**: Handles user interruptions (Ctrl+C) and network errors gracefully.
*   **Terminal-Aware UI**: The progress bar and tables are designed to display correctly on a wide range of terminal sizes.

## 📦 Installation

1.  **Clone the Repository (or download the script):**
    ```bash
    git clone https://github.com/xQuantoM/QMDNS.git
    cd QMDNS
    ```

2.  **Create and Activate a Python Virtual Environment (Recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows, use `.\.venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install dnspython
    ```

## 🛠️ Usage

### The Easy Way (Interactive Mode)

For most users, just run the script without any arguments:

```bash
python3 dns_speed_test.py
```

This will launch a simple wizard that asks you two questions:
1.  Do you want a **(q)uick** test or a **(c)omprehensive** one?
2.  Do you want a **(s)imple** recommendation or a **(d)etailed** table?

### Command-Line Options (For Advanced Users)

For more control, you can use command-line flags.

#### Quick & Simple Tests

*   **Quick Test**: Get a fast recommendation by testing only major providers.
    ```bash
    python3 dns_speed_test.py --quick
    ```
*   **Simple Output**: Show only the final recommendation without the detailed table.
    ```bash
    python3 dns_speed_test.py --simple
    ```
*   **Combine them**: Get a quick and simple recommendation.
    ```bash
    python3 dns_speed_test.py --quick --simple
    ```

#### Customizing Servers and Domains

Provide your own lists of DNS servers and domains in plain text files (one entry per line).

`my_servers.txt`:
```
8.8.4.4
9.9.9.10
1.0.0.1
```

Run the test with your custom list:
```bash
python3 dns_speed_test.py --servers my_servers.txt
```

#### Output Formats

*   `--output-format`: Choose `table` (default), `json`, or `csv`.
*   `--output-file`: Specify a file path to save JSON or CSV results.

Save full results to a CSV file:
```bash
python3 dns_speed_test.py --output-format csv --output-file results.csv
```

## 📊 Sample Output

**Default Table View:**

```
--- DNS Speed Test Results (Reliable Servers) ---
Rank  DNS Server         Success    Avg (ms)           Median (ms)        p90 (ms)           p95 (ms)           Std Dev      Timeouts
----------------------------------------------------------------------------------------------------------------------------------------
1     8.8.8.8            99%        2.94               0.81               1.20               1.32               20.86        1
2     9.9.9.9            98%        17.87              1.08               1.98               225.37             60.87        2
3     1.1.1.1            100%       24.61              1.02               1.95               234.48             91.83        0

--- DNS Recommendation ---
Recommended DNS Server: 8.8.8.8
 -> Speed: 2.94 ms average
 -> Reliability: 99% success rate
```

**Simple View (`--simple` flag):**

```
--- DNS Recommendation ---
Recommended DNS Server: 8.8.8.8
 -> Speed: 2.94 ms average
 -> Reliability: 99% success rate
```

## 🗺️ Roadmap

The future development plans for this tool are outlined in the [ROADMAP.md](ROADMAP.md) file.

## 🤝 Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute code, please open an issue or a pull request.

## 📄 License

This project is licensed under the MIT License.
