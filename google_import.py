from __future__ import print_function
import csv
from datetime import datetime
import json
import pickle
import os.path
import re
import requests
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .settings_minerva2gcal import CAL_ID,MINERVA_CREDS

SCOPES = ['https://www.googleapis.com/auth/calendar']
REJECTS = [
    'travel\/private study',
    'Self Directed Learning',
    'ILA groups (24-30|1-8|9-16)',
    'Personal\/Self directed study',
    'Early Years .* Class B',
    'Prescribing Session',
    'Prescribing Answers Session',
    'Travel Time',
    'Dedicated Free Time',
    'Microbiology practical.*Class B',
    'Personal\/Private study time'
]

class CalendarWrapper:
    def __init__(self, csvdata, rejects, scopes, calendarId):
        self.csvdata = csvdata
        self.csvobj = csv.reader(self.csvdata[1:])
        self.rejects = []
        self.rejected = 0
        self.added = 0
        self.deleted = 0
        self._creds = None
        self._service = None
        self.scopes = scopes
        self.calendarId = calendarId
        self.headers = next(csv.reader(self.csvdata))
        for pattern in rejects:
            self.rejects.append(re.compile(pattern))

    def __iter__(self):
        return self

    def __next__(self):
        line = self._list_to_dict(next(self.csvobj))
        while self._should_reject(line['Subject']):
            self.rejected += 1
            line = self._list_to_dict(next(self.csvobj))
        return self._row_to_event(line)

    def _list_to_dict(self, row):
        return dict(zip(self.headers, row))

    def _should_reject(self, subject):
        for expression in self.rejects:
            if expression.search(subject):
                return True
        return False

    def _date_conv(self, date, time):
        date = datetime.strptime(date+' '+time, '%d/%m/%Y %H:%M:%S')
        return date.isoformat() + 'Z'

    def _row_to_event(self, row):
        return {
            "summary": row['Subject'],
            "start": {
                "timeZone": "Europe/London",
                "dateTime": self._date_conv(
                    row['Start Date'],
                    row['Start Time']
                ),
            },
            "location": row['Location'],
            "end": {
                "timeZone": "Europe/London",
                "dateTime": self._date_conv(
                    row['End Date'],
                    row['End Time']
                ),
            },
            "kind": "calendar#event",
            "locked": True,
        }

    @property
    def service(self):
        if self._service is not None:
            return self._service
        creds = self.creds
        self._service = build('calendar', 'v3', credentials=creds)
        return self._service

    @property
    def creds(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self._creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self._creds or not self._creds.valid:
            if (
                self._creds and
                self._creds.expired and
                self._creds.refresh_token
            ):
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                self._creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self._creds, token)
        return self._creds

    def delete_all(self):
        events_service = self.service.events()
        events = events_service.list(
            calendarId=self.calendarId,
            showDeleted=True
        ).execute()
        next_page_token = events['nextPageToken'] if 'nextPageToken' in events else None
        batch = self.service.new_batch_http_request()
        for event in events['items']:
            batch.add(events_service.delete(
                calendarId=self.calendarId,
                eventId=event['id']
            ))
        batch.execute()
        self.deleted += len(events['items'])
        print(f"Deleted {len(events['items'])}")
        while nextPageToken is not None:
            batch = self.service.new_batch_http_request()
            for event in events['items']:
                batch.add(events_service.delete(
                    calendarId=self.calendarId,
                    eventId=event['id']
                ))
            batch.execute()
            self.deleted += len(events['items'])
            print(f"Deleted {len(events['items'])}")
            events = events_service.list(
                calendarId=self.calendarId,
                showDeleted=True,
                pageToken=next_page_token
            ).execute()
            next_page_token = events['nextPageToken'] if 'nextPageToken' in events else None
        return True

    def add_events(self, events):
        events_service = self.service.events()
        batch = self.service.new_batch_http_request()
        for event in events:
            batch.add(events_service.insert(
                calendarId=self.calendarId,
                body=event
            ))
        batch.execute()
        self.added = len(events)
        return True

    def import_csv(self):
        events = []
        headers = self.headers
        for event in self:
            events.append(event)
        return events

    def print_calendars(self):
        lis = self.service.calendarList()
        for cal in lis.list().execute()['items']:
            print(f"{cal['summary']} ({cal['id']})")


def download_from_minerva():
    print("Downloading calendar from Minerva")
    s = requests.Session()
    cred = MINVERVA_CREDS
    r = s.post('https://minerva.shef.ac.uk/minerva/med/index.php', data=cred)
    r.raise_for_status()
    r = s.get('https://minerva.shef.ac.uk/minerva/med/scripts/process_lect_'
                'export_timetable_student.php?t=2A_18_19&m=CSM1')
    r.raise_for_status()
    return r.text.splitlines()

def main():
    cal = download_from_minerva()
    calendar = CalendarWrapper(cal, REJECTS, SCOPES, CAL_ID)
    calendar.delete_all()
    if calendar.deleted is 0:
        print("Didn't find any events to delete, so quitting to prevent "
              "duplicates")
        sys.exit(1)
    print(f'Deleted total of {calendar.deleted} events from the calendar')
    events = calendar.import_csv()
    print(f'Ignoring {calendar.rejected} events from CSV that match the '
           'reject list')
    calendar.add_events(events)
    print(f'Added {calendar.added} events to the calendar')
    print(f'Diff = {calendar.added - calendar.deleted}')

if __name__ == '__main__':
    main()
