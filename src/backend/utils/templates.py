from datetime import datetime
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/backend/templates")

def date_to_string(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object.strftime("%d-%m-%Y %H:%M:%S")

templates.env.filters['date_to_string'] = date_to_string