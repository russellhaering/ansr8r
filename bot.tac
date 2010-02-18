#!/usr/bin/env python
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
sys.path.append(os.path.join(HERE, 'twitty-twister', 'lib'))

import bot
from twisted.application import service

ansr8r = bot.TwitterBot()

application = service.Application('ansr8r')
