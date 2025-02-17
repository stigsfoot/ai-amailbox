def categorize_mail(mail_text):
    if "Current Resident" in mail_text or "Occupant" in mail_text:
        return "Spam"
    elif "Bank" in mail_text or "IRS" in mail_text:
        return "Important"
    else:
        return "Unknown"

if __name__ == "__main__":
    sample_text = "Dear Current Resident, You may have won a prize!"
    print(f"Mail Category: {categorize_mail(sample_text)}")
