MAPPED_STATUSES = {
    'R02': 'Received in Hub - Portarlington Co Laois',
    'R10': 'Received in DEPOT - Dublin',
    'ONB': 'On Board with courier',
    'A51': 'Customer Collected and Paid'
}


def map_status_to_description(event):
    if event['Status'] in MAPPED_STATUSES:
        return MAPPED_STATUSES[event['Status']]
    else:
        return event['TypeVerbose']
