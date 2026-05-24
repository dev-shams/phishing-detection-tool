#!/bin/bash

# Email Phishing Detection Project - Cleanup Script
# This script safely removes unnecessary files to reduce project size
# Created: May 24, 2026

echo "=================================================="
echo "Email Phishing Detection - Project Cleanup"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Calculate initial size
echo "📊 Calculating initial project size..."
INITIAL_SIZE=$(du -sh . | cut -f1)
echo "Initial size: $INITIAL_SIZE"
echo ""

# Counters
FILES_DELETED=0
DIRS_DELETED=0

# Function to safely delete with confirmation
safe_delete() {
    local path=$1
    local description=$2

    if [ -e "$path" ]; then
        echo -e "${YELLOW}→${NC} $description"
        rm -rf "$path"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}  ✓ Deleted${NC}"
            ((FILES_DELETED++))
        else
            echo -e "${RED}  ✗ Failed to delete${NC}"
        fi
    fi
}

echo "🧹 Starting cleanup process..."
echo ""

# 1. Delete __pycache__ directories
echo "Step 1: Removing __pycache__ directories..."
PYCACHE_COUNT=$(find . -type d -name "__pycache__" | wc -l)
if [ $PYCACHE_COUNT -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    echo -e "${GREEN}✓ Removed $PYCACHE_COUNT __pycache__ directories${NC}"
    ((DIRS_DELETED += PYCACHE_COUNT))
else
    echo "No __pycache__ directories found"
fi
echo ""

# 2. Delete .DS_Store files
echo "Step 2: Removing .DS_Store files..."
DS_STORE_COUNT=$(find . -name ".DS_Store" | wc -l)
if [ $DS_STORE_COUNT -gt 0 ]; then
    find . -name ".DS_Store" -delete
    echo -e "${GREEN}✓ Removed $DS_STORE_COUNT .DS_Store files${NC}"
    ((FILES_DELETED += DS_STORE_COUNT))
else
    echo "No .DS_Store files found"
fi
echo ""

# 3. Delete temporary files
echo "Step 3: Removing temporary files..."
TEMP_COUNT=$(find . -name "~\$*" | wc -l)
if [ $TEMP_COUNT -gt 0 ]; then
    find . -name "~\$*" -delete
    echo -e "${GREEN}✓ Removed $TEMP_COUNT temporary files${NC}"
    ((FILES_DELETED += TEMP_COUNT))
else
    echo "No temporary files found"
fi
echo ""

# 4. Optional: Delete virtual environment
echo "Step 4: Virtual Environment Check"
if [ -d "Phase1_development/phishing_env" ]; then
    echo -e "${YELLOW}⚠ Found virtual environment (272 MB)${NC}"
    echo "This is SAFE to delete - can be recreated with:"
    echo "  python -m venv Phase1_development/phishing_env"
    echo "  source Phase1_development/phishing_env/bin/activate"
    echo "  pip install -r Phase1_development/requirements.txt"
    echo ""
    read -p "Delete virtual environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf Phase1_development/phishing_env
        echo -e "${GREEN}✓ Deleted virtual environment${NC}"
        ((DIRS_DELETED++))
    else
        echo "Keeping virtual environment"
    fi
else
    echo "No virtual environment found"
fi
echo ""

# 5. Optional: Delete screenshots
echo "Step 5: Screenshots Check"
SCREENSHOT_COUNT=$(find . -name "Screenshot*.png" | wc -l)
if [ $SCREENSHOT_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $SCREENSHOT_COUNT screenshots (~2.3 MB)${NC}"
    echo "These are safe to delete if you have them documented elsewhere"
    read -p "Delete screenshots? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find . -name "Screenshot*.png" -delete
        echo -e "${GREEN}✓ Deleted screenshots${NC}"
        ((FILES_DELETED += SCREENSHOT_COUNT))
    else
        echo "Keeping screenshots"
    fi
else
    echo "No screenshots found"
fi
echo ""

# 6. Optional: Delete debug files
echo "Step 6: Debug Files Check"
DEBUG_COUNT=$(find . -name "debug_*.py" -o -name "DIAGNOSIS_COMPLETE.txt" -o -name "IMMEDIATE_FIX*.py" | wc -l)
if [ $DEBUG_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $DEBUG_COUNT debug files${NC}"
    echo "These are safe to delete if debugging is complete"
    read -p "Delete debug files? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find . -name "debug_*.py" -delete 2>/dev/null
        find . -name "DIAGNOSIS_COMPLETE.txt" -delete 2>/dev/null
        find . -name "IMMEDIATE_FIX*.py" -delete 2>/dev/null
        echo -e "${GREEN}✓ Deleted debug files${NC}"
        ((FILES_DELETED += DEBUG_COUNT))
    else
        echo "Keeping debug files"
    fi
else
    echo "No debug files found"
fi
echo ""

# Calculate final size
echo "=================================================="
echo "📊 Cleanup Summary"
echo "=================================================="
FINAL_SIZE=$(du -sh . | cut -f1)
echo "Initial size: $INITIAL_SIZE"
echo "Final size:   $FINAL_SIZE"
echo "Files deleted: $FILES_DELETED"
echo "Directories deleted: $DIRS_DELETED"
echo ""
echo -e "${GREEN}✓ Cleanup completed successfully!${NC}"
echo ""

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Step 7: Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Temporary files
~$*
*.tmp
*.bak

# Virtual Environments
*/phishing_env/
*/venv/

# Logs
logs/
*.log

# Model checkpoints (if using for training)
# *.pkl
# Keep actual model files but ignore checkpoints

# Data (if too large, adjust as needed)
# raw_data/
# uploads/
EOF
    echo -e "${GREEN}✓ Created .gitignore${NC}"
fi

echo ""
echo "📝 Next steps:"
echo "1. Review deleted files in your recycle bin if needed"
echo "2. Commit changes to your version control"
echo "3. Read PROJECT_CLEANUP_ANALYSIS.md for detailed information"
echo ""
echo "Happy coding! 🚀"
