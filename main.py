# Booking Analysis Code
import gspread, pprint
from oauth2client.service_account import ServiceAccountCredentials
from email_util import send_email
from datetime import *
import config


# connect to Google-spreadsheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(config.path_to_code + "client_secret.json", scope)
client = gspread.authorize(creds)
google_sheet = client.open(config.spreadsheet).sheet1

# Construct a dict with keys being the holiday homes
# and key being a list of 2 lists, with first one being the arrivals for that home, second one the departures
# based on the google sheet
head_row = google_sheet.row_values(1)
hol_homes = {}

for each in head_row:
	if each:
		hol_homes[each] = [head_row.index(each)+1, head_row.index(each)+2]

for hol_home, vals in hol_homes.items():
	vals[0] = google_sheet.col_values(vals[0])[1:]
	vals[1] = google_sheet.col_values(vals[1])[1:]


# Feature 1 - "Guest-changes" this week
def move_outs_this_week():
	first_email = "Diese Woche werden folgende Wohnungen an folgenden Tagen frei: \n\n"
	todays_date = datetime.today()
	move_outs = {}

	for hol_home, vals in hol_homes.items():
		# find those departure dates that are happening this week.
		for each in vals[1]:
			dep_date = datetime.strptime(each, '%d.%m.%Y')
			if dep_date > todays_date and dep_date < todays_date + timedelta(days=7):
				move_outs[hol_home] = dep_date.strftime("%A - %d.%m")

	for hol_home, date in move_outs.items():
		first_email = first_email + "- " + hol_home + " on " + date + "\n"

	first_email = first_email + "\n Reminder - Diese Auswertung beruht auf den Daten, die jetzt gerade in dem Spreadsheet angegeben sind."
	first_email = first_email + "\n Daher koennen diese Auswertung und die Luecken-analyse nur mit Sicherheit korrekt sein, wenn der Spreadsheet up-to-date ist."
	return first_email


# Feature 2 - Booking gap analysis
def booking_gap_analysis():
	second_email = ""
	todays_date = datetime.today()

	for hol_home, vals in hol_homes.items():
		no_of_gaps = 0
		arr_dates = vals[0]
		dep_dates = vals[1]

		# add first part to email msg stating until when the apartment is booked
		second_email = second_email + hol_home + "\n" 
		second_email = second_email + "Ist gebucht bis zum " + dep_dates[-1] + ". \n"
		second_email = second_email + "Luecken bis dahin: \n"

		# add second part to email msg identifying larger gaps in the booking
		for dep in dep_dates:
			dep_date = datetime.strptime(dep, '%d.%m.%Y')
			if dep_date > todays_date:	
				for arr in arr_dates:
					arr_date = datetime.strptime(arr, '%d.%m.%Y')
					if arr_date >= dep_date:
						delta = arr_date - dep_date
						
						significant_gap_size = 3
						if delta.days > significant_gap_size:
							# append relevant data to email
							no_of_gaps += 1
							second_email = second_email + str(delta.days) + " Tage - " + "zwischen dem " + dep_date.strftime("%d.%m") + " und dem " + arr_date.strftime("%d.%m") + "\n"
						break
		
		# Changing message accordingly if there no significant gaps
		if no_of_gaps == 0:
			second_email = second_email + "--- \n"

		second_email = second_email + "\n\n"
	return second_email


# only run code if not already run today
with open(config.path_to_code + "done_dates.txt") as f:
	done_dates = f.read().split("/")

date_today = datetime.today().strftime('%d.%m.%Y')
if not date_today in done_dates:
	# run code
	try: 
		first_email = move_outs_this_week()
		second_email = booking_gap_analysis()

		# Send Emails - each to Muddi and myself
		recipient = config.recipient_email
		subject = "Bettenwechsel diese Woche"
		content = first_email
		send_email(recipient, subject , content)
		recipient = config.my_email
		send_email(recipient, subject, content)
		
		recipient = config.recipient_email
		subject = "Einfache Auslastungsanalyse - Ferienwohnungen"
		content = second_email
		send_email(recipient, subject, content)
		recipient = config.my_email		
		send_email(recipient, subject, content)

		# write execution to recording file
		with open(config.path_to_code + "done_dates.txt", "a") as f:
			f.write(date_today + "/")

	except Exception as e:
		recipient = config.my_email
		subject = "Exception thrown when running FeWo code"
		content = str(e)
		# print(content)
		send_email(recipient, subject, content)