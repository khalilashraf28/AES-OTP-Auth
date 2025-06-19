# import smtplib
# import random
# from email.message import EmailMessage

# def send_otp(receiver_email):
#     otp = str(random.randint(100000, 999999))
#     msg = EmailMessage()
#     msg.set_content(f"Your OTP is {otp}")
#     msg["Subject"] = "Your OTP for 2FA System"
#     msg["From"] = "khalilashraf28@gmail.com"  # Replace with your email
#     msg["To"] = receiver_email

#     server = smtplib.SMTP("smtp.gmail.com", 587)
#     server.starttls()
#     server.login("khalilashraf28@gmail.com", "madhcoxlmllofqqv")
#     server.send_message(msg)
#     server.quit()
#     return otp


import smtplib
import random
from email.message import EmailMessage

def send_otp(receiver_email):
    otp = str(random.randint(100000, 999999))
    msg = EmailMessage()
    msg.set_content(f"Your OTP is {otp}")
    msg["Subject"] = "Your OTP for 2FA System"
    msg["From"] = "khalilashraf28@gmail.com"  
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("khalilashraf28@gmail.com", "madhcoxlmllofqqv")  # Use App Password
        server.send_message(msg)
        server.quit()
        return otp
    except Exception as e:
        print(f"Email sending failed: {e}")
        return None  # Handle this in calling code

# send_otp('khalil_ashraf47@yahoo.com')