import json
import socket
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from aapp.network_active_scan import ALLOWED, BLOCKED, run_file, scan_request
from aapp.network_scope import authorize_request, validate_scope


FIXTURES = Path(__file__).parent / "fixtures" / "network_scope"


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def scope_for_port(port, methods=None):
    return {
        "schema_version": "aapp.network_scope.v1",
        "scope_id": "dynamic-local-scope",
        "authorized_by": "test",
        "created_at": "2026-01-01T00:00:00Z",
        "expires_at": "2099-01-01T00:00:00Z",
        "allowed_targets": ["127.0.0.1"],
        "allowed_ports": [port],
        "allowed_methods": methods or ["tcp_connect", "http_head", "http_get"],
        "rate_limit": {"max_attempts": 10, "min_interval_ms": 0},
        "purpose": "local test only",
        "no_exploit": True,
    }


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_missing_scope_blocks_without_network_attempt():
    result = scan_request(None, {"target": "127.0.0.1", "port": 1, "method": "tcp_connect"})
    assert result["decision"] == BLOCKED
    assert result["reason"] == "missing_scope_artifact"
    assert result["network_attempted"] is False


def test_out_of_scope_target_blocks():
    scope = scope_for_port(12345)
    result = authorize_request(
        scope,
        {"target": "localhost", "port": 12345, "method": "tcp_connect"},
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert result["allowed"] is False
    assert result["reason"] == "target_not_in_scope"


def test_out_of_scope_port_blocks():
    scope = scope_for_port(12345)
    result = authorize_request(
        scope,
        {"target": "127.0.0.1", "port": 54321, "method": "tcp_connect"},
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert result["allowed"] is False
    assert result["reason"] == "port_not_in_scope"


def test_out_of_scope_method_blocks():
    scope = scope_for_port(12345, methods=["tcp_connect"])
    result = authorize_request(
        scope,
        {"target": "127.0.0.1", "port": 12345, "method": "http_get"},
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert result["allowed"] is False
    assert result["reason"] == "method_not_in_scope"


def test_expired_scope_blocks():
    scope = scope_for_port(12345)
    scope["expires_at"] = "2020-01-01T00:00:00Z"
    result = validate_scope(scope, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert result["allowed"] is False
    assert result["reason"] == "scope_expired"


def test_prohibited_mode_blocks():
    scope = scope_for_port(12345)
    result = authorize_request(
        scope,
        {
            "target": "127.0.0.1",
            "port": 12345,
            "method": "tcp_connect",
            "exploit": True,
        },
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert result["allowed"] is False
    assert result["reason"] == "prohibited_mode_requested"


def test_tcp_connect_allowed_only_with_scope(tmp_path):
    port = free_port()
    ready = threading.Event()

    def server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            s.listen(1)
            ready.set()
            conn, _ = s.accept()
            conn.close()

    thread = threading.Thread(target=server, daemon=True)
    thread.start()
    ready.wait(timeout=2)

    scope_path = tmp_path / "scope.artifact.json"
    request_path = tmp_path / "request.json"
    write_json(scope_path, scope_for_port(port, methods=["tcp_connect"]))
    write_json(request_path, {"target": "127.0.0.1", "port": port, "method": "tcp_connect", "timeout_s": 1.0})

    result = run_file(scope_path, request_path, tmp_path / "out")

    assert result["decision"] == ALLOWED
    assert result["network_attempted"] is True
    assert result["result"]["status"] == "open"
    assert (tmp_path / "out" / "network.scan.json").exists()
    assert (tmp_path / "out" / "network.report.md").exists()


def test_http_head_allowed_on_local_server(tmp_path):
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

        def log_message(self, format, *args):
            return

    port = free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        scope_path = tmp_path / "scope.artifact.json"
        request_path = tmp_path / "request.json"
        write_json(scope_path, scope_for_port(port, methods=["http_head"]))
        write_json(request_path, {"target": "127.0.0.1", "port": port, "method": "http_head", "path": "/", "timeout_s": 1.0})

        result = run_file(scope_path, request_path, tmp_path / "out")

        assert result["decision"] == ALLOWED
        assert result["network_attempted"] is True
        assert result["result"]["status"] == "http_response"
        assert result["result"]["http_status"] == 200
    finally:
        server.shutdown()


def test_cli_blocked_result_is_machine_readable(tmp_path):
    request_path = tmp_path / "request.json"
    write_json(request_path, {"target": "127.0.0.1", "port": 1, "method": "tcp_connect"})

    result = run_file(None, request_path, tmp_path / "out")
    verdict = json.loads((tmp_path / "out" / "network.scan.json").read_text())

    assert result["decision"] == BLOCKED
    assert verdict["decision"] == BLOCKED
    assert verdict["network_attempted"] is False
