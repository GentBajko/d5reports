import json
from typing import Set, Dict, List, Union, Optional
import calendar
from datetime import date, datetime

from fastapi import (
    File,
    Form,
    Query,
    Depends,
    Request,
    APIRouter,
    UploadFile,
    HTTPException,
)
from fastapi.responses import HTMLResponse, RedirectResponse

from database.models import (
    user_mapper,  # noqa F401
    calendar_mapper,  # noqa F401
)
from core.models.user import User
from backend.dependencies import get_session
from database.models.mapper import mapper_registry  # noqa F401
from backend.utils.templates import templates
from backend.dependencies.auth import (
    is_admin,
    get_current_user,
)
from backend.utils.xlsx_parser import FileParser, IFileParser
from core.models.office_calendar import OfficeCalendar
from database.interfaces.session import ISession

calendar_router = APIRouter(prefix="/calendar")

attendance_data_store: Dict[str, Set[str]] = {}


@calendar_router.post("/upload_xlsx", response_class=RedirectResponse)
async def upload_xlsx(
    file: UploadFile = File(...),
    parser: IFileParser = Depends(FileParser),
    current_user: User = Depends(get_current_user),
    session: ISession = Depends(get_session),
):
    """
    Accepts an XLSX file upload, extracts attendance data in-memory, and updates the database.
    If the user dates match, sets OfficeCalendar.present to True.
    """
    if not is_admin(current_user):
        return RedirectResponse(url=f"/calendar/{current_user.id}", status_code=302)

    file_ext = file.filename.split(".")[-1] if file.filename else ""
    file_content = await file.read()
    data = parser.parse_bytes(file_content, file_ext)

    for day_key, names in data.items():
        try:
            day_date = datetime.strptime(day_key, "%Y-%m-%d").date()
        except ValueError:
            continue
        for full_name in names:
            user_record = session.query(User, full_name=full_name)
            if user_record:
                office_calendar = (
                    session.query(
                        OfficeCalendar, day=day_date, user_id=user_record[0].id
                    )  # noqa E501
                )
                if not office_calendar:
                    office_calendar = OfficeCalendar(
                        user_id=user_record[0].id, day=day_date, present=True
                    )
                    session.add(office_calendar)
                else:
                    office_calendar[0].present = True
    session.commit()

    return RedirectResponse(url="/calendar", status_code=302)


@calendar_router.get("/", response_class=HTMLResponse, response_model=None)
def get_all_remote(
    request: Request,
    year: Optional[int] = Query(None, description="Year for the calendar"),
    month: Optional[int] = Query(None, description="Month for the calendar"),
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Union[HTMLResponse, RedirectResponse]:
    """
    Returns a calendar view displaying days, highlighting users' presence with color coding.
    """
    if not is_admin(current_user):
        return RedirectResponse(url=f"/calendar/{current_user.id}", status_code=302)

    today = date.today()
    used_year = year if year else today.year
    used_month = month if month else today.month

    if not 1 <= used_month <= 12:
        raise HTTPException(status_code=400, detail="Invalid month value")

    first_day = date(used_year, used_month, 1)
    last_day = date(
        used_year, used_month, calendar.monthrange(used_year, used_month)[1]
    )

    all_users: List[User] = session.query(User)
    remote_days: List[OfficeCalendar] = session.query(
        OfficeCalendar,
        day__gte=first_day,
        day__lte=last_day,
    )

    user_dict: Dict[str, str] = {user.id: user.full_name for user in all_users}

    presence_by_date: Dict[date, Dict[str, bool]] = {}
    for rd in remote_days:
        if rd.day not in presence_by_date:
            presence_by_date[rd.day] = {}  # type: ignore
        user_full_name = user_dict.get(rd.user_id, "Unknown User")
        presence_by_date[rd.day][user_full_name] = rd.present  # type: ignore

    days_list = []
    cal = calendar.Calendar()
    for day_date in cal.itermonthdates(used_year, used_month):
        if day_date.month != used_month:
            continue
        date_key = day_date.isoformat()
        user_presence_map = presence_by_date.get(day_date, {})
        color_coded_users = []
        for user_full_name, present_val in user_presence_map.items():
            color_class = "text-green-500" if present_val else "text-red-500"
            color_coded_users.append(
                {"name": user_full_name, "color_class": color_class}
            )
        day_obj = {
            "day_number": day_date.day,
            "day_name": day_date.strftime("%A"),
            "date_iso": date_key,
            "users": color_coded_users,
            "is_weekend": day_date.weekday() >= 5,
        }
        days_list.append(day_obj)

    month_name = datetime(used_year, used_month, 1).strftime("%B")

    return templates.TemplateResponse(
        "calendar/all.html",
        {
            "request": request,
            "days": days_list,
            "current_month_name": month_name,
            "current_month": used_month,
            "current_year": used_year,
        },
    )

@calendar_router.get("/{user_id}", response_class=HTMLResponse)
def get_user_remote(
    request: Request,
    user_id: str,
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """
    Returns the user's remote-days page for the given year and month.
    """
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Access forbidden")
    today = date.today()
    used_year = year if year else today.year
    used_month = month if month else today.month
    first_day = date(used_year, used_month, 1)
    last_day = date(
        used_year, used_month, calendar.monthrange(used_year, used_month)[1]
    )
    remote_days = session.query(
        OfficeCalendar,
        user_id=user_id,
        day__gte=first_day,
        day__lte=last_day,
    )
    selected_dates = set(rd.day for rd in remote_days)
    days_list = []
    cal = calendar.Calendar()
    for day_date in cal.itermonthdates(used_year, used_month):
        if day_date.month != used_month:
            continue
        day_obj = {
            "day_number": day_date.day,
            "day_name": day_date.strftime("%A"),
            "date_iso": day_date.isoformat(),
            "is_selected": day_date in selected_dates,
            "has_event": day_date in selected_dates,
        }
        days_list.append(day_obj)
    month_name = datetime(used_year, used_month, 1).strftime("%B")
    return templates.TemplateResponse(
        "calendar/user.html",
        {
            "request": request,
            "days": days_list,
            "user_id": user_id,
            "current_month_name": month_name,
            "current_month": used_month,
            "current_year": used_year,
        },
    )

@calendar_router.post("/{user_id}", response_class=HTMLResponse)
def post_user_remote(
    request: Request,
    user_id: str,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    selected_dates: str = Form(...),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """
    Saves and removes user remote days for a given year and month.
    """
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Access forbidden")
    try:
        selected_date_list = json.loads(selected_dates)
        selected_date_set = set(
            datetime.strptime(d, "%Y-%m-%d").date() for d in selected_date_list
        )
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=400, detail="Invalid date format"
        ) from e
    today = date.today()
    used_year = year if year else today.year
    used_month = month if month else today.month
    first_day = date(used_year, used_month, 1)
    last_day = date(
        used_year, used_month, calendar.monthrange(used_year, used_month)[1]
    )
    existing_remote_days = session.query(
        OfficeCalendar,
        user_id=user_id,
        day__gte=first_day,
        day__lte=last_day,
    )
    existing_dates = set(rd.day for rd in existing_remote_days)
    dates_to_add = selected_date_set - existing_dates
    dates_to_remove = existing_dates - selected_date_set
    for day in dates_to_add:
        rd = OfficeCalendar(user_id=user_id, day=day)
        session.add(rd)
    if not is_admin(current_user):
        dates_to_remove = {d for d in dates_to_remove if d >= today}
    if dates_to_remove:
        to_remove = session.query(
            OfficeCalendar,
            user_id=user_id,
            in_={OfficeCalendar.day: list(dates_to_remove)},
        )
        for rd in to_remove:
            session.delete(rd)
    session.commit()
    return RedirectResponse(
        url=f"/calendar/{user_id}?year={used_year}&month={used_month}",
        status_code=302,
    )