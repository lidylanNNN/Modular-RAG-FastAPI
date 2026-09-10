'''Trace recording primitives.'''

from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class Trace:
    '''Minimal trace record for one application operation.'''

    trace_id: str
    started_at: float = field(default_factory=perf_counter)
    events: list[dict] = field(default_factory=list)

    def add_event(self, name: str, payload: dict | None = None) -> None:
        '''Append a named event to the trace.'''
        self.events.append({'name': name, 'payload': payload or {}})

