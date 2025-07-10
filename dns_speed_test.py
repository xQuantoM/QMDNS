# This tool is designed for IPv4 (A record) testing only.

import dns.resolver
import time
import statistics
import argparse
import json
import csv
import sys
import shutil
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- ANSI Color Codes for Terminal Output ---
class Colors:
    """A class to hold ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    DISABLED = ''

def setup_colors(disable=False):
    """Disables colors if the --no-color flag is set or if output is not a TTY."""
    if disable or not sys.stdout.isatty():
        for attr in dir(Colors):
            if attr.isupper():
                setattr(Colors, attr, Colors.DISABLED)

# --- Default Configuration ---
DEFAULT_DNS_SERVERS = [
    "8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9", "8.26.56.26",
    "77.88.8.8", "1.2.4.8", "223.5.5.5", "180.76.76.76", "114.114.114.114"
]
QUICK_DNS_SERVERS = ["8.8.8.8", "1.1.1.1", "9.9.9.9"] # Google, Cloudflare, Quad9
DEFAULT_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "apple.com", "microsoft.com",
    "cloudflare.com", "amazon.com", "github.com", "wikipedia.org", "archlinux.org"
]
RELIABILITY_THRESHOLD = 0.95 # Minimum success rate to be considered reliable

def is_valid_ipv4(ip):
    """Checks if a string is a valid IPv4 address using the ipaddress module."""
    try:
        ipaddress.IPv4Address(ip)
        return True
    except (ipaddress.AddressValueError, TypeError, AttributeError):
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
        return None

def load_domains_from_file(filepath):
    """Loads a list of domains from a text file."""
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File not found at {filepath}{Colors.RESET}", file=sys.stderr)
        return None

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
    """Creates and prints a terminal progress bar that overwrites itself correctly."""
    percent_str = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    line_to_print = f'{prefix} |{bar}| {percent_str}% {suffix}'
    try:
        terminal_width = shutil.get_terminal_size().columns
    except OSError:
        terminal_width = 80 # A safe default
    padded_line = line_to_print.ljust(terminal_width)
    sys.stdout.write(f'\r{padded_line}')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()

def test_dns_server(server, domains, queries, warmup_queries, timeout, lifetime, check_dnssec):
    """Tests a single DNS server, returning detailed statistics."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    resolver.timeout = timeout
    resolver.lifetime = lifetime

    results = {
        "server": server, "times": [], "successes": 0,
        "errors": {"Timeout": 0, "NoAnswer": 0, "NoNameservers": 0, "NXDOMAIN": 0, "Other": 0},
        "dnssec": "N/A"
    }

    if check_dnssec:
        try:
            qname = dns.name.from_text('internic.net')
            q = dns.message.make_query(qname, dns.rdatatype.A, want_dnssec=True)
            response = dns.query.udp(q, server, timeout=timeout)
            results["dnssec"] = bool(response.flags & dns.flags.AD)
        except Exception:
            try: # Fallback to TCP
                response = dns.query.tcp(q, server, timeout=timeout)
                results["dnssec"] = bool(response.flags & dns.flags.AD)
            except Exception:
                results["dnssec"] = False

    if warmup_queries > 0 and domains:
        for _ in range(warmup_queries):
            try:
                resolver.resolve(domains[0], "A")
            except Exception:
                pass

    for domain in domains:
        for _ in range(queries):
            try:
                start_time = time.perf_counter()
                resolver.resolve(domain, "A")
                end_time = time.perf_counter()
                results["times"].append((end_time - start_time) * 1000)
                results["successes"] += 1
            except dns.resolver.Timeout:
                results["errors"]["Timeout"] += 1
            except dns.resolver.NoAnswer:
                results["errors"]["NoAnswer"] += 1
            except dns.resolver.NoNameservers:
                results["errors"]["NoNameservers"] += 1
            except dns.resolver.NXDOMAIN:
                results["errors"]["NXDOMAIN"] += 1
            except Exception:
                results["errors"]["Other"] += 1
    return results

def process_results(results):
    """Calculates statistics from raw test results."""
    stats = {"server": results["server"]}
    total_failures = sum(results["errors"].values())
    total_attempts = results["successes"] + total_failures
    stats['success_rate'] = (results["successes"] / total_attempts) if total_attempts > 0 else 0.0

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
        stats.update({'avg': float('inf'), 'median': float('inf'), 'stdev': float('inf'), 'p90': float('inf'), 'p95': float('inf')})

    stats.update(results["errors"])
    stats['dnssec'] = results.get('dnssec', 'N/A')
    return stats

def colorize_time(t):
    if t < 50: return f"{Colors.GREEN}{t:.2f}{Colors.RESET}"
    if t < 150: return f"{Colors.YELLOW}{t:.2f}{Colors.RESET}"
    return f"{Colors.RED}{t:.2f}{Colors.RESET}"

def colorize_success_rate(rate):
    rate_pct = rate * 100
    if rate >= RELIABILITY_THRESHOLD: return f"{Colors.GREEN}{rate_pct:.0f}%{Colors.RESET}"
    if rate >= 0.9: return f"{Colors.YELLOW}{rate_pct:.0f}%{Colors.RESET}"
    return f"{Colors.RED}{rate_pct:.0f}%{Colors.RESET}"

def display_simple_output(reliable_servers, dnssec):
    """Displays a single, clear recommendation."""
    print(f"\n{Colors.BOLD}--- DNS Recommendation ---{Colors.RESET}")
    if not reliable_servers:
        print(f"{Colors.RED}No reliable DNS servers found.{Colors.RESET}")
        print("This could be due to network issues or a low timeout.")
        print(f"Consider running the test again with a longer timeout, e.g., {Colors.CYAN}--timeout 5.0{Colors.RESET}")
        return

    fastest = reliable_servers[0]
    dnssec_str = ""
    if dnssec:
        if fastest.get('dnssec') is True:
            dnssec_str = f" {Colors.GREEN}(Supports DNSSEC){Colors.RESET}"
        else:
            dnssec_str = f" {Colors.YELLOW}(No DNSSEC Support){Colors.RESET}"

    print(f"Recommended DNS Server: {Colors.GREEN}{Colors.BOLD}{fastest['server']}{Colors.RESET}")
    print(f" -> Speed: {colorize_time(fastest['avg'])} ms average")
    print(f" -> Reliability: {colorize_success_rate(fastest['success_rate'])} success rate{dnssec_str}")

def display_table(stats_list, show_dnssec, unreliable_servers):
    """Displays the results in a formatted table."""
    print(f"\n{Colors.BOLD}--- DNS Speed Test Results (Reliable Servers) ---{Colors.RESET}")
    if not stats_list:
        print(f"{Colors.YELLOW}No servers met the reliability threshold of {RELIABILITY_THRESHOLD:.0%}.{Colors.RESET}")
    else:
        header = (f"{'Rank':<5} {'DNS Server':<18} {'Success':<10} {'Avg (ms)':<18} "
                  f"{'Median (ms)':<18} {'p90 (ms)':<18} {'p95 (ms)':<18} {'Std Dev':<12}")
        if show_dnssec: header += f" {'DNSSEC':<10}"
        header += f" {'Timeouts':<10}"
        print(Colors.BOLD + header + Colors.RESET)
        print("-" * (len(header) + 20))

        ANSI_LEN = len(Colors.GREEN) + len(Colors.RESET)

        for i, stats in enumerate(stats_list, 1):
            if stats['avg'] == float('inf'):
                failed_str = f"{Colors.RED}Failed{Colors.RESET}".ljust(18 + ANSI_LEN)
                na_str = f"{Colors.RED}N/A{Colors.RESET}".ljust(12 + ANSI_LEN)
                line = (f"{i:<5} {stats['server']:<18} "
                        f"{colorize_success_rate(stats['success_rate']):<{10 + ANSI_LEN}} "
                        f"{failed_str} {failed_str} {failed_str} {failed_str} {na_str}")
            else:
                rank_str = f"{i:<5}"
                server_ip = f"{stats['server']:<18}"
                success_str = colorize_success_rate(stats['success_rate'])
                avg_str = colorize_time(stats['avg'])
                median_str = colorize_time(stats['median'])
                p90_str = colorize_time(stats['p90'])
                p95_str = colorize_time(stats['p95'])
                stdev_str = f"{stats['stdev']:.2f}"

                line = (f"{rank_str} "
                        f"{server_ip} "
                        f"{success_str:<{10 + ANSI_LEN}} "
                        f"{avg_str:<{18 + ANSI_LEN}} "
                        f"{median_str:<{18 + ANSI_LEN}} "
                        f"{p90_str:<{18 + ANSI_LEN}} "
                        f"{p95_str:<{18 + ANSI_LEN}} "
                        f"{stdev_str:<12}")

            if show_dnssec:
                dnssec_status = stats.get('dnssec')
                if dnssec_status is True:
                    dnssec_str = f"{Colors.GREEN}Yes{Colors.RESET}"
                elif dnssec_status is False:
                    dnssec_str = f"{Colors.RED}No{Colors.RESET}"
                else:
                    dnssec_str = "N/A"
                line += f" {dnssec_str:<{10 + ANSI_LEN}}"

            timeouts_str = f"{stats['Timeout']}"
            line += f" {timeouts_str:<10}"
            print(line)

    if unreliable_servers:
        print(f"\n{Colors.YELLOW}Note: {len(unreliable_servers)} unreliable server(s) were hidden due to low success rates.{Colors.RESET}")
        print(f"To see all results, run with the {Colors.CYAN}--show-unreliable{Colors.RESET} flag.")

def output_csv(stats_list, filename):
    """Outputs the results to a CSV file."""
    if not stats_list: return
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=stats_list[0].keys())
            writer.writeheader()
            writer.writerows(stats_list)
        print(f"\nResults saved to {filename}")
    except IOError as e:
        print(f"{Colors.RED}Error writing to CSV file {filename}: {e}{Colors.RESET}", file=sys.stderr)

def output_json(stats_list, filename):
    """Outputs the results to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(stats_list, f, indent=4)
        print(f"\nResults saved to {filename}")
    except IOError as e:
        print(f"{Colors.RED}Error writing to JSON file {filename}: {e}{Colors.RESET}", file=sys.stderr)

def interactive_setup():
    """Guides the user through a simple, interactive setup process."""
    print(f"\n{Colors.BOLD}--- Interactive DNS Speed Test Setup ---{Colors.RESET}")
    try:
        test_type = ""
        while test_type not in ['q', 'c']:
            test_type = input(f"{Colors.CYAN}Run a (q)uick test (major providers) or a (c)omprehensive one? [q]:{Colors.RESET} ").strip().lower() or 'q'
        
        use_quick_servers = (test_type == 'q')
        servers = QUICK_DNS_SERVERS if use_quick_servers else DEFAULT_DNS_SERVERS

        output_type = ""
        while output_type not in ['s', 'd']:
            output_type = input(f"{Colors.CYAN}Show a (s)imple recommendation or a (d)etailed table? [s]:{Colors.RESET} ").strip().lower() or 's'
        
        simple_output = (output_type == 's')

        dnssec_choice = input(f"{Colors.CYAN}Check for DNSSEC support? (y/n) [n]:{Colors.RESET} ").strip().lower() or 'n'
        check_dnssec = (dnssec_choice == 'y')

        print(f"\n{Colors.GREEN}Configuration complete. Using smart defaults.{Colors.RESET}")

        return argparse.Namespace(
            servers_list=servers,
            domains_list=DEFAULT_DOMAINS,
            queries=5 if use_quick_servers else 10,
            warmup_queries=1,
            workers=10,
            timeout=3.0,
            lifetime=3.0,
            dnssec=check_dnssec,
            simple=simple_output,
            output_format='table',
            output_file=None,
            no_color=False,
            show_unreliable=False
        )
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="A user-friendly, feature-rich DNS speed test tool (IPv4-only).",
        epilog=f"Run without arguments for a simple interactive setup. By default, only servers with a success rate of {RELIABILITY_THRESHOLD:.0%}" + " or higher are shown.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    group_basic = parser.add_argument_group('Basic Test Controls')
    group_basic.add_argument('--servers', help="Path to a file of DNS servers. Uses a default list if omitted.")
    group_basic.add_argument('--domains', help="Path to a file of domains to test. Uses a default list if omitted.")
    group_basic.add_argument('-q', '--queries', type=int, default=10, help="Number of queries per domain.\nMore queries = more accurate results, but a slower test. (Default: 10)")
    group_basic.add_argument('--dnssec', action='store_true', help="Check if servers support DNSSEC validation (adds a small overhead).")

    group_output = parser.add_argument_group('Output & Formatting')
    group_output.add_argument('--simple', action='store_true', help="Show a simple, one-line recommendation instead of a detailed table.")
    group_output.add_argument('--output-format', choices=['table', 'json', 'csv'], default='table', help="Output format. 'table' is default.")
    group_output.add_argument('--output-file', help="File path to save JSON or CSV results. Required for those formats.")
    group_output.add_argument('--show-unreliable', action='store_true', help="Show all tested servers in the results, even unreliable ones.")
    group_output.add_argument('--no-color', action='store_true', help="Disable colorized output.")

    group_advanced = parser.add_argument_group('Advanced & Performance')
    group_advanced.add_argument('--quick', action='store_true', help="Perform a quick test using only major providers (Google, Cloudflare, Quad9).")
    group_advanced.add_argument('--warmup-queries', type=int, default=1, help="Untimed queries before testing to warm up the cache. (Default: 1)")
    group_advanced.add_argument('-w', '--workers', type=int, default=10, help="Number of concurrent workers for testing. (Default: 10)")
    group_advanced.add_argument('-t', '--timeout', type=float, default=3.0, help="DNS query timeout in seconds. Increase if on a slow network. (Default: 3.0)")
    group_advanced.add_argument('-l', '--lifetime', type=float, default=3.0, help="Total time for a query attempt in seconds. (Default: 3.0)")

    if len(sys.argv) == 1:
        config = interactive_setup()
    else:
        config = parser.parse_args()
        if config.output_format in ('json', 'csv') and not config.output_file:
            parser.error('--output-file is required for JSON or CSV output.')

    setup_colors(config.no_color)

    if hasattr(config, 'servers_list'):
        servers = config.servers_list
        domains = config.domains_list
    else:
        if config.quick:
            servers = QUICK_DNS_SERVERS
            print(f"{Colors.CYAN}Running in --quick mode, testing {len(servers)} major DNS providers.{Colors.RESET}")
        else:
            servers = load_servers_from_file(config.servers) if config.servers else DEFAULT_DNS_SERVERS
        domains = load_domains_from_file(config.domains) if config.domains else DEFAULT_DOMAINS

    if not servers or not domains:
        sys.exit(1)

    total_queries = len(servers) * len(domains) * config.queries
    print(f"\n{Colors.BOLD}Starting DNS speed test...{Colors.RESET}")
    print(f"Testing {len(servers)} servers, {len(domains)} domains, {config.queries} queries each.")
    if config.dnssec: print("DNSSEC validation check enabled.")
    print(f"Total timed queries: {total_queries} using {config.workers} workers.")

    all_stats = []
    try:
        with ThreadPoolExecutor(max_workers=config.workers) as executor:
            future_to_server = { executor.submit(test_dns_server, s, domains, config.queries, config.warmup_queries, config.timeout, config.lifetime, config.dnssec): s for s in servers }
            
            completed = 0
            total_servers = len(servers)
            print_progress_bar(completed, total_servers, prefix='Progress:', suffix='Complete', length=50)

            for future in as_completed(future_to_server):
                server = future_to_server[future]
                try:
                    stats = process_results(future.result())
                    all_stats.append(stats)
                except Exception as exc:
                    print(f"\n{Colors.RED}Server {server} generated an exception: {exc}{Colors.RESET}", file=sys.stderr)
                finally:
                    completed += 1
                    suffix = f"({server:<15.15} done)"
                    print_progress_bar(completed, total_servers, prefix='Progress:', suffix=suffix, length=50)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)

    reliable_stats = sorted([s for s in all_stats if s['success_rate'] >= RELIABILITY_THRESHOLD], key=lambda item: item['avg'])
    unreliable_stats = [s for s in all_stats if s['success_rate'] < RELIABILITY_THRESHOLD]

    if config.simple:
        display_simple_output(reliable_stats, config.dnssec)
    elif config.output_format == 'table':
        stats_to_display = reliable_stats
        if config.show_unreliable:
            stats_to_display = sorted(all_stats, key=lambda item: (item['success_rate'] < RELIABILITY_THRESHOLD, item['avg']))
        display_table(stats_to_display, config.dnssec, unreliable_stats if not config.show_unreliable else [])
        display_simple_output(reliable_stats, config.dnssec)
    elif config.output_format in ['csv', 'json']:
        output_stats = sorted(all_stats, key=lambda item: item['avg'])
        if config.output_format == 'csv':
            output_csv(output_stats, config.output_file)
        elif config.output_format == 'json':
            output_json(output_stats, config.output_file)

if __name__ == "__main__":
    main()
