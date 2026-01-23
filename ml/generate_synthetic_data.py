"""
Generate synthetic phishing email dataset for training.

This creates a realistic dataset when Kaggle data is not available.
"""

import pandas as pd
from pathlib import Path

# Phishing email examples
phishing_emails = [
    {
        "subject": "Urgent: Verify your PayPal account",
        "body": "Your PayPal account has been limited. Please verify your information immediately by clicking here: http://paypal-verify.com/login",
        "label": 1
    },
    {
        "subject": "Action Required: Suspended Account",
        "body": "Dear customer, your account will be permanently deleted within 24 hours unless you confirm your identity. Click here to restore access.",
        "label": 1
    },
    {
        "subject": "Security Alert: Unusual Activity Detected",
        "body": "We detected suspicious activity on your Amazon account. Verify your credentials now: http://amazon-security.xyz/verify",
        "label": 1
    },
    {
        "subject": "Your package could not be delivered",
        "body": "Your package delivery failed. Update your address here to reschedule: http://fedex-tracking.tk/update",
        "label": 1
    },
    {
        "subject": "Netflix: Payment Failed",
        "body": "Your payment method was declined. Update your billing information to continue watching: http://netflix-billing.ga/fix",
        "label": 1
    },
    {
        "subject": "Your Apple ID was locked",
        "body": "For security reasons, your Apple ID has been locked. Click here to unlock: http://apple-id-verify.ml/unlock",
        "label": 1
    },
    {
        "subject": "Microsoft Account: Suspicious Sign-in",
        "body": "Someone tried to access your Microsoft account. Confirm your identity immediately: http://microsoft-security.cf/confirm",
        "label": 1
    },
    {
        "subject": "Bank Alert: Unauthorized Transaction",
        "body": "We detected an unauthorized transaction of $1,249.99. Click here to dispute: http://secure-banking.xyz/dispute",
        "label": 1
    },
    {
        "subject": "You've won a $1000 Amazon Gift Card!",
        "body": "Congratulations! You've been selected to receive a $1000 gift card. Claim your prize now: http://amazon-prize.top/claim",
        "label": 1
    },
    {
        "subject": "IRS: Tax Refund Pending",
        "body": "You have a pending tax refund of $2,847. Provide your bank details to receive it: http://irs-refund.icu/claim",
        "label": 1
    },
    {
        "subject": "Your Instagram account will be deleted",
        "body": "Your account violated our policies and will be deleted. Appeal here: http://instagram-appeal.work/verify",
        "label": 1
    },
    {
        "subject": "Facebook Security: Verify Your Identity",
        "body": "We need to verify your identity to prevent your account from being disabled. Click here: http://facebook-verify.click/confirm",
        "label": 1
    },
    {
        "subject": "LinkedIn: Someone viewed your profile",
        "body": "Premium member viewed your profile. See who: http://linkedin-premium.xyz/view (requires login)",
        "label": 1
    },
    {
        "subject": "Google: Unusual sign-in activity",
        "body": "Sign-in attempt from unknown device. Verify it was you: http://google-security.tk/verify",
        "label": 1
    },
    {
        "subject": "Dropbox: Storage Full",
        "body": "Your Dropbox is full. Upgrade to premium now: http://dropbox-upgrade.ga/premium",
        "label": 1
    },
    {
        "subject": "Zoom: Meeting Link - Action Required",
        "body": "You've been invited to a meeting. Login to join: http://zoom-meeting.cf/join?id=12345",
        "label": 1
    },
    {
        "subject": "Adobe: Your license has expired",
        "body": "Your Creative Cloud license expired. Renew now to continue: http://adobe-renewal.ml/renew",
        "label": 1
    },
    {
        "subject": "Spotify: Update Payment Method",
        "body": "Your payment failed. Update your card to keep listening: http://spotify-payment.icu/update",
        "label": 1
    },
    {
        "subject": "eBay: Account Limited",
        "body": "Your eBay account has been limited due to unusual activity. Restore access: http://ebay-restore.top/verify",
        "label": 1
    },
    {
        "subject": "GitHub: Security Alert",
        "body": "Suspicious activity detected on your GitHub account. Review activity: http://github-alert.xyz/review",
        "label": 1
    }
]

# Legitimate email examples
legitimate_emails = [
    {
        "subject": "Meeting tomorrow at 2pm",
        "body": "Hi team, just a reminder about our project sync meeting tomorrow at 2pm in conference room B. Please bring your status updates.",
        "label": 0
    },
    {
        "subject": "Invoice #12345 - Payment Received",
        "body": "Thank you for your payment. Your invoice #12345 has been marked as paid. Receipt attached.",
        "label": 0
    },
    {
        "subject": "Weekly Newsletter - Tech News",
        "body": "Here are this week's top technology stories: AI breakthroughs, new programming languages, and cloud computing trends.",
        "label": 0
    },
    {
        "subject": "Your order has shipped",
        "body": "Good news! Your order #789456 has been shipped and will arrive by Friday. Track your package using the link in your account.",
        "label": 0
    },
    {
        "subject": "Welcome to our service",
        "body": "Thank you for signing up! We're excited to have you. Check out our getting started guide to make the most of your account.",
        "label": 0
    },
    {
        "subject": "Project update - Q4 deliverables",
        "body": "Hi everyone, here's an update on our Q4 project timeline. All milestones are on track and we're planning the final review for December 15th.",
        "label": 0
    },
    {
        "subject": "Lunch plans for Friday?",
        "body": "Hey, want to grab lunch on Friday? There's a new Italian restaurant downtown I've been wanting to try.",
        "label": 0
    },
    {
        "subject": "Your subscription renewal",
        "body": "Your annual subscription will renew on January 1st. No action needed - we'll use your payment method on file.",
        "label": 0
    },
    {
        "subject": "Conference registration confirmed",
        "body": "Your registration for TechConf 2025 is confirmed. Event details and schedule are available in your account dashboard.",
        "label": 0
    },
    {
        "subject": "Monthly report - October 2025",
        "body": "Please find attached the monthly performance report for October. Key highlights: 15% growth in user engagement and 8% increase in conversions.",
        "label": 0
    },
    {
        "subject": "Team building event next month",
        "body": "We're organizing a team building event on November 20th. Please fill out the survey to help us plan activities and catering.",
        "label": 0
    },
    {
        "subject": "Code review requested",
        "body": "Hi, I've submitted PR #456 for the new authentication feature. Would you mind reviewing when you have a chance? Thanks!",
        "label": 0
    },
    {
        "subject": "Happy birthday!",
        "body": "Wishing you a wonderful birthday filled with joy and happiness! Hope you have a great celebration today.",
        "label": 0
    },
    {
        "subject": "Document shared with you",
        "body": "Sarah shared 'Q4 Budget Proposal' with you on Google Drive. You have edit access to this document.",
        "label": 0
    },
    {
        "subject": "Reminder: dental appointment tomorrow",
        "body": "This is a reminder of your dental appointment tomorrow at 10:30am. Please arrive 10 minutes early to complete paperwork.",
        "label": 0
    },
    {
        "subject": "Thank you for your purchase",
        "body": "We appreciate your business! Your order is being processed and you'll receive shipping confirmation soon.",
        "label": 0
    },
    {
        "subject": "New feature announcement",
        "body": "We're excited to introduce dark mode! Update your app to access this and other new features. Learn more in our blog post.",
        "label": 0
    },
    {
        "subject": "Password changed successfully",
        "body": "Your password was changed successfully on November 27, 2025 at 3:45pm. If you didn't make this change, please contact support.",
        "label": 0
    },
    {
        "subject": "Survey: Help us improve",
        "body": "We'd love to hear your feedback! Please take 2 minutes to complete our user satisfaction survey. Your input helps us improve.",
        "label": 0
    },
    {
        "subject": "Webinar recording available",
        "body": "Thank you for attending yesterday's webinar! The recording and slides are now available in your account under Resources.",
        "label": 0
    }
]

def generate_dataset():
    """Generate synthetic dataset and save to CSV."""
    # Combine all emails
    all_emails = phishing_emails + legitimate_emails
    
    # Create variations by duplicating with slight modifications
    expanded_emails = []
    for email in all_emails:
        # Add original
        expanded_emails.append(email)
        
        # Create variations (simple text modifications)
        for i in range(2):  # 2 variations per email
            variation = {
                "subject": email["subject"],
                "body": email["body"] + f" [Ref: {i+1}]",
                "label": email["label"]
            }
            expanded_emails.append(variation)
    
    # Create DataFrame
    df = pd.DataFrame(expanded_emails)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to CSV
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "phishing_email_dataset.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✅ Generated synthetic dataset: {output_file}")
    print(f"   Total samples: {len(df)}")
    print(f"   Phishing: {df['label'].sum()}")
    print(f"   Legitimate: {len(df) - df['label'].sum()}")
    print(f"\nDataset structure:")
    print(df.head())
    
    return output_file

if __name__ == "__main__":
    generate_dataset()
