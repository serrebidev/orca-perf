# Orca
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""speech_emitted fires for characters, not only for speak()."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


def _server(test_context: OrcaTestContext):
    test_context.setup_shared_dependencies()
    from orca import speechdispatcherfactory

    server = speechdispatcherfactory.SpeechServer.__new__(speechdispatcherfactory.SpeechServer)
    server._client = mock.Mock()
    server._apply_acss = mock.Mock()
    server._send_command = mock.Mock()
    server._speak = mock.Mock()
    server._emit_speech_emitted = mock.Mock()
    return speechdispatcherfactory, server


def _key_event(name: str, locking_state: str = ""):
    event = mock.Mock()
    event.get_key_name.return_value = name
    event.get_locking_state_string.return_value = locking_state
    return event


@pytest.mark.unit
class TestCharacterSpeechEmitted:
    def test_speak_character_emits(self, test_context: OrcaTestContext) -> None:
        _module, server = _server(test_context)
        server.speak_character("a")
        server._emit_speech_emitted.assert_called_once_with("a", None)
        server._send_command.assert_called_once_with(server._client.char, "a")

    def test_speak_character_icon_style_emits_once(self, test_context: OrcaTestContext) -> None:
        module, server = _server(test_context)
        server.speak_character("A", cap_style=module.CapitalizationStyle.ICON)
        server._emit_speech_emitted.assert_called_once_with("A", None)
        server._speak.assert_called_once()

    def test_single_character_key_event_emits(self, test_context: OrcaTestContext) -> None:
        _module, server = _server(test_context)
        server.speak_key_event(_key_event("a"))
        server._emit_speech_emitted.assert_called_once_with("a", None)

    def test_named_key_event_emits_once_through_speak(self, test_context: OrcaTestContext) -> None:
        _module, server = _server(test_context)
        server.speak = mock.Mock()
        server.speak_key_event(_key_event("left control"))
        server._emit_speech_emitted.assert_not_called()
        server.speak.assert_called_once_with("left control", acss=None)
