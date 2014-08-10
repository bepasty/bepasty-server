# note: keep this module rather slim, esp. do not import stuff
#       from other dependencies here, so we can import this from
#       everywhere where we just need the version number, project
#       name, etc. - even if the dependencies are not installed.

version = u"0.3.0"

# python package name, pypi package name,
# but: repo name is "bepasty-server"
project = u"bepasty"

description = u"a binary pastebin / file upload service"

__doc__ = u"%s - %s" % (project, description)

license = u"BSD 2-clause"
copyright_years = u"2013, 2014"

author = u"The Bepasty Team (see AUTHORS file)"
author_email = u""  # XXX TBD

maintainer = u"Thomas Waldmann"
maintainer_email = u"tw@waldmann-edv.de"
