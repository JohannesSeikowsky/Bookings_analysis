import os

# private data is set locally as environment variables
# and assigned to application-specifc config variables here 
gmail_account = os.environ["EMAIL_ACC"]
gmail_pw = os.environ["EMAIL_PW"]
path_to_code = os.environ["BOOKINGS_ANALYSIS_PATH"]
spreadsheet = os.environ["BOOKINGS_ANALYSIS_SHEET"]
my_email = os.environ["EMAIL_ACC"]
recipient_email = os.environ["MUMS_EMAIL"]