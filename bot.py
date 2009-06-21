#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.join(sys.path[0], 'twitty-twister', 'lib'))

from twisted.internet import reactor, protocol, defer, task
from twisted.python import log

import twitter
import settings

def onLogin(user, feed):
    feed.follow(onFollowEvent, user.id).addErrback(log.err)

def onFollowEvent(entry):
    print entry.text

feed = twitter.TwitterFeed(settings.USERNAME, settings.PASSWORD)
feed.show_user(settings.USERNAME).addCallback(onLogin, feed)

reactor.run()
