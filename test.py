import smtplib

# Email credentials
sender_email = "sritree15@outlook.com"
sender_password = "Sritree@1515"

# Email details
receiver_email = "shivamsawarn15@gmail.com"
subject = "Subject of the email"
body = "This is the body of the email."

# Create the message
message = f"Subject: {subject}\n\n{body}"

# Send the email
try:
    with smtplib.SMTP("smtp-mail.outlook.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, receiver_email, message)
    print("Email sent successfully!")
except Exception as e:
    print(f"An error occurred: {e}")