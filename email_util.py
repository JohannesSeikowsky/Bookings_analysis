# email utilities
import smtplib, config

def send_email(target, subject, content):
	mail = smtplib.SMTP("smtp.gmail.com", 587)
	mail.ehlo()
	mail.starttls()

	gmail_acc = config.gmail_account
	gmail_pw = config.gmail_pw
	mail.login(gmail_acc, gmail_pw)

	msg_content = "Subject:{}\n\n{}".format(subject, content)
	mail.sendmail(gmail_acc, target, msg_content)
	mail.close()