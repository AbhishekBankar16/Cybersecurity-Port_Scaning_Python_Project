import socket
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_port(target, port, timeout=1):
    """Scan a single port and return result"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((target, port))
            if result == 0:
                try:
                    # Try to grab banner
                    s.send(b'HEAD / HTTP/1.0\r\n\r\n')
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                    return (port, True, banner[:50] if banner else "No banner")
                except:
                    return (port, True, "No banner")
            else:
                return (port, False, None)
    except Exception as e:
        return (port, False, str(e))

def main():
    print("=== Enhanced Port Scanner ===")
    print("=" * 40)
    
    # Target IP or Hostname
    target = input("Enter target IP or hostname (default: localhost): ").strip()
    if not target:
        target = "localhost"
    
    # Range of ports to scan
    try:
        start_port = int(input("Enter start port (default: 1): ") or "1")
        end_port = int(input("Enter end port (default: 1000): ") or "1000")
    except ValueError:
        print("Invalid port numbers. Using defaults.")
        start_port = 1
        end_port = 1000
    
    # Validate port range
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("Invalid port range. Using 1-1000.")
        start_port = 1
        end_port = 1000
    
    print(f"\nScanning {target} from port {start_port} to {end_port}...")
    print("This may take a moment...\n")
    
    # Common ports to check first
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 8080]
    common_in_range = [p for p in common_ports if start_port <= p <= end_port]
    
    open_ports = []
    
    # Scan with threading for better performance
    with ThreadPoolExecutor(max_workers=100) as executor:
        # Submit all port scanning tasks
        future_to_port = {
            executor.submit(scan_port, target, port): port 
            for port in range(start_port, end_port + 1)
        }
        
        # Process results as they complete
        for future in as_completed(future_to_port):
            port, is_open, banner = future.result()
            if is_open:
                open_ports.append((port, banner))
                print(f"[+] Port {port} is OPEN - {banner}")
    
    # Display results
    print("\n" + "=" * 40)
    print("SCAN RESULTS:")
    print("=" * 40)
    
    if open_ports:
        print(f"\nFound {len(open_ports)} open port(s):")
        for port, banner in sorted(open_ports):
            print(f"  Port {port}: {banner}")
    else:
        print("\nNo open ports found in the specified range.")
        print("\nCommon services to check:")
        print("- Web servers typically run on ports 80, 443, 8080")
        print("- SSH typically runs on port 22")
        print("- MySQL typically runs on port 3306")
        print("- PostgreSQL typically runs on port 5432")
    
    print("\nScan complete!")

if __name__ == "__main__":
    main()
