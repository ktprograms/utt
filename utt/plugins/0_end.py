import argparse

from ..api import _v1


class EndHandler:
    def __init__(
        self, args: argparse.Namespace, now: _v1.Now, add_entry: _v1._private.AddEntry,
    ):
        self._args = args
        self._now = now
        self._add_entry = add_entry

    def __call__(self):
        self._add_entry(_v1.Entry(self._now, _v1.END_ENTRY_NAME, False))


end_command = _v1.Command(
    "end",
    "Say '{end_entry_name}' when you're done for the day...".format(end_entry_name=_v1.END_ENTRY_NAME),
    EndHandler,
    lambda p: None,
)

_v1.register_command(end_command)
