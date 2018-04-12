def create_data(data):
    return f'data: {data}\n\n'


def create_event(data, event_name, event_id=None):
    event_id_row = f'id: {event_id}\n' if event_id else ''
    return f'event: {event_name}\n' \
           f'{event_id_row}' \
           f'data: {data}\n\n'
