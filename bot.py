#!/usr/bin/env python
import sys, os, glob, cPickle

from twisted.internet import reactor, protocol, defer, task
from twisted.python import log

import aiml
import twitter
import settings


class TwitterBot:
    def __init__(self):
        self.status = {}
        print "Initializing AIML Bot..."
        self.k = aiml.Kernel()
        print "Loading Brain..."
        if os.path.isfile(settings.BRAINFILE):
            self.k.loadBrain(settings.BRAINFILE)
        else:
            self._loadBrainFromAIML()
        print "Loading Sessions..."
        self._loadSessions()
        print "Loading Previous Status Data..."
        self._loadBotStatusData()
        reactor.addSystemEventTrigger('before', 'shutdown', self._onShutDown)
        print "Connecting to Twitter..."
        self.feed = twitter.TwitterFeed(settings.USERNAME, settings.PASSWORD)
        print "Fetching Account Data..."
        self.feed.show_user(settings.USERNAME).addCallback(self.onLogin).addErrback(lambda fail: fail.printTraceback())

    def _onShutDown(self):
        self.k.saveBrain(settings.BRAINFILE)
        print "Brain Saved"
        sessionFile = open(settings.SESSNFILE, 'w')
        cPickle.dump(self.k.getSessionData(), sessionFile)
        sessionFile.close()
        print "Sessions Saved"
        self._saveBotStatusData()


    def _loadBrainFromAIML(self):
        for file in glob.glob(os.path.join('standard', '*.aiml')):
            self.k.learn(file)

    def _loadSessions(self):
        if os.path.isfile(settings.SESSNFILE):
            sessionfile = open(settings.SESSNFILE, 'r')
            sessions = cPickle.load(sessionfile)
            for user, data in sessions.items():
                for pred, value in data.items():
                    self.k.setPredicate(pred, value, user)

    def _saveBotStatusData(self):
        statusFile = open(settings.STATUSFILE, 'w')
        cPickle.dump(self.status, statusFile)

    def _loadBotStatusData(self):
        if os.path.isfile(settings.STATUSFILE):
            statusFile = open(settings.STATUSFILE, 'r')
            self.status = cPickle.load(statusFile)

    def onFollowStreamClose(self, result):
        """Called when the follow stream connection is lost, reopens the
            connection recursively"""
        self.feed.follow(self.onMention, self.id).addCallback(self.onFollowStreamClose).addErrback(log.err)

    def onLogin(self, user):
        self.id = user.id
        # Deal with (latest 20) Mentions Since Shutdown
        try:
            self.feed.mentions(self.onMention, params={'since_id': unicode(self.status['lastMentionRepliedTo'])}) 
        except KeyError:
            print "No previous post data available, skipping"
            pass
        # Begin Following Self
        self.feed.follow(self.onMention, user.id).addCallback(self.onFollowStreamClose).addErrback(log.err)

    def onMention(self, entry):
        if entry.user.screen_name == settings.USERNAME:
            return
        else:
            input = entry.text.replace('@' + settings.USERNAME, '', 1)
            reply = '@%s %s' % (entry.user.screen_name, self.k.respond(input, entry.user.screen_name))
            print "Responding to", entry.id, ":", input, "with:", reply
            self.feed.update(reply, in_reply_to=entry.id).addErrback(lambda fail: fail.printTraceback())
            self.status['lastMentionRepliedTo'] = entry.id
