#!/usr/bin/env python3
"""Run the CLI inside the minimal filesystem for the existing HTTP/TLS tests.

Fixtures live under /runtime-rootfs/tmp. Translate their absolute paths before
entering the root so the client sees the same files as the external test server.
Test servers, Python, openssl, and reference curl stay outside the minimal root.
"""
import os
import sys

ROOT = '/runtime-rootfs'


def inside(argument):
    for prefix in (ROOT + '/', '@' + ROOT + '/'):
        if argument.startswith(prefix):
            return argument.replace(ROOT, '', 1)
    return argument


os.execv('/usr/sbin/chroot', ['chroot', ROOT, '/usr/local/bin/curl-impersonate',
                            *(inside(arg) for arg in sys.argv[1:])])
