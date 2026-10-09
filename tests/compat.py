#!/usr/bin/env python3
"""Real HTTP/TLS compatibility checks; no public services required."""
import base64
import gzip
import http.server
import json
import os
from pathlib import Path
import ssl
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest

CLI = os.environ.get("CLI", str(Path(__file__).resolve().parents[1] / "target/debug/curl-impersonate"))
CURL = os.environ.get("REFERENCE_CURL", "curl")
BINARY = b"\x00\xffhello\r\n\x80world\n"


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "fixture"
    sys_version = ""

    def log_message(self, *_):
        pass

    def handle(self):
        # A client rejecting the test certificate may close after TLS setup.
        try:
            super().handle()
        except ConnectionResetError:
            pass

    def date_time_string(self, *_):
        return "Thu, 01 Jan 1970 00:00:00 GMT"

    def do_HEAD(self):
        self.respond()

    def do_GET(self):
        self.respond()

    def do_POST(self):
        self.respond()

    def do_PATCH(self):
        self.respond()

    def respond(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        code, headers = 200, []
        if self.path == "/bytes":
            payload = BINARY
        elif self.path == "/empty":
            code, payload = 204, b""
        elif self.path == "/gzip":
            payload = gzip.compress(BINARY)
            headers.append(("Content-Encoding", "gzip"))
        elif self.path == "/redirect":
            code, payload = 302, b"redirect body"
            headers.append(("Location", "/bytes"))
        elif self.path == "/redirect-post":
            code, payload = 302, b"redirect body"
            headers.append(("Location", "/echo"))
        elif self.path == "/redirect-host":
            code, payload = 302, b"redirect body"
            headers.append(("Location", f"http://localhost:{self.server.server_port}/echo"))
        elif self.path == "/missing":
            code, payload = 404, b"missing resource\n"
        elif self.path == "/slow":
            time.sleep(0.2)
            payload = b"late"
        elif self.path == "/set-cookie":
            headers.append(("Set-Cookie", "session=hello; Path=/"))
            payload = b"cookie saved"
        else:
            names = ["Content-Type", "Accept", "X-Test", "Cookie", "Authorization", "Referer"]
            payload = json.dumps({"method": self.command, "path": self.path,
                                  "body": base64.b64encode(body).decode(),
                                  "headers": {n.lower(): self.headers.get_all(n, []) for n in names}}, sort_keys=True).encode()
        self.send_response(code)
        for name, value in headers:
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            try:
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError, ssl.SSLError):
                pass


class Compatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.cert = cls.root / "cert.pem"
        key = cls.root / "key.pem"
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                        "-keyout", str(key), "-out", str(cls.cert), "-subj", "/CN=localhost",
                        "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"], check=True, capture_output=True)
        cls.tls = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cls.cert, key)
        cls.tls.socket = ctx.wrap_socket(cls.tls.socket, server_side=True)
        threading.Thread(target=cls.tls.serve_forever, daemon=True).start()
        cls.tls_url = f"https://127.0.0.1:{cls.tls.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tls.shutdown()
        cls.tls.server_close()
        cls.temp.cleanup()

    def run_cli(self, args, *, engine=CLI, data=None):
        env = {k: v for k, v in os.environ.items() if k.lower() not in
               {"http_proxy", "https_proxy", "all_proxy", "no_proxy", "curl_impersonate", "curl_impersonate_headers", "curl_ca_bundle", "ssl_cert_file", "ssl_cert_dir"}}
        return subprocess.run([engine, "-q", "-sS", *args], input=data, capture_output=True, env=env, timeout=10)

    def compare(self, args, *, data=None):
        actual = self.run_cli(args, data=data)
        expected = self.run_cli(args, engine=CURL, data=data)
        self.assertEqual(actual.returncode, expected.returncode, actual.stderr)
        self.assertEqual(actual.stdout, expected.stdout, actual.stderr)
        return actual

    def test_get_binary_and_headers(self):
        self.compare([self.url + "/bytes"])
        self.compare(["-i", self.url + "/bytes"])
        self.compare(["-I", self.url + "/bytes"])
        self.compare(["-H", "X-Test: one", "-H", "X-Test: two", "-e", "https://httpbin.org/get/", self.url + "/echo"])

    def test_request_data_and_method(self):
        self.compare(["-d", "a=1", "-d", "b=two", self.url + "/echo"])
        self.compare(["--data-raw", "@literal", "-XPATCH", self.url + "/echo"])
        self.compare(["-d", "", self.url + "/echo"])
        self.compare(["-G", "-d", "a=1", self.url + "/echo?x=2"])
        self.compare(["-G", "-d", "a=1", self.url + "/echo?"])
        self.compare(["--json", '{"x":1}', self.url + "/echo"])
        self.compare(["--json", '{}', "-H", "Content-Type: custom/test", "-H", "Accept: text/plain", self.url + "/echo"])

    def test_stdin_and_file_bodies_preserve_binary(self):
        self.compare(["--data-binary", "@-", self.url + "/echo"], data=BINARY)
        source = self.root / "body.bin"
        source.write_bytes(BINARY)
        self.compare(["--data-binary", "@" + str(source), self.url + "/echo"])
        # curl 7.88 (bookworm) handles embedded NULs differently from modern
        # curl. Assert the current documented --data behavior independently:
        # https://curl.se/docs/manpage.html#-d (strip CR, LF, and NUL from files).
        result = self.run_cli(["--data", "@" + str(source), self.url + "/echo"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(base64.b64decode(json.loads(result.stdout)["body"]), b"\xffhello\x80world")
        source.write_bytes(b"a=hello\r\n&b=world\n")
        self.compare(["--data", "@" + str(source), self.url + "/echo"])
        missing = self.run_cli(["--data-binary", "@" + str(self.root / "absent"), self.url + "/echo"])
        self.assertEqual(missing.returncode, 26)
        self.assertEqual(missing.stdout, b"")

    def test_redirects_and_credentials(self):
        self.compare(["-L", self.url + "/redirect"])
        self.compare(["-L", "-d", "value=1", self.url + "/redirect-post"])
        result = self.compare(["-L", "-u", "alice:secret", self.url + "/redirect-host"])
        self.assertEqual(json.loads(result.stdout)["headers"]["authorization"], [])
        self.compare(["-L", "--max-redirs", "0", self.url + "/redirect"])

    def test_http_errors_and_writeout(self):
        self.compare([self.url + "/missing"])
        self.compare(["-f", self.url + "/missing"])
        self.compare(["--fail-with-body", self.url + "/missing"])
        self.compare(["-L", "-w", r"\n%{http_code}|%{num_redirects}|%%\n", self.url + "/redirect"])
        self.compare(["-f", "-w", "%{http_code}|%{exitcode}", self.url + "/missing"])
        result = self.run_cli(["-s", "--no-show-error", "-f", self.url + "/missing"])
        self.assertEqual(result.returncode, 22)
        self.assertEqual(result.stderr, b"")

    def test_output_and_header_files(self):
        outputs = []
        for name, engine in [("ours", CLI), ("reference", CURL)]:
            body, headers = self.root / (name + ".bin"), self.root / (name + ".headers")
            result = self.run_cli(["-o", str(body), "-D", str(headers), "-w", "%{http_code}", self.url + "/bytes"], engine=engine)
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append((body.read_bytes(), headers.read_bytes(), result.stdout))
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[0][0], BINARY)

    def test_compression_timeout_and_proxy(self):
        self.assertEqual(self.compare(["--compressed", self.url + "/gzip"]).stdout, BINARY)
        self.compare(["--max-time", "0.025", self.url + "/slow"])
        result = self.compare(["--proxy", self.url, "--noproxy", "", "http://unresolved.invalid/proxy-check"])
        self.assertEqual(json.loads(result.stdout)["path"], "http://unresolved.invalid/proxy-check")

    def test_output_file_survives_errors_without_response_body(self):
        # A bound, unlistening socket cannot serve a response. macOS may report
        # a connection timeout instead of Linux's immediate refusal.
        with socket.socket() as closed:
            closed.bind(("127.0.0.1", 0))
            unreachable = f"http://127.0.0.1:{closed.getsockname()[1]}/"
            for args, codes in [(["--connect-timeout", "0.05", unreachable], (7, 28)), (["-f", self.url + "/missing"], (22,))]:
                for engine in (CLI, CURL):
                    output = self.root / "keep.bin"
                    output.write_bytes(b"KEEP")
                    result = self.run_cli(["-o", str(output), *args], engine=engine)
                    self.assertIn(result.returncode, codes, result.stderr)
                    self.assertEqual(output.read_bytes(), b"KEEP", (engine, args))
            output = self.root / "keep.bin"
            output.write_bytes(b"KEEP")
            result = self.run_cli(["-o", str(output), "--impersonate", "invalid-profile", self.url + "/bytes"])
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b"KEEP")
        for engine in (CLI, CURL):
            output = self.root / "empty.bin"
            output.write_bytes(b"REPLACE")
            result = self.run_cli(["-o", str(output), self.url + "/empty"], engine=engine)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), b"")
        for endpoint in ("/bytes", "/empty"):
            result = self.compare(["-o", str(self.root / "missing-directory" / "out.bin"),
                                   "-w", "%{exitcode}", self.url + endpoint])
            self.assertEqual(result.returncode, 23, result.stderr)

    def test_cookies(self):
        self.compare(["-b", "a=1", "-b", "b=2", self.url + "/echo"])
        jar = self.root / "cookies.txt"
        result = self.run_cli(["-c", str(jar), self.url + "/set-cookie"])
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.compare(["-b", str(jar), self.url + "/echo"])
        self.assertIn("session=hello", json.loads(result.stdout)["headers"]["cookie"][0])

    def test_tls_verification_is_on_by_default(self):
        self.assertEqual(self.run_cli([self.tls_url + "/bytes"]).returncode, 60)
        self.assertEqual(self.run_cli(["--cacert", str(self.cert), self.tls_url + "/bytes"]).stdout, BINARY)
        self.assertEqual(self.run_cli(["-k", self.tls_url + "/bytes"]).stdout, BINARY)

    def test_profile_selection_and_header_override(self):
        result = self.run_cli(["--impersonate", "chrome150", "-H", "Accept: application/json", self.url + "/echo"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["headers"]["accept"], ["application/json"])
        invalid = self.run_cli(["--impersonate", "not-a-browser", self.url + "/bytes"])
        self.assertNotEqual(invalid.returncode, 0)
        self.assertEqual(invalid.stdout, b"")

    def test_catalog_matches_the_native_engine(self):
        result = self.run_cli(["--list-profiles"])
        self.assertEqual(result.returncode, 0, result.stderr)
        profiles = result.stdout.decode().splitlines()
        self.assertIn("chrome150", profiles)
        self.assertIn("firefox147", profiles)
        self.assertIn("safari2601", profiles)
        self.assertEqual(len(profiles), len(set(profiles)))

    def test_http2_profile_on_local_tls_server(self):
        server = shutil.which("nghttpd")
        if not server:
            if os.environ.get("REQUIRE_HTTP2") == "1":
                self.fail("nghttpd is required for the Docker validation target")
            self.skipTest("nghttpd is not installed on this host; mandatory in Docker")
        (self.root / "resource.bin").write_bytes(BINARY)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        with tempfile.TemporaryFile() as log:
            process = subprocess.Popen([server, "-v", "-a", "127.0.0.1", "-d", str(self.root), str(port), str(self.root / "key.pem"), str(self.cert)], stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 5
                while True:
                    self.assertIsNone(process.poll(), "nghttpd exited before listening")
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                            break
                    except OSError:
                        if time.monotonic() >= deadline:
                            self.fail("nghttpd did not start")
                        time.sleep(0.02)
                result = self.run_cli(["--impersonate", "chrome150", "--cacert", str(self.cert), "--http2", "-w", "%{http_version}", f"https://127.0.0.1:{port}/resource.bin"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, BINARY + b"2")
            finally:
                process.terminate()
                process.wait(timeout=5)
            log.seek(0)
            observed = log.read().decode(errors="replace")
            self.assertIn("Chrome/150.0.0.0", observed)

    def test_unsupported_options_and_formats_are_explicit(self):
        for args in [["--retry", "2"], ["--next"], ["-w", "%{not_supported}"], ["-w", "%{http_code"], ["--config", "missing"], ["-I", "-d", "body"]]:
            result = self.run_cli([*args, self.url + "/bytes"])
            self.assertEqual(result.returncode, 2, (args, result.stderr))
            self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main(verbosity=2)
