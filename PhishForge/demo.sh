#!/bin/bash

# PhishForge Detector - Demo Mode
# Shows pre-generated analysis examples without running the detector

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║         🛡️  PHISHFORGE DETECTOR - DEMO MODE                       ║"
echo "║  Educational phishing detection tool - Example analyses           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This demo shows two pre-analyzed emails to demonstrate how PhishForge works."
echo "To analyze your own emails, use: ./analyze.sh <your_email_file.txt>"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

cat DEMO_OUTPUT.txt

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   Ready to analyze your emails?                   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Usage examples:"
echo ""
echo "  1. Quick analysis:"
echo "     ./analyze.sh --body-file your_email.txt"
echo ""
echo "  2. Full analysis with details:"
echo "     ./analyze.sh --subject \"Email subject\" \\"
echo "                  --sender \"Name <email@domain.com>\" \\"
echo "                  --body-file your_email.txt"
echo ""
echo "  3. Run test suite:"
echo "     ./test.sh"
echo ""
echo "For more information, see USAGE.md"
echo ""
