from .google_auth import get_calendar_service
from datetime import datetime, timedelta

def get_free_slots():
    # Use Google Calendar API to get events and find gaps
    pass

def get_busy_slots(start: datetime, end: datetime):
    service = get_calendar_service()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    busy_slots = []
    for event in events:
        busy_slots.append({
            'start': event['start'].get('dateTime'),
            'end': event['end'].get('dateTime')
        })
    return busy_slots

def book_slot(start_time: datetime, end_time: datetime):
    service = get_calendar_service()
    event = {
        'summary': 'TailorTalk Booking',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }
    service.events().insert(calendarId='primary', body=event).execute()
    return True

def check_availability(start: datetime, end: datetime):
    busy_slots = get_busy_slots(start, end)
    if not busy_slots:
        return True  # No busy slots, available for booking
    for slot in busy_slots:
        slot_start = datetime.fromisoformat(slot['start'])
        slot_end = datetime.fromisoformat(slot['end'])
        if (start < slot_end and end > slot_start):
            return False  # Overlaps with a busy slot
    return True  # No overlaps, available for booking