from datetime import datetime

from idv.common.fastway import get_client_from_settings
from idv.tracker.status_descriptions import map_status_to_description


def get_tracking_events(label_id):
    client = get_client_from_settings()
    events = client.get_tracking_events(label_id)
    return [get_displayable_event_info(event) for event in events]


def get_displayable_event_info(event):
    date = datetime.strptime(event['Date'], '%d/%m/%Y %H:%M:%S')
    return {
        'date': date.strftime('%B %d, %Y'),
        'time': date.strftime('%A, %I:%M %p'),
        'description': event['Description'],
        'status_scan': event['Status'],
        'status_description': map_status_to_description(event),
        'name': event['Name'],
        'franchisee': event['Franchise'],
        'recipient': event['CompanyInfo']
    }
