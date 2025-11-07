from copy import deepcopy
from unittest.mock import MagicMock
import os
import sys
import types

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class _DummyApp:
    def __init__(self, *args, **kwargs):
        pass

    def action(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def shortcut(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def view_closed(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


class _DummySocketModeHandler:
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass


fake_slack_bolt = types.ModuleType("slack_bolt")
fake_slack_bolt.App = _DummyApp
adapter_module = types.ModuleType("slack_bolt.adapter")
socket_mode_module = types.ModuleType("slack_bolt.adapter.socket_mode")
socket_mode_module.SocketModeHandler = _DummySocketModeHandler
adapter_module.socket_mode = socket_mode_module
fake_slack_bolt.adapter = adapter_module
sys.modules.setdefault("slack_bolt", fake_slack_bolt)
sys.modules.setdefault("slack_bolt.adapter", adapter_module)
sys.modules.setdefault("slack_bolt.adapter.socket_mode", socket_mode_module)

os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test-token")
os.environ.setdefault("SLACK_APP_TOKEN", "xapp-test-token")

import _app


@pytest.fixture
def ack():
    return MagicMock()


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def mock_client(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(_app, "client", client)
    return client


@pytest.fixture
def base_body():
    return {
        "actions": [
            {
                "selected_options": [],
            }
        ],
        "view": {
            "id": "V123",
            "hash": "H123",
            "state": {
                "values": {
                    "call_to_action": {
                        "call_to_action-action": {
                            "selected_options": [],
                        }
                    }
                }
            },
        },
    }


@pytest.fixture
def sender_only_payload(base_body):
    body = deepcopy(base_body)
    body["actions"][0]["selected_options"] = [{"value": "value-0"}]
    return body


@pytest.fixture
def cta_only_payload(base_body):
    body = deepcopy(base_body)
    body["view"]["state"]["values"]["call_to_action"]["call_to_action-action"]["selected_options"] = [
        {"value": "value-1"}
    ]
    body["view"]["state"]["values"]["call_to_action_dropdown"] = {
        "call_to_action_dropdown-action": {
            "selected_option": {"value": "1"}
        }
    }
    return body


@pytest.fixture
def both_selected_payload(cta_only_payload):
    body = deepcopy(cta_only_payload)
    body["actions"][0]["selected_options"] = [{"value": "value-0"}]
    return body


@pytest.fixture
def neither_selected_payload(base_body):
    return deepcopy(base_body)


def _extract_blocks(mock_client):
    assert mock_client.views_update.called, "Expected views_update to be called"
    return mock_client.views_update.call_args.kwargs["view"]["blocks"]


def test_sender_only_adds_sender_fields(ack, logger, mock_client, sender_only_payload):
    _app.handle_customize_sender_id_checkbox(ack=ack, body=sender_only_payload, logger=logger)

    ack.assert_called_once_with()

    expected_blocks = [
        _app.advanced_options_blocks[0],
        *_app.sender_identity_fields,
        _app.advanced_options_blocks[1],
    ]

    assert _extract_blocks(mock_client) == expected_blocks


def test_cta_only_adds_cta_blocks_with_buttons(ack, logger, mock_client, cta_only_payload):
    _app.handle_customize_sender_id_checkbox(ack=ack, body=cta_only_payload, logger=logger)

    ack.assert_called_once_with()

    expected_blocks = [
        *_app.advanced_options_blocks,
        *_app.call_to_action_dropdown,
        *_app.generate_cta_buttons(1),
    ]

    assert _extract_blocks(mock_client) == expected_blocks


def test_both_selected_combines_sender_and_cta_blocks(ack, logger, mock_client, both_selected_payload):
    _app.handle_customize_sender_id_checkbox(ack=ack, body=both_selected_payload, logger=logger)

    ack.assert_called_once_with()

    expected_blocks = [
        _app.advanced_options_blocks[0],
        *_app.sender_identity_fields,
        _app.advanced_options_blocks[1],
        *_app.call_to_action_dropdown,
        *_app.generate_cta_buttons(1),
    ]

    assert _extract_blocks(mock_client) == expected_blocks


def test_neither_selected_resets_to_default_blocks(ack, logger, mock_client, neither_selected_payload):
    _app.handle_customize_sender_id_checkbox(ack=ack, body=neither_selected_payload, logger=logger)

    ack.assert_called_once_with()

    expected_blocks = _app.advanced_options_blocks

    assert _extract_blocks(mock_client) == expected_blocks
