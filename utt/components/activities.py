import datetime
import itertools
from typing import List, Optional

from ..constants import END_ENTRY_NAME
from ..data_structures.activity import Activity
from ..data_structures.entry import Entry
from .entries import Entries
from .local_timezone import LocalTimezone
from .now import Now
from .report_args import DateRange, ReportArgs

Activities = List[Activity]


def filter_activities_by_project(activities: Activities, project_name: Optional[str]):
    for activity in activities:
        if project_name is None or project_name == activity.name.project:
            yield activity


def filter_activities_by_range(activities: Activities, date_range: DateRange, local_timezone: LocalTimezone):
    start_datetime = local_timezone.localize(
        datetime.datetime(date_range.start.year, date_range.start.month, date_range.start.day)
    )
    end_datetime = local_timezone.localize(
        datetime.datetime(date_range.end.year, date_range.end.month, date_range.end.day, 23, 59, 59, 99999)
    )

    for full_activity in activities:
        activity = full_activity.clip(start_datetime, end_datetime)
        if activity.duration > datetime.timedelta():
            yield activity


def get_current_activity(
    current_activity_name: Optional[str],
    last_entry: Optional[Entry],
    now: Now,
    start_datetime: datetime,
    end_datetime: datetime,
) -> Optional[Activity]:
    if current_activity_name is None or last_entry is None or last_entry.name == "end":
        return

    last_entry_time = max(last_entry.datetime, start_datetime)

    now_is_between_last_entry_and_end_report_range = last_entry_time < now <= end_datetime
    if not now_is_between_last_entry_and_end_report_range:
        return

    return Activity(f"{current_activity_name} {last_entry.name}", last_entry_time, now, True)


def remove_end_activities(activities):
    for activity in activities:
        if activity.name.name != END_ENTRY_NAME:
            yield activity


def activities(report_args: ReportArgs, now: Now, local_timezone: LocalTimezone, entries: Entries) -> Activities:
    activities = list(_activities(entries))
    _filtered_activities = list(filter_activities_by_range(activities, report_args.range, local_timezone))

    start_datetime = local_timezone.localize(
        datetime.datetime(
            year=report_args.range.start.year, month=report_args.range.start.month, day=report_args.range.start.day
        )
    )

    end_datetime = local_timezone.localize(
        datetime.datetime(
            year=report_args.range.end.year, month=report_args.range.end.month, day=report_args.range.end.day
        )
        + datetime.timedelta(days=1)
    )

    last_entry = entries[-1] if entries else None
    current_activity = get_current_activity(
        report_args.current_activity_name, last_entry, now, start_datetime, end_datetime
    )
    if current_activity is not None:
        _filtered_activities.append(current_activity)

    _filtered_activities = list(remove_end_activities(_filtered_activities))
    _filtered_activities = list(filter_activities_by_project(_filtered_activities, report_args.project_name_filter))

    return _filtered_activities


def _activities(entries: Entries):
    for prev_entry, next_entry in _pairwise(entries):
        activity = Activity(
            prev_entry.name,
            prev_entry.datetime,
            next_entry.datetime,
            False,
            comment=next_entry.comment,
        )
        yield activity


def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
