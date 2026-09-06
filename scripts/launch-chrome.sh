#!/usr/bin/env bash
# ==============================================================================
# Job Terminator - macOS Chrome CDP Launcher
# Target Host: Mac Mini 2018 (Intel Core i5) running macOS Sequoia
# ==============================================================================

PORT="${1:-9222}"
PROFILE_DIR="${HOME}/.chrome-job-terminator"
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

echo -e "\033[0;36m====================================================\033[0m"
echo -e "\033[0;36m 🤖 Job Terminator - Chrome CDP Launcher (macOS)\033[0m"
echo -e "\033[0;36m====================================================\033[0m"

# 1. Verify Google Chrome is installed
if [ ! -f "$CHROME_BIN" ]; then
    echo -e "\033[0;31mError: Google Chrome not found at $CHROME_BIN\033[0m"
    echo -e "\033[0;33mPlease install Google Chrome via Homebrew:\033[0m"
    echo "  brew install --cask google-chrome"
    exit 1
fi

echo -e "\033[0;32mFound Google Chrome at: $CHROME_BIN\033[0m"

# 2. Check if port is already active
if lsof -Pi :"$PORT" -sTCP:LISTEN -t >/dev/null ; then
    echo -e "\033[0;33mPort $PORT is already in use by another process.\033[0m"
    echo -e "\033[0;32mChrome remote debugging appears to already be active on port $PORT.\033[0m"
    echo -e "\033[0;36mVerify at: http://localhost:$PORT/json/version\033[0m"
    exit 0
fi

# 3. Create persistent profile directory if not present
mkdir -p "$PROFILE_DIR"
echo -e "\033[0;33mUsing dedicated automation profile at: $PROFILE_DIR\033[0m"

# 4. Launch Chrome with CDP
echo -e "\033[0;32mLaunching Google Chrome with CDP on port $PORT...\033[0m"
echo -e "\033[0;33mTIP: Log into your job sites (LinkedIn, Indeed, Glassdoor, etc.) in this window.\033[0m"
echo -e "\033[0;33mYour cookies and login sessions will remain permanently saved.\033[0m\n"

nohup "$CHROME_BIN" \
    --remote-debugging-port="$PORT" \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check > /dev/null 2>&1 &

sleep 2

# 5. Verify CDP port listening
if lsof -Pi :"$PORT" -sTCP:LISTEN -t >/dev/null ; then
    echo -e "\033[0;32mSUCCESS: Chrome is actively listening for CDP on port $PORT!\033[0m"
    echo -e "\033[0;36mCDP Endpoint: http://localhost:$PORT\033[0m"
else
    echo -e "\033[0;33mNotice: Chrome launched. Check http://localhost:$PORT/json/version to verify.\033[0m"
fi
