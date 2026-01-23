#!/bin/bash

# PhishForge Detector - Operational Mode
# Analyze your own emails for phishing signals

print_usage() {
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║         🛡️  PHISHFORGE DETECTOR - ANALYZE EMAIL                   ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Usage:"
    echo "  $0 --body-file <file> [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  --body-file FILE    Path to text file containing email body"
    echo ""
    echo "Optional:"
    echo "  --subject TEXT      Email subject line (auto: 'Unknown Subject')"
    echo "  --sender TEXT       Sender info with email (auto: 'Unknown Sender')"
    echo "  --json              Output in JSON format"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo ""
    echo "  # Quick analysis (minimal info):"
    echo "  $0 --body-file suspicious_email.txt"
    echo ""
    echo "  # Full analysis:"
    echo "  $0 --subject \"Verify your account\" \\"
    echo "     --sender \"Support <support@example.com>\" \\"
    echo "     --body-file email.txt"
    echo ""
    echo "  # JSON output for scripts:"
    echo "  $0 --body-file email.txt --json > result.json"
    echo ""
    echo "Demo mode: Run './demo.sh' to see example analyses"
    echo ""
}

# Default values
SUBJECT="Unknown Subject"
SENDER="Unknown Sender <unknown@unknown.com>"
BODY_FILE=""
JSON_FLAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --subject)
            SUBJECT="$2"
            shift 2
            ;;
        --sender)
            SENDER="$2"
            shift 2
            ;;
        --body-file)
            BODY_FILE="$2"
            shift 2
            ;;
        --json)
            JSON_FLAG="--json"
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo "❌ Error: Unknown option: $1"
            echo ""
            print_usage
            exit 1
            ;;
    esac
done

# Check required argument
if [ -z "$BODY_FILE" ]; then
    echo "❌ Error: --body-file is required"
    echo ""
    print_usage
    exit 1
fi

# Check if file exists
if [ ! -f "$BODY_FILE" ]; then
    echo "❌ Error: File not found: $BODY_FILE"
    exit 1
fi

# Run the detector
python "PhishForge Detector.py" \
    --subject "$SUBJECT" \
    --sender "$SENDER" \
    --body-file "$BODY_FILE" \
    $JSON_FLAG
