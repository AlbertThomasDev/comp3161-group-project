"""Lightweight model helpers used by routers.

This module provides small dataclass representations and helpers to
convert DB row dictionaries into typed objects. The project uses raw
SQL and dictionary cursors; these helpers are optional conveniences
for serialization and validation.

Keep this file minimal so routers can import model helpers when useful.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

ALLOWED_EVENT_TYPES = ('assignment', 'lecture', 'exam')


@dataclass
class CalendarEvent:
	event_id: Optional[int]
	course_id: int
	title: str
	description: Optional[str]
	event_date: str  # YYYY-MM-DD
	event_type: str


def event_from_row(row: Dict[str, Any]) -> CalendarEvent:
	"""Convert a DB row (dict) into a CalendarEvent dataclass."""
	return CalendarEvent(
		event_id=row.get('event_id'),
		course_id=row['course_id'],
		title=row.get('title') or '',
		description=row.get('description'),
		event_date=str(row.get('event_date')),
		event_type=row.get('event_type')
	)


def events_from_rows(rows: List[Dict[str, Any]]) -> List[CalendarEvent]:
	return [event_from_row(r) for r in rows]


__all__ = [
	'CalendarEvent',
	'event_from_row',
	'events_from_rows',
	'ALLOWED_EVENT_TYPES',
]

