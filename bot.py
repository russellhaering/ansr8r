#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.join(sys.path[0], 'twitty-twister', 'lib'))

from twisted.internet import reactor, protocol, defer, task
from twisted.python import log

import twitter
import settings

class TwitterBot:
    def __init__(self):
        print "Initializing..."
        self.feed = twitter.TwitterFeed(settings.USERNAME, settings.PASSWORD)
        print "Logged In"
        self.feed.show_user(settings.USERNAME).addCallback(self.onLogin).addErrback(lambda fail: fail.printTraceback())

    def onLogin(self, user):
        self.id = user.id
        self.feed.follow(self.onFollowEvent, user.id).addErrback(log.err)

    def onFollowEvent(self, entry):
        #print entry.text
        if entry.user.screen_name == settings.USERNAME:
            return
        else:
            reply = entry.text.replace('@' + settings.USERNAME, 'RT @' + entry.user.screen_name, 1)
            self.feed.update(reply).addErrback(lambda fail: fail.printTraceback())


if __name__ == "__main__":
    bot = TwitterBot()
    reactor.run()
