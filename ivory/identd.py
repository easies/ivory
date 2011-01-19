# A proper identification protocol (RFC 1413) implementation,
# providing all the utility, security, and authentication
# of all other implementations of this protocol, without
# all the expensive and pointless grovelling in /dev/kmem.
#
# Careful design and software engineering makes this software
# efficient, fast, compact, scalable, and completely maintenance free.
#
# Anyone who feels the need to use a daemon more complex than this one
# should go read section 6 of RFC 1413 very carefully, and think again.
#
# Erik E. Fair <fair@clock.org>, February 1, 2000

# This runs under inetd, with the following configuration:
# ident  stream tcp  nowait  nobody  /usr/local/libexec/identd  identd
#
# There are two mutually exclusive options:
# -h	- always reply that the user is hidden
# -u	- always reply that there was an unknown error

#include <sys/types.h>
#include <sys/time.h>
#include <sys/uio.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>

#define	STDIN	0
#define	STDOUT	1

HIDING = ":ERROR:HIDDEN-USER\r\n"
UNKNOWN = ":ERROR:UNKNOWN-ERROR\r\n"
RESPERR = "0,0:ERROR:INVALID-PORT\r\n"
RESPONSE = "%s:USERID:OTHER:%lu-ident-is-a-completely-pointless-protocol-that-offers-no-security-or-traceability-at-all-so-take-this-and-log-it!\r\n"


MAXREAD = 1024

import time
import os
import sys


def MakeItAllUp(query):
    tod = time.time()
    pid = os.getpid()
    return RESPONSE % (query, tod % pid)


def main():
    buf = sys.stdin.read(MAXREAD)
    buf = buf.strip()

    if buf is None or len(buf) <= 0:
        os.exit(1)

	p = buf.split('\r', 2)[0]

    if len(sys.argv) > 1 and len(sys.argv[1]) > 1:
        c = sys.argv[1][1]
        if c == 'h':
            p = buf + HIDING
        elif c == 'u':
            p = buf + UNKNOWN
        else:
            p = MakeItAllUp(buf)
    else:
        p = MakeItAllUp(buf)

    sys.stdout.write(p)


if __name__ == '__main__':
    main()
