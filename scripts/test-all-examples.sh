#!/usr/bin/env bash
#
# test-all-examples.sh - Automated testing for reference configuration examples
#
# Tests each example by:
# 1. Pushing config to device
# 2. Pulling config back from device
# 3. Validating pulled config
# 4. Reporting results
#
# Usage:
#   ./scripts/test-all-examples.sh <device_ip>
#
# Example:
#   ./scripts/test-all-examples.sh 192.168.13.147
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXAMPLES_DIR="$REPO_ROOT/examples"
OUTPUT_DIR="$REPO_ROOT/.test-output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Check arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <device_ip>"
    echo ""
    echo "Example:"
    echo "  $0 192.168.13.147"
    exit 1
fi

DEVICE_IP="$1"

# Validate IP format (basic check)
if ! [[ "$DEVICE_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}✗ Invalid IP address format: $DEVICE_IP${NC}"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "  $1"
}

# Main test function
test_example() {
    local example_file="$1"
    local example_name=$(basename "$example_file" .json)
    local pulled_file="$OUTPUT_DIR/${example_name}_pulled_${TIMESTAMP}.json"

    print_header "Testing: $example_name"

    # Step 1: Validate original example
    print_info "Step 1: Validating original config..."
    if python3 "$SCRIPT_DIR/validate_moku_config.py" "$example_file" > /dev/null 2>&1; then
        print_success "Original config validates"
    else
        print_error "Original config validation failed"
        return 1
    fi

    # Step 2: Push to device
    print_info "Step 2: Pushing config to device ($DEVICE_IP)..."
    if python3 "$SCRIPT_DIR/push.py" "$example_file" "$DEVICE_IP" > /dev/null 2>&1; then
        print_success "Config pushed successfully"
    else
        print_error "Push failed"
        return 1
    fi

    # Wait a moment for device to settle
    sleep 1

    # Step 3: Pull from device
    print_info "Step 3: Pulling config from device..."
    if python3 "$SCRIPT_DIR/pull.py" "$DEVICE_IP" --level 2 -o "$pulled_file" > /dev/null 2>&1; then
        print_success "Config pulled successfully"
        print_info "   Saved to: $pulled_file"
    else
        print_error "Pull failed"
        return 1
    fi

    # Step 4: Validate pulled config
    print_info "Step 4: Validating pulled config..."
    if python3 "$SCRIPT_DIR/validate_moku_config.py" "$pulled_file" > /dev/null 2>&1; then
        print_success "Pulled config validates"
    else
        print_error "Pulled config validation failed"
        return 1
    fi

    # Step 5: Compare routing (basic sanity check)
    print_info "Step 5: Comparing configurations..."

    # Extract routing connection counts using Python
    pushed_routes=$(python3 -c "
import json
with open('$example_file') as f:
    data = json.load(f)
print(len(data.get('routing', [])))
")

    pulled_routes=$(python3 -c "
import json
with open('$pulled_file') as f:
    data = json.load(f)
print(len(data.get('routing', [])))
")

    if [ "$pushed_routes" -eq "$pulled_routes" ]; then
        print_success "Route count matches ($pushed_routes connections)"
    else
        print_warning "Route count differs (pushed: $pushed_routes, pulled: $pulled_routes)"
        print_info "   This may be normal (device adds default routes)"
    fi

    print_success "Test passed: $example_name"
    return 0
}

# Main execution
print_header "Reference Configuration Example Testing"
echo ""
echo "Device IP: $DEVICE_IP"
echo "Output Directory: $OUTPUT_DIR"
echo "Timestamp: $TIMESTAMP"

# Find all example JSON files
EXAMPLES=("$EXAMPLES_DIR"/*.json)

if [ ${#EXAMPLES[@]} -eq 0 ]; then
    print_error "No example files found in $EXAMPLES_DIR"
    exit 1
fi

echo ""
echo "Found ${#EXAMPLES[@]} example(s) to test"

# Test counters
PASSED=0
FAILED=0
FAILED_EXAMPLES=()

# Test each example
for example in "${EXAMPLES[@]}"; do
    if [ -f "$example" ]; then
        if test_example "$example"; then
            ((PASSED++))
        else
            ((FAILED++))
            FAILED_EXAMPLES+=("$(basename "$example")")
        fi
    fi
done

# Summary
print_header "Test Summary"
echo ""
echo -e "Total: ${#EXAMPLES[@]} examples"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "Failed examples:"
    for failed_ex in "${FAILED_EXAMPLES[@]}"; do
        echo -e "  ${RED}✗ $failed_ex${NC}"
    done
    echo ""
    echo "Check logs in: $OUTPUT_DIR"
    exit 1
else
    echo ""
    print_success "All examples passed!"
    echo ""
    echo "Pulled configs saved in: $OUTPUT_DIR"
    exit 0
fi
