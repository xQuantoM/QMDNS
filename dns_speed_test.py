# This tool is designed for IPv4 (A record) testing only.

import dns.resolver
import time
import statistics
import argparse
import json
import csv
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


# --- ANSI Color Codes for Terminal Output ---
class Colors:
    """A class to hold ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DISABLED = ''

def setup_colors(disable=False):
    """Disables colors if the --no-color flag is set."""
    if disable:
        for attr in dir(Colors):
            if attr.isupper():
                setattr(Colors, attr, Colors.DISABLED)

# --- Default Configuration ---
DEFAULT_DNS_SERVERS = [
    "8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9", "8.26.56.26",
    "77.88.8.8", "1.2.4.8", "223.5.5.5", "180.76.76.76", "114.114.114.114"
]
DEFAULT_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "apple.com", "microsoft.com",
    "cloudflare.com", "amazon.com", "github.com", "wikipedia.org", "archlinux.org"
]

def is_valid_ipv4(ip):
    """Checks if a string is a valid IPv4 address."""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    except ValueError:
        return False

def load_servers_from_file(filepath):
    """Loads a list of DNS servers from a file, validating each as a valid IPv4 address."""
    servers = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    if is_valid_ipv4(stripped):
                        servers.append(stripped)
                    else:
                        print(f"{Colors.YELLOW}Warning: Skipping invalid IPv4 address '{stripped}' from {filepath}{Colors.RESET}", file=sys.stderr)
        return servers
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File not found at {filepath}{Colors.RESET}", file=sys.stderr)
        sys.exit(1)

def load_domains_from_file(filepath):
    """Loads a list of domains from a text file."""
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File not found at {filepath}{Colors.RESET}", file=sys.stderr)
        sys.exit(1)

def test_dns_server(server, domains, queries, warmup_queries, timeout, lifetime, check_dnssec):
    """
    Tests a single DNS server, returning detailed statistics.
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    resolver.timeout = timeout
    resolver.lifetime = lifetime

    results = {
        "server": server,
        "times": [],
        "successes": 0,
        "errors": {"Timeout": 0, "NoAnswer": 0, "NoNameservers": 0, "Other": 0},
        "dnssec": "N/A"
    }

    # --- DNSSEC Check ---
    if check_dnssec:
        try:
            # Query a known DNSSEC-signed domain
            qname = dns.name.from_text('internic.net')
            q = dns.message.make_query(qname, dns.rdatatype.A, want_dnssec=True)
            response = dns.query.udp(q, server, timeout=timeout)
            if response.flags & dns.flags.AD:
                results["dnssec"] = True
            else:
                results["dnssec"] = False
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: DNSSEC check for {server} failed: {e}{Colors.RESET}", file=sys.stderr)
            results["dnssec"] = False # Assume no support on error

    # --- Warm-up Phase ---
    if warmup_queries > 0 and domains:
        for _ in range(warmup_queries):
            try:
                resolver.resolve(domains[0], "A")
            except Exception:
                pass # Ignore errors, main test will catch them.


    for domain in domains:
        for _ in range(queries):
            try:
                start_time = time.time()
                resolver.resolve(domain, "A")
                end_time = time.time()
                results["times"].append((end_time - start_time) * 1000)
                results["successes"] += 1
            except dns.resolver.Timeout:
                results["errors"]["Timeout"] += 1
            except dns.resolver.NoAnswer:
                results["errors"]["NoAnswer"] += 1
            except dns.resolver.NoNameservers:
                results["errors"]["NoNameservers"] += 1
            except Exception as e:
                results["errors"]["Other"] += 1
                # print(f"{Colors.YELLOW}Debug: Query for {domain} on {server} failed: {e}{Colors.RESET}", file=sys.stderr) # Debugging line
    return results



def process_results(results):
    """Calculates statistics from raw test results."""
    stats = {"server": results["server"]}
    total_failures = sum(results["errors"].values())
    total_attempts = results["successes"] + total_failures

    if total_attempts > 0:
        stats['success_rate'] = results["successes"] / total_attempts
    else:
        stats['success_rate'] = 0.0

    if results["times"]:
        stats['avg'] = statistics.mean(results["times"])
        stats['median'] = statistics.median(results["times"])
        stats['stdev'] = statistics.stdev(results["times"]) if len(results["times"]) > 1 else 0.0
        
        sorted_times = sorted(results["times"])
        p90_index = min(int(len(sorted_times) * 0.90), len(sorted_times) - 1)
        p95_index = min(int(len(sorted_times) * 0.95), len(sorted_times) - 1)
        stats['p90'] = sorted_times[p90_index]
        stats['p95'] = sorted_times[p95_index]
    else:
        stats['avg'] = float('inf')
        stats['median'] = float('inf')
        stats['stdev'] = float('inf')
        stats['p90'] = float('inf')
        stats['p95'] = float('inf')

    stats.update(results["errors"])
    stats['dnssec'] = results.get('dnssec', 'N/A')
    return stats

def colorize_time(t):
    if t < 50:
        return f"{Colors.GREEN}{t:.2f}{Colors.RESET}"
    elif t < 150:
        return f"{Colors.YELLOW}{t:.2f}{Colors.RESET}"
    else:
        return f"{Colors.RED}{t:.2f}{Colors.RESET}"

def colorize_success_rate(rate):
    rate_pct = rate * 100
    if rate == 1.0:
        return f"{Colors.GREEN}{rate_pct:.0f}%{Colors.RESET}"
    elif rate >= 0.9:
        return f"{Colors.YELLOW}{rate_pct:.0f}%{Colors.RESET}"
    else:
        return f"{Colors.RED}{rate_pct:.0f}%{Colors.RESET}"

def display_table(stats_list, show_dnssec):
    """Displays the results in a formatted table."""
    print(f"\n{Colors.BOLD}--- DNS Speed Test Results ---{Colors.RESET}")
    header = (f"{'Rank':<5} {'DNS Server':<18} {'Success':<10} {'Avg (ms)':<18} "
              f"{'Median (ms)':<18} {'p90 (ms)':<18} {'p95 (ms)':<18} {'Std Dev':<12}")
    if show_dnssec:
        header += f" {'DNSSEC':<10}"
    header += f" {'Timeouts':<10}"
    
    print(Colors.BOLD + header + Colors.RESET)
    print("-" * (len(header) + 20))

    for i, stats in enumerate(stats_list, 1):
        rank = f"{i:<5}"
        server_ip = f"{stats['server']:<18}"

        if stats['avg'] == float('inf'):
            success_str = colorize_success_rate(stats['success_rate'])
            avg_str = f"{Colors.RED}Failed{Colors.RESET}"
            median_str = f"{Colors.RED}Failed{Colors.RESET}"
            p90_str = f"{Colors.RED}Failed{Colors.RESET}"
            p95_str = f"{Colors.RED}Failed{Colors.RESET}"
            stdev_str = f"{Colors.RED}N/A{Colors.RESET}"
        else:
            success_str = colorize_success_rate(stats['success_rate'])
            avg_str = colorize_time(stats['avg'])
            median_str = colorize_time(stats['median'])
            p90_str = colorize_time(stats['p90'])
            p95_str = colorize_time(stats['p95'])
            stdev_str = f"{stats['stdev']:.2f}"

        line = (f"{rank} {server_ip} {success_str:<18} {avg_str:<28} "
                f"{median_str:<28} {p90_str:<28} {p95_str:<28} {stdev_str:<12}")

        if show_dnssec:
            dnssec_status = stats.get('dnssec')
            if dnssec_status is True:
                dnssec_str = f"{Colors.GREEN}Yes{Colors.RESET}"
            elif dnssec_status is False:
                dnssec_str = f"{Colors.RED}No{Colors.RESET}"
            else:
                dnssec_str = "N/A"
            line += f" {dnssec_str:<18}"

        timeouts_str = f"{stats['Timeout']}"
        line += f" {timeouts_str:<10}"
        print(line)

    print(f"\n{Colors.BOLD}--- Recommendation ---{Colors.RESET}")
    if stats_list and stats_list[0]['avg'] != float('inf'):
        fastest = stats_list[0]
        recommendation = (f"Fastest server: {Colors.GREEN}{Colors.BOLD}{fastest['server']}{Colors.RESET} "
                          f"(Avg: {Colors.GREEN}{fastest['avg']:.2f} ms, p90: {colorize_time(fastest['p90'])} ms)")
        if show_dnssec and fastest.get('dnssec') is True:
            recommendation += f" {Colors.GREEN}(Supports DNSSEC){Colors.RESET}"
        print(recommendation)
    else:
        print(f"{Colors.RED}All DNS servers failed the test.{Colors.RESET}")

def output_csv(stats_list, filename):
    """Outputs the results to a CSV file."""
    if not stats_list:
        return
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=stats_list[0].keys())
        writer.writeheader()
        writer.writerows(stats_list)
    print(f"\nResults saved to {filename}")

def output_json(stats_list, filename):
    """Outputs the results to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(stats_list, f, indent=4)
    print(f"\nResults saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="DNS Speed Test Tool (IPv4-only)")
    parser.add_argument('--servers', help="Path to a file with DNS servers (one per line).")
    parser.add_argument('--domains', help="Path to a file with domains to test (one per line).")
    parser.add_argument('-q', '--queries', type=int, default=3, help="Number of queries per domain.")
    parser.add_argument('--warmup-queries', type=int, default=1, help="Number of untimed queries to perform before testing.")
    parser.add_argument('-w', '--workers', type=int, default=10, help="Number of concurrent workers for testing.")
    parser.add_argument('-t', '--timeout', type=float, default=2.0, help="DNS query timeout in seconds.")
    parser.add_argument('-l', '--lifetime', type=float, default=2.0, help="Total time for a query attempt in seconds.")
    parser.add_argument('--dnssec', action='store_true', help="Check if servers support DNSSEC validation.")
    parser.add_argument('--output-format', choices=['table', 'json', 'csv'], default='table', help="Output format.")
    parser.add_argument('--output-file', help="File path to save JSON or CSV results.")
    parser.add_argument('--no-color', action='store_true', help="Disable colorized output.")
    args = parser.parse_args()

    setup_colors(args.no_color)

    servers = load_servers_from_file(args.servers) if args.servers else DEFAULT_DNS_SERVERS
    domains = load_domains_from_file(args.domains) if args.domains else DEFAULT_DOMAINS

    if not servers:
        print(f"{Colors.RED}Error: No valid DNS servers to test.{Colors.RESET}", file=sys.stderr)
        sys.exit(1)

    total_queries = len(servers) * len(domains) * args.queries
    print(f"{Colors.BOLD}Starting DNS speed test...{Colors.RESET}")
    print(f"Testing {len(servers)} servers, {len(domains)} domains, {args.queries} queries each.")
    if args.dnssec:
        print("DNSSEC validation check enabled.")
    print(f"Total timed queries to be performed: {total_queries} using {args.workers} workers.\n")

    all_stats = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_server = {
            executor.submit(test_dns_server, s, domains, args.queries, args.warmup_queries, args.timeout, args.lifetime, args.dnssec): s
            for s in servers
        }
        for future in as_completed(future_to_server):
            server = future_to_server[future]
            try:
                raw_result = future.result()
                stats = process_results(raw_result)
                all_stats.append(stats)
                print(f"Finished testing {server}...")
            except Exception as exc:
                print(f"{Colors.RED}Server {server} generated an exception: {exc}{Colors.RESET}", file=sys.stderr)

    sorted_stats = sorted(all_stats, key=lambda item: item['avg'])

    if args.output_format == 'table':
        display_table(sorted_stats, args.dnssec)
    elif args.output_format == 'csv':
        if args.output_file:
            output_csv(sorted_stats, args.output_file)
        else:
            print(f"{Colors.RED}Error: --output-file is required for CSV format.{Colors.RESET}", file=sys.stderr)
    elif args.output_format == 'json':
        if args.output_file:
            output_json(sorted_stats, args.output_file)
        else:
            print(f"{Colors.RED}Error: --output-file is required for JSON format.{Colors.RESET}", file=sys.stderr)

if __name__ == "__main__":
    main()
