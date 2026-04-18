#!/usr/bin/env python3
"""
NetOps PII/PHI & Secret Scanner

An open-source scanner designed for Network Automation, Infrastructure-as-Code (IaC),
and Agentic workflows. It scans source files for hardcoded sensitive data including:
- IP addresses (IPv4/IPv6) and MAC addresses
- Emails and URLs with embedded credentials
- Generic API keys, secrets, and Bearer tokens
- Network-specific secrets (SNMP communities, Cisco Type 7, Juniper Type 9)

Usage:
    python netops_pii_scanner.py <file_or_directory>
    python netops_pii_scanner.py my_agent_workflows/
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

# =========================================================================
# DATA CLASSES
# =========================================================================

@dataclass
class Violation:
    line_number: int
    line_content: str
    pattern_name: str
    severity: str  # "critical", "warning", "info"
    matched_value: str
    context: str = ""

    def __str__(self) -> str:
        return f"  L{self.line_number} [{self.severity.upper()}] {self.pattern_name}: {self.matched_value!r}"

@dataclass
class ScanResult:
    file_path: str
    violations: List[Violation] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "warning")

    @property
    def is_clean(self) -> bool:
        return self.critical_count == 0

    def __str__(self) -> str:
        status = "PASS" if self.is_clean else "FAIL"
        return f"{self.file_path}: {status} (critical={self.critical_count}, warning={self.warning_count})"

# =========================================================================
# ALLOWLIST CONSTANTS
# =========================================================================

# RFC 5737 documentation IPs and standard private spaces used in examples
_RFC5737_PREFIXES = ("192.0.2.", "198.51.100.", "203.0.113.")

# Loopback, broadcast, and special addresses — always safe
_SAFE_IPS = frozenset({"0.0.0.0", "127.0.0.1", "255.255.255.255", "255.255.255.0", "0.0.0.0/0"})

# Common network protocol ports (avoids flagging ports as IPs/serials)
_COMMON_PORTS = frozenset({"22", "80", "443", "161", "162", "514", "6514", "8080", "179", "500", "4500"})

# =========================================================================
# PII & SECRET PATTERNS
# =========================================================================

@dataclass
class PIIPattern:
    name: str
    regex: re.Pattern
    severity: str
    description: str = ""

    def __post_init__(self):
        if isinstance(self.regex, str):
            self.regex = re.compile(self.regex)

PII_PATTERNS: List[PIIPattern] = [
    # ---- Standard PII ----
    PIIPattern(
        name="ipv4_address",
        regex=re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"),
        severity="warning",
    ),
    PIIPattern(
        name="ipv6_address",
        regex=re.compile(
            r"(?<![\w:])(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}(?![\w:])"
            r"|(?<![\w:])(?:[0-9a-fA-F]{1,4}:){1,7}:(?![\w:])"
            r"|(?<![\w:])(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}(?![\w:])"
        ),
        severity="warning",
    ),
    PIIPattern(
        name="mac_address",
        regex=re.compile(r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b"),
        severity="warning",
    ),
    PIIPattern(
        name="email_address",
        regex=re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"),
        severity="critical",
    ),
    
    # ---- Universal Application Secrets ----
    PIIPattern(
        name="bearer_token",
        regex=re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]{20,}=*"),
        severity="critical",
    ),
    PIIPattern(
        name="api_key_assignment",
        regex=re.compile(r"""(?i)(?:api[_-]?key|api[_-]?secret|password|token|secret)\s*=\s*['"][A-Za-z0-9\-._~+/]{8,}['"]"""),
        severity="critical",
    ),
    PIIPattern(
        name="url_with_credentials",
        regex=re.compile(r"https?://[^:]+:[^@]+@[^\s'\"]+"),
        severity="critical",
    ),

    # ---- NetOps Specific Secrets ----
    PIIPattern(
        name="cisco_type7_password",
        regex=re.compile(r"(?i)(?:password|secret)\s+7\s+[0-9A-Fa-f]{10,}"),
        severity="critical",
    ),
    PIIPattern(
        name="juniper_type9_hash",
        regex=re.compile(r"\$9\$[a-zA-Z0-9./]{10,}"),
        severity="critical",
    ),
    PIIPattern(
        name="snmp_community_string",
        regex=re.compile(r"(?i)snmp-server\s+community\s+([a-zA-Z0-9@_.\-]+)"),
        severity="critical",
    ),
]

# =========================================================================
# CONTEXT DETECTION & ALLOWLISTING
# =========================================================================

def _is_in_comment(line: str, match_start: int) -> bool:
    in_single, in_double = False, False
    for i, ch in enumerate(line):
        if i >= match_start: return False
        if ch == "'" and not in_double: in_single = not in_single
        elif ch == '"' and not in_single: in_double = not in_double
        elif ch == "#" and not in_single and not in_double: return True
    return False

def _is_in_regex_string(line: str) -> bool:
    return bool(re.search(r'''r['"]''', line) or re.search(r'''r"""''', line))

def _is_in_docstring_block(lines: List[str], line_idx: int) -> bool:
    triple_count = sum(l.count('"""') + l.count("'''") for l in lines[:line_idx])
    return triple_count % 2 == 1

def _is_safe_ip(ip_str: str) -> bool:
    if ip_str in _SAFE_IPS: return True
    if any(ip_str.startswith(prefix) for prefix in _RFC5737_PREFIXES): return True
    # Ignore Semantic Versions (e.g., 1.23.4) masquerading as IPs
    if re.fullmatch(r"\b\d{1,2}\.\d{1,2}\.\d{1,2}(?:-.*)?\b", ip_str): return True
    return False

def _is_safe_email(email: str) -> bool:
    safe_domains = {"example.com", "example.org", "test.com", "domain.com", "placeholder.com"}
    domain = email.split("@")[1].lower() if "@" in email else ""
    return domain in safe_domains or "{" in email

def _is_safe_mac(mac: str) -> bool:
    return mac.replace(":", "").replace("-", "") == "000000000000"

# =========================================================================
# SCANNER LOGIC
# =========================================================================

def scan_file(file_path: str) -> ScanResult:
    result = ScanResult(file_path=file_path)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError) as e:
        result.violations.append(Violation(0, "", "file_error", "warning", str(e)))
        return result

    lines = content.splitlines()

    for pattern in PII_PATTERNS:
        for line_idx, line in enumerate(lines):
            for match in pattern.regex.finditer(line):
                matched_value = match.group(0)
                match_start = match.start()

                # --- Context Allowlisting ---
                if _is_in_comment(line, match_start) and pattern.severity == "critical": continue
                if _is_in_regex_string(line) and pattern.name in ("ipv4_address", "ipv6_address", "mac_address"): continue
                
                if _is_in_docstring_block(lines, line_idx) or line.strip().startswith(('"""', "'''")):
                    if pattern.name in ("ipv4_address", "ipv6_address", "mac_address", "email_address"): continue

                # --- Pattern Specific Allowlisting ---
                if pattern.name == "ipv4_address" and (_is_safe_ip(matched_value) or matched_value in _COMMON_PORTS): continue
                if pattern.name == "mac_address" and _is_safe_mac(matched_value): continue
                if pattern.name == "email_address" and _is_safe_email(matched_value): continue
                if pattern.name == "api_key_assignment":
                    # Skip env vars and obvious placeholders
                    if "os.getenv" in line or "os.environ" in line: continue
                    val_match = re.search(r"""['"]([^'"]+)['"]""", line[match_start:])
                    if val_match and val_match.group(1) in ("", "your-key-here", "CHANGE_ME", "xxx", "test"): continue

                context = "in comment" if _is_in_comment(line, match_start) else "in docstring" if _is_in_docstring_block(lines, line_idx) else ""
                
                result.violations.append(
                    Violation(
                        line_number=line_idx + 1,
                        line_content=line.rstrip()[:200],
                        pattern_name=pattern.name,
                        severity=pattern.severity,
                        matched_value=matched_value[:100],
                        context=context,
                    )
                )
    return result

def scan_directory(dir_path: str, file_pattern: str = "*.py") -> List[ScanResult]:
    path = Path(dir_path)
    return [scan_file(str(py_file)) for py_file in sorted(path.rglob(file_pattern)) if py_file.is_file()] if path.exists() else []

def print_report(results: List[ScanResult], verbose: bool = False) -> int:
    total_critical = sum(r.critical_count for r in results)
    total_warning = sum(r.warning_count for r in results)

    print("=" * 70)
    print("NETOPS PII/PHI & SECRET SCAN REPORT")
    print("=" * 70)

    for result in results:
        if result.violations:
            print(f"\n{result}")
            for v in result.violations:
                if verbose or v.severity in ("critical", "warning"):
                    ctx = f" ({v.context})" if v.context else ""
                    print(f"{v}{ctx}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(results)} files scanned")
    print(f"  Critical: {total_critical}\n  Warning:  {total_warning}")
    print("\nRESULT: FAIL — critical violations found" if total_critical > 0 else "\nRESULT: PASS — no critical violations")
    print("=" * 70)

    return total_critical

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan NetOps workflow files for PII/PHI and Secrets")
    parser.add_argument("path", help="File or directory to scan")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show all violations")
    parser.add_argument("--pattern", default="*.py", help="File glob pattern (default: *.py)")
    
    args = parser.parse_args()
    target = Path(args.path)

    if target.is_file(): results = [scan_file(str(target))]
    elif target.is_dir(): results = scan_directory(str(target), args.pattern)
    else:
        print(f"Error: {args.path} is not a valid file or directory")
        sys.exit(1)

    sys.exit(1 if print_report(results, verbose=args.verbose) > 0 else 0)
