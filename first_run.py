#from google_import import CalendarWrapper, SCOPES
from getpass import getpass
import os

def setup_api():
    print("1.  Create a project at https://console.developers.google.com/start/api?id=calendar")
    print("    This may take a few minutes, so be patient")
    print("2.  Click 'Go to credentials'")
    print("3.  Click 'Cancel'")
    print("4.  At the top of the page, select the OAuth consent screen tab.")
    print("    Select an email address")
    print("    Enter a product name if not already set (such as 'UoS Minerva Medicine Importer')")
    print("    Click the save button.")
    print("5.  Click the credentials tab at the tob of the page")
    print("6.  Click 'Create credentials' button and select 'OAuth client ID'")
    print("7.  Select 'Other'")
    print("    Give a suitable name")
    print("    Proceed to the next screen")
    print("8.  On the credential you just created, click the download button and save the file as credentials.json in the same folder as this program")
    input("9.  Press enter when you've done this")
    return os.path.isfile('credentials.json')

def setup_minerva():
    minerva_user = input("1.  Input your minerva username and press enter: ")
    print("    Next, input your password, but be aware it will not be shown as screen as you type")
    minerva_pass = getpass("2.  Input your minerva password and press enter: ")
    return minerva_user, minerva_pass

def setup_calendar():
    print("1.  Go to Google Calendar")
    print("2.  Go to the settings for the calendar, scroll down and copy the calendar ID")
    print("    It should be something like fsdgjoisjgoiewj389jwojqngown@group.calendar.google.com")
    cal_id = input("Input the calendar ID and press enter: ")
    return cal_id

def write_settings(minerva, cal_id):
    with open("settings_minerva2gcal.py", "w") as f:
        f.write(f'CAL_ID = "{cal_id}"\r\n')
        f.write(f'MINERVA_CREDS = {{"user": "{minerva[0]}", "pass": "{minerva[1]}"}}\r\n')
        f.write('REJECTS = []\r\n')

def main():
    while setup_api() is False:
        print("=========================")
        input("It looks like that didn't work. Press enter to restart")
        print("=========================")
        setup_api()
    print("=========================")
    print("Now the Google Calendar API is set up, we'll configure minerva")
    minerva_creds = setup_minerva()
    print("=========================")
    print("Now, let's configure which calendar to use")
    cal_id = setup_calendar()
    write_settings(minerva_creds, cal_id)
    print("=========================")
    print("Authorising your application... If instructions below, follow them")
    print("If you are prompted to log into Google, log into an account that has write access to the calendar you specified")
    import google_import
    from settings_minerva2gcal import CAL_ID
    cal = google_import.CalendarWrapper([""], [], google_import.SCOPES, CAL_ID)
    cal.service
    print("=========================")
    print("Successfully setup. Now you can use google_import.py")

if __name__ == '__main__':
    main()
