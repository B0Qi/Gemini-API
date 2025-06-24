#!/bin/bash

echo "========================================="
echo "Gemini API Cookie Update Helper"
echo "========================================="
echo ""
echo "Please follow these steps to get new cookies:"
echo ""
echo "1. Open https://gemini.google.com in your browser"
echo "2. Log in with your Google account"
echo "3. Press F12 to open Developer Tools"
echo "4. Go to the 'Network' tab"
echo "5. Refresh the page (F5)"
echo "6. Click on any request to gemini.google.com"
echo "7. Find the 'Cookie' header in the Request Headers"
echo "8. Copy the values for __Secure-1PSID and __Secure-1PSIDTS"
echo ""
echo "========================================="
echo ""

read -p "Enter your __Secure-1PSID cookie: " PSID
read -p "Enter your __Secure-1PSIDTS cookie: " PSIDTS

# Create config.env file
cat > config.env << EOF
# Gemini API Configuration

# Required: Get these from https://gemini.google.com
SECURE_1PSID=$PSID
SECURE_1PSIDTS=$PSIDTS

# Optional: Server configuration
PORT=8080
HOST=0.0.0.0
EOF

echo ""
echo "✅ config.env has been updated with new cookies!"
echo ""
echo "You can now run: docker compose up -d"
echo ""