import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime as dt
from datetime import timedelta


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def main():
  cwd = os.getcwd()  # Get the current working directory (cwd)
  files = os.listdir(cwd)  # Get all the files in that directory
  print("Files in %r: %s" % (cwd, files))
  
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print(now)
    timeMax = SevenDaysOut(now)
    print(timeMax)
    # print("Getting the upcoming 10 events")

    # Retrieve the list of calendars
    calendar_list = service.calendarList().list().execute()

    hashmap = {}

    # Iterate through the calendars
    for calendar in calendar_list['items']:
      if calendar.get('summary', 'No summary') == "LDM: General" or calendar.get('summary', 'No summary') == "Neurotech@Davis Projects Calendar":
          continue
      print('------------------------------------------')
      print('Calendar ID:', calendar['id'])
      print('Summary:', calendar.get('summary', 'No summary'))
      print('Description:', calendar.get('description', 'No description'))
      print('------------------------------------------')

      events_result = service.events().list(calendarId=calendar['id'], timeMin=now, timeMax=timeMax ,showDeleted=False, singleEvents=True).execute()
      events = events_result.get("items", [])
      
      if not events:
          print("No upcoming events found.")
          continue

      counter = 0
      for event in events:
          counter += 1
          if event["status"] != "cancelled":
              start = event["start"].get("dateTime", event["start"].get("date"))
              print(start, event["summary"], counter)
              
              # (self, ref, calendar, name, date, description, start, end)
              cal = calendar.get('summary')
              name = event["summary"]
              date = start[:10]
              description = event.get("description", None)
              if "date" in event["start"]:
                startTime = None
                endTime = None
              else: # assuming dateTime is 
                timeString = event["start"].get("dateTime")
                startTime = int(timeString[11:13] + timeString[14:16])
                timeString = event["end"].get("dateTime")
                endTime = int(timeString[11:13] + timeString[14:16])
              MyEvent = EventObject(event, cal, name, date, description, startTime, endTime)


              if date in hashmap: # NEEDS TO BE SORTED
                event_list = hashmap[start[:10]]
                if startTime == None: # If no time
                  event_list.insert(0, MyEvent)
                  continue
                inserted = False
                for i in range(len(event_list)): # If does have time
                  if event_list[i].start == None:
                    continue
                  if startTime < event_list[i].start:
                    event_list.insert(i, MyEvent)
                    inserted = True
                    break
                if not inserted: 
                  event_list.append(MyEvent) 

              else:
                hashmap[date] = [MyEvent]
                  
          # else:
          #     original = service.events().get(calendarId=calendar['id'], eventId=event['id'])
          #     print(original)
    print("Done :P")
        

    # events_result = (
    #     service.events()
    #     .list(
    #         calendarId="primary",
    #         timeMin=now,
    #         maxResults=10,
    #         singleEvents=True,
    #         orderBy="startTime",
    #     )
    #     .execute()
    # )
    

  except HttpError as error:
    print(f"An error occurred: {error}")



class EventObject:
  def __init__(self, ref, calendar, name, date, description, start, end) -> None:
    self.event = ref # Reference to OG event
    self.calendar = calendar
    self.name = name # Event name (summary)
    self.date = date # Event date
    self.description = description # The comments/description to event
    self.start = start # Event start time
    self.end = end # Event end time

  def __str__(self) -> str:
    return f"{self.date}, {self.start}, {self.end}, {self.name}"
  def __repr__(self) -> str:
    return f"{self.date}, {self.start}, {self.end}, {self.name}"


def SevenDaysOut(now): # EX: 2024-04-29T04:32:38.486550Z
  # Convert string to datetime object
  date_object = dt.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')

  # Add 7 days to the date
  future_date = date_object + timedelta(days=7)

  # Return the future date as a string in the same format
  return future_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

# Set-ExecutionPolicy Unrestricted -Scope Process
if __name__ == "__main__":
  main()