#!/usr/bin/env python3
"""
Quick test for enterprise heuristics functions
"""

import sys
sys.path.insert(0, '/workspaces/PhishForge-Lite/PhishForge')

from phishforge_detector import has_char_substitution, has_double_extension

print("="*60)
print("  PhishForge Enterprise Heuristics - Unit Tests")
print("="*60)

print("\n1. Testing has_char_substitution():")
print("-" * 60)

test_domains = [
    ("paypa1.com", True, "PayPal with 1 instead of l"),
    ("micr0soft.com", True, "Microsoft with 0 instead of o"),
    ("g00gle.com", True, "Google with 00 instead of oo"),
    ("amaz0n.com", True, "Amazon with 0 instead of o"),
    ("paypal.com", False, "Legitimate PayPal"),
    ("microsoft.com", False, "Legitimate Microsoft"),
    ("company2023.com", False, "Year number (legitimate)"),
    ("ver1fy-acc0unt.xyz", True, "Multiple substitutions"),
]

passed = 0
failed = 0

for domain, expected, description in test_domains:
    result = has_char_substitution(domain)
    status = "✅" if result == expected else "❌"
    if result == expected:
        passed += 1
    else:
        failed += 1
    print(f"{status} {domain:25} -> {result:5} (expected: {expected:5}) - {description}")

print(f"\nChar Substitution Tests: {passed} passed, {failed} failed")

print("\n2. Testing has_double_extension():")
print("-" * 60)

test_files = [
    ("invoice.pdf.exe", True, "PDF disguised as executable"),
    ("document.docx.exe", True, "Word doc disguised"),
    ("report.xlsx.html", True, "Excel as HTML phishing"),
    ("contract.pptx.html", True, "PowerPoint as HTML"),
    ("receipt.pdf.html", True, "PDF as HTML"),
    ("image.jpg.exe", True, "Image disguised"),
    ("normal.pdf", False, "Legitimate PDF"),
    ("document.docx", False, "Legitimate Word doc"),
    ("report.xlsx", False, "Legitimate Excel"),
    ("archive.zip", False, "Legitimate ZIP"),
    ("invoice123.pdf.exe", True, "Numbered filename with double ext"),
]

passed2 = 0
failed2 = 0

for filename, expected, description in test_files:
    result = has_double_extension(filename)
    status = "✅" if result == expected else "❌"
    if result == expected:
        passed2 += 1
    else:
        failed2 += 1
    print(f"{status} {filename:30} -> {result:5} (expected: {expected:5}) - {description}")

print(f"\nDouble Extension Tests: {passed2} passed, {failed2} failed")

print("\n" + "="*60)
total_passed = passed + passed2
total_tests = len(test_domains) + len(test_files)
print(f"OVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.0f}%)")
print("="*60 + "\n")

if total_passed == total_tests:
    print("🎉 All heuristics working correctly!")
    sys.exit(0)
else:
    print(f"⚠️  {total_tests - total_passed} test(s) failed")
    sys.exit(1)
