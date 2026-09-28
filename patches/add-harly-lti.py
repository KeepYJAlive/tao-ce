#!/usr/bin/env python3
"""Insert Harly LTI entries into the base image's authoritative template.

Deliberately fail closed on upstream layout changes or repeated application.
All checks run before writing; existing upstream content is preserved verbatim.
"""

import re
import sys
from pathlib import Path


def patch(source):
    def unique(anchor):
        count = source.count(anchor)
        if count != 1:
            raise ValueError(f"expected exactly one {anchor!r}; found {count}")

    platforms = "        ltiPlatforms: [\n"
    registrations = "        ltiRegistrations: [\n"
    tools = "        ltiTools: [\n"
    deliver = "            id: 'nextgen-tao-deliver-be-tool',\n"
    for anchor in (platforms, registrations, tools, deliver):
        unique(anchor)
    if not source.index(platforms) < source.index(registrations) < source.index(tools) < source.index(deliver):
        raise ValueError("unexpected upstream LTI section order")
    for identifier in ("harly-platform", "lti-harly-deliver-#tenantId#", "harly-tao-f3695cee-3122-4e89-a2ce-c0c4ef364718"):
        if identifier in source:
            raise ValueError(f"Harly identifier already present: {identifier}")

    # Every existing Deliver registration must use the expected EM expression.
    jwks = "'%s/.well-known/jwks.json' % setup.apps['environment-management'].auth_server.http.url"
    upstream_registrations = source[source.index(registrations):source.index(tools)]
    deliver_refs = re.findall(r"^            toolId: 'nextgen-tao-deliver-be-tool',\n", upstream_registrations, re.M)
    expressions = re.findall(r"^            toolId: 'nextgen-tao-deliver-be-tool',\n            toolJwksUrl: (.+),\n", upstream_registrations, re.M)
    if not deliver_refs or len(expressions) != len(deliver_refs) or set(expressions) != {jwks}:
        raise ValueError("missing or ambiguous upstream Deliver JWKS expression")

    platform = """          {
            audience: 'https://opportunities.keepyjalive.org',
            id: 'harly-platform',
            isInternal: false,
            name: 'Harly LTI Platform',
            oauth2AccessTokenUrl: 'https://opportunities.keepyjalive.org/api/integrations/tao/lti/token',
            oidcAuthenticationUrl: 'https://opportunities.keepyjalive.org/api/integrations/tao/lti/authorize',
          },
"""
    registration = """          {
            clientId: 'harly-tao-f3695cee-3122-4e89-a2ce-c0c4ef364718',
            deploymentIds: ['f0d717d2-02ff-468e-bfea-e59c65ce4e75'],
            id: 'lti-harly-deliver-#tenantId#',
            platformId: 'harly-platform',
            platformJwksUrl: 'https://opportunities.keepyjalive.org/api/integrations/tao/lti/jwks',
            platformKeyChain: {},
            toolId: 'nextgen-tao-deliver-be-tool',
            toolJwksUrl: JWKS_EXPRESSION,
            toolKeyChain: {},
          },
""".replace("JWKS_EXPRESSION", jwks)
    return source.replace(platforms, platforms + platform).replace(registrations, registrations + registration)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    try:
        result = patch(path.read_text())
    except ValueError as error:
        sys.exit(f"Harly LTI patch refused: {error}")
    path.write_text(result)
    print("Harly LTI patch: added platform and Deliver registration")
