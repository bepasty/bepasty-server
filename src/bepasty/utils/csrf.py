"""
Protection against cross-site request forgery (CSRF).

Browsers send credentials (the session cookie, but also cached HTTP Basic auth
credentials) with requests that other sites trigger, e.g. by auto-submitting a
form. Without protection, a malicious site could make a logged-in user delete,
lock, unlock or modify items, upload items or log in with a token of the
attacker.

We reject state-changing requests that a browser marks as cross-origin, using
the Sec-Fetch-Site and Origin request headers. Modern browsers send these
headers and scripts on other sites cannot forge them. Non-browser clients
(e.g. the REST API used by command line clients) usually send neither of them,
so their requests are not affected.

This follows the algorithm used by Go's net/http CrossOriginProtection.
"""

from urllib.parse import urlsplit

from flask import render_template, request

# Request methods that must not change state, see RFC 9110.
SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS', 'TRACE'})


def is_cross_origin_request():
    """
    Check whether the current request was made cross-origin by a browser.
    """
    if request.method in SAFE_METHODS:
        return False

    sec_fetch_site = request.headers.get('Sec-Fetch-Site')
    if sec_fetch_site is not None:
        # "none" means the user triggered the request directly (e.g. via a bookmark).
        # "same-site" (another origin on the same site, e.g. a subdomain) is rejected.
        return sec_fetch_site not in ('same-origin', 'none')

    origin = request.headers.get('Origin')
    if origin is None:
        # No Sec-Fetch-Site and no Origin: not a (modern) browser, so not CSRF.
        return False

    # Older browsers send Origin, but not Sec-Fetch-Site. This needs the Host
    # header to reach the app unchanged (as it does for url_for(_external=True)).
    try:
        origin_host = urlsplit(origin).netloc
    except ValueError:
        return True
    return origin_host.lower() != request.host.lower()


def check_csrf():
    """
    Reject the current request if it was made cross-origin by a browser.

    To be used as a Flask before_request handler.
    """
    if is_cross_origin_request():
        body = ('This request was rejected because it came from another site. '
                'Please use the forms and buttons on this site.')
        return render_template('error.html', heading='Forbidden', body=body), 403
