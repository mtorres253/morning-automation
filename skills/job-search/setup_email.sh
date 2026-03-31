#!/bin/bash

# Email setup helper for job-search skill

echo "🔧 Job Search Email Setup"
echo "=========================="
echo ""
echo "This script will help you configure Gmail to send job search digests."
echo ""
echo "Step 1: Go to https://myaccount.google.com/ and enable 2-factor authentication"
echo "Step 2: Generate an app password at https://myaccount.google.com/apppasswords"
echo "        (Select Mail and your device type)"
echo "Step 3: Copy the 16-character password"
echo ""

read -p "Press Enter once you have your app password ready..."

# Create secrets directory
mkdir -p ~/.openclaw/secrets

# Get credentials from user
read -p "Enter your Gmail address: " email
read -sp "Enter your 16-character app password: " password
echo ""

# Create config file
cat > ~/.openclaw/secrets/email_config.json << EOF
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "$email",
  "sender_password": "$password"
}
EOF

# Secure the file
chmod 600 ~/.openclaw/secrets/email_config.json

echo ""
echo "✓ Email config saved to ~/.openclaw/secrets/email_config.json"
echo ""
echo "Testing email delivery..."
echo ""

cd "$(dirname "$0")"
python3 scripts/filter_and_deliver.py

echo ""
echo "✓ Setup complete! Your job search digest is ready."
echo ""
echo "The daily cron job will run at 9 AM PDT and send results to: $email"
