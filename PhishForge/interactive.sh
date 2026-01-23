#!/bin/bash

# PhishForge Detector - Interactive Mode
# Guides you through email analysis step by step

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║      🛡️  PHISHFORGE DETECTOR - INTERACTIVE ANALYSIS               ║"
echo "║  Analyze a suspicious email step by step                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Function to read input with default value
read_with_default() {
    local prompt="$1"
    local default="$2"
    local value
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " value
        value="${value:-$default}"
    else
        read -p "$prompt: " value
    fi
    echo "$value"
}

echo "Let's analyze a suspicious email together!"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Email body
echo "📝 Step 1: Email Body"
echo "─────────────────────"
echo ""
echo "Choose how to provide the email body:"
echo "  1. Paste text directly (end with empty line + Ctrl+D)"
echo "  2. Provide file path"
echo ""
read -p "Choose option [1]: " BODY_OPTION
BODY_OPTION="${BODY_OPTION:-1}"

if [ "$BODY_OPTION" = "1" ]; then
    # Read multi-line input
    echo ""
    echo "Paste email body (press Ctrl+D when done):"
    echo "───────────────────────────────────────────"
    BODY_FILE="/tmp/phishforge_email_$$.txt"
    cat > "$BODY_FILE"
    
    if [ ! -s "$BODY_FILE" ]; then
        echo "❌ Error: No content provided"
        rm -f "$BODY_FILE"
        exit 1
    fi
else
    echo ""
    read -p "Enter path to email body file: " BODY_FILE
    
    if [ -z "$BODY_FILE" ]; then
        echo "❌ Error: Body file path is required"
        exit 1
    fi
    
    if [ ! -f "$BODY_FILE" ]; then
        echo "❌ Error: File not found: $BODY_FILE"
        exit 1
    fi
fi

echo ""
echo "✅ Email body loaded"
echo ""

# Step 2: Subject
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📧 Step 2: Email Subject"
echo "─────────────────────────"
echo ""
read -p "Subject [Unknown Subject]: " SUBJECT
SUBJECT="${SUBJECT:-Unknown Subject}"

echo ""
echo "✅ Subject: $SUBJECT"
echo ""

# Step 3: Sender
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "👤 Step 3: Email Sender"
echo "───────────────────────"
echo ""
echo "Format: Name <email@domain.com>"
read -p "Sender [Unknown Sender <unknown@unknown.com>]: " SENDER
SENDER="${SENDER:-Unknown Sender <unknown@unknown.com>}"

echo ""
echo "✅ Sender: $SENDER"
echo ""

# Step 4: Output format
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Step 4: Output Format"
echo "────────────────────────"
echo ""
echo "  1. Human-readable (colorful, educational)"
echo "  2. JSON (for scripts/automation)"
echo ""
read -p "Choose format [1]: " OUTPUT_CHOICE
OUTPUT_CHOICE="${OUTPUT_CHOICE:-1}"

JSON_FLAG=""
if [ "$OUTPUT_CHOICE" = "2" ]; then
    JSON_FLAG="--json"
fi

echo ""
echo "✅ Format selected"
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Analysis Summary"
echo "───────────────────"
echo ""
echo "  Subject:    $SUBJECT"
echo "  Sender:     $SENDER"
echo "  Body file:  $BODY_FILE"
echo "  Format:     $([ "$OUTPUT_CHOICE" = "2" ] && echo "JSON" || echo "Human-readable")"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"

echo ""
echo "🔍 Analyzing email..."
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Run the analysis
python "PhishForge Detector.py" \
    --subject "$SUBJECT" \
    --sender "$SENDER" \
    --body-file "$BODY_FILE" \
    $JSON_FLAG

EXIT_CODE=$?

# Cleanup temporary file if created
if [[ "$BODY_FILE" == /tmp/phishforge_email_* ]]; then
    rm -f "$BODY_FILE"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Analysis completed successfully!"
else
    echo "❌ Analysis failed with error code: $EXIT_CODE"
fi

echo ""
echo "Want to analyze another email? Run: ./interactive.sh"
echo "For quick analysis without prompts: ./analyze.sh --body-file <file>"
echo ""

exit $EXIT_CODE
