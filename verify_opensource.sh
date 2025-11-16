#!/bin/bash
# Open Source Readiness Verification Script
# Run this script to verify your repository is ready for open source release

echo "🔍 Verifying open source readiness..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "1. Checking config.yaml is not tracked..."
if git ls-files | grep -q "^config\.yaml$"; then
    echo -e "   ${RED}❌ ERROR: config.yaml is tracked in git!${NC}"
    echo "   ACTION: Remove it with: git rm --cached config.yaml"
    ((ERRORS++))
else
    echo -e "   ${GREEN}✅ config.yaml is not tracked${NC}"
fi

echo ""
echo "2. Checking for real API keys in tracked files..."
# Look for patterns that look like actual API keys (long alphanumeric strings)
# Exclude code references like config['api']['amadeus_api_key']
FOUND_KEYS=$(git grep -iE "(amadeus_api_key|amadeus_api_secret)\s*:\s*[\"'][a-zA-Z0-9]{20,}" -- "*.py" "*.yaml" "*.md" 2>/dev/null | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example\|test_key\|test_secret\|config\[" || true)
if [ -n "$FOUND_KEYS" ]; then
    echo -e "   ${RED}❌ WARNING: Found potential API keys in tracked files!${NC}"
    echo "$FOUND_KEYS" | while IFS= read -r line; do
        echo "   $line"
    done
    ((WARNINGS++))
else
    echo -e "   ${GREEN}✅ No real API keys found in tracked files${NC}"
    echo "   (Code references to config keys are OK)"
fi

echo ""
echo "3. Checking for log files in git..."
LOG_FILES=$(git ls-files | grep "\.log$" || true)
if [ -n "$LOG_FILES" ]; then
    echo -e "   ${YELLOW}⚠️  WARNING: Log files are tracked in git${NC}"
    echo "$LOG_FILES" | while IFS= read -r file; do
        echo "   - $file"
    done
    ((WARNINGS++))
else
    echo -e "   ${GREEN}✅ No log files tracked${NC}"
fi

echo ""
echo "4. Checking for output files in git..."
OUTPUT_FILES=$(git ls-files | grep -E "\.csv$|flight_results\.html$" || true)
if [ -n "$OUTPUT_FILES" ]; then
    echo -e "   ${YELLOW}⚠️  WARNING: Output files are tracked in git${NC}"
    echo "$OUTPUT_FILES" | while IFS= read -r file; do
        echo "   - $file"
    done
    ((WARNINGS++))
else
    echo -e "   ${GREEN}✅ No output files tracked${NC}"
fi

echo ""
echo "5. Checking essential files exist..."
files=("README.md" "LICENSE" ".github/CONTRIBUTING.md" "CHANGELOG.md" "pyproject.toml" ".gitignore")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅ $file exists${NC}"
    else
        echo -e "   ${RED}❌ $file is missing!${NC}"
        ((ERRORS++))
    fi
done

echo ""
echo "6. Checking for placeholder email in pyproject.toml..."
if grep -q "your.email@example.com" pyproject.toml 2>/dev/null; then
    echo -e "   ${YELLOW}⚠️  WARNING: Placeholder email found in pyproject.toml${NC}"
    echo "   ACTION: Update author email in pyproject.toml"
    ((WARNINGS++))
else
    echo -e "   ${GREEN}✅ Author email is set${NC}"
fi

echo ""
echo "7. Checking CODE_OF_CONDUCT.md..."
if [ -f "CODE_OF_CONDUCT.md" ] || [ -f ".github/CODE_OF_CONDUCT.md" ]; then
    echo -e "   ${GREEN}✅ CODE_OF_CONDUCT.md exists${NC}"
else
    echo -e "   ${YELLOW}⚠️  INFO: CODE_OF_CONDUCT.md not found (optional but recommended)${NC}"
fi

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Repository appears ready for open source.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Verification complete with $WARNINGS warning(s).${NC}"
    echo "   Review warnings above before making repository public."
    exit 0
else
    echo -e "${RED}❌ Verification failed with $ERRORS error(s) and $WARNINGS warning(s).${NC}"
    echo "   Please fix errors before making repository public."
    exit 1
fi

