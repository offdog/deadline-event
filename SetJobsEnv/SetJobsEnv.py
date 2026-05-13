###############################################################
# Imports
###############################################################
from System import *

from Deadline.Events import *
from Deadline.Scripting import *

import os
import string
#########################################################################################
# This is the function called by Deadline to get an instance of the Draft event listener.
#########################################################################################


def GetDeadlineEventListener():
    return CustomEnvironmentCopyListener()


def CleanupDeadlineEventListener(eventListener):
    eventListener.Cleanup()

###############################################################
# The event listener class.
###############################################################


class CustomEnvironmentCopyListener (DeadlineEventListener):

    def __init__(self):
        self.OnJobSubmittedCallback += self.OnJobSubmitted

    def Cleanup(self):
        del self.OnJobSubmittedCallback

    def OnJobSubmitted(self, job):
        # List of environment keys you don't want passed.
        setenvkeys = self.GetConfigEntryWithDefault("EnvKeys", "")

        # Split out on ;
        setenvkeys = setenvkeys.split(';')

        addkeys = []

        self.LogInfo("On Job Submitted Event Plugin: Set Environment Started")
        self.LogInfo("Set Environment keys")

        for key in setenvkeys:
            addkeys.append(key)
            addkeys = key.split('=')
            self.LogInfo(str(addkeys[0])+"="+str(addkeys[1])+"\n")
            job.SetJobEnvironmentKeyValue(addkeys[0], addkeys[1])

        RepositoryUtils.SaveJob(job)

        self.LogInfo("On Job Submitted Event Plugin: Set Environment Finished")