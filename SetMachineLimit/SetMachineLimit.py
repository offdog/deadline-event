from System import *

from Deadline.Events import *
from Deadline.Scripting import *
from Deadline.Scripting import RepositoryUtils

import os
import string


def GetDeadlineEventListener():
    return CustomEnvironmentCopyListener()

def CleanupDeadlineEventListener(eventListener):
    eventListener.Cleanup()

class CustomEnvironmentCopyListener (DeadlineEventListener):

    def __init__(self):
        self.OnJobSubmittedCallback += self.OnJobSubmitted
        self.OnJobStartedCallback += self.OnJobStarted
        self.OnJobResumedCallback += self.OnJobResumed
        self.OnJobRequeuedCallback += self.OnJobRequeued

    def Cleanup(self):
        del self.OnJobSubmittedCallback
        del self.OnJobStartedCallback
        del self.OnJobResumedCallback
        del self.OnJobRequeuedCallback

    def ApplyMachineLimit(self, job):
        try:
            # Read configurable values from .param
            active_threshold = self.GetConfigEntryWithDefault("ActiveJobThreshold", "10")
            priority_threshold = self.GetConfigEntryWithDefault("JobPriorityThreshold", "50")
            machine_limit_high = self.GetConfigEntryWithDefault("MachineLimitMaximumHigh", "35")

            active_threshold = int(active_threshold)
            priority_threshold = int(priority_threshold)
            machine_limit_high = int(machine_limit_high)

            active = RepositoryUtils.GetJobsInState("Active")
            active_count = len(active)

            self.LogInfo(
                "Job Stats -> active: {} | ActiveThreshold: {} | PriorityThreshold: {} | MachineLimitHigh: {}".format(
                    active_count, active_threshold, priority_threshold, machine_limit_high
                )
            )

            if active_count > active_threshold:
                if job.JobPriority > priority_threshold:
                    RepositoryUtils.SetMachineLimitMaximum(job.JobId, machine_limit_high)
                    self.LogInfo("High priority job ({}): Set MachineLimitMaximum to {}".format(job.JobPriority, machine_limit_high))
                elif job.JobPriority <= priority_threshold:
                    RepositoryUtils.SetMachineLimitMaximum(job.JobId, 0)
                    self.LogInfo("Low priority job ({}): Set MachineLimitMaximum to 0".format(job.JobPriority))
            else:
                RepositoryUtils.SetMachineLimitMaximum(job.JobId, 0)
                self.LogInfo("Default priority job ({}): Set MachineLimitMaximum to 0".format(job.JobPriority))

        except Exception as e:
            self.LogWarning("Error counting jobs: {}".format(str(e)))

        self.LogInfo("Check")

    def OnJobSubmitted(self, job):
        self.LogInfo("OnJobSubmitted triggered for job: {}".format(job.JobId))
        self.ApplyMachineLimit(job)

    def OnJobStarted(self, job):
        self.LogInfo("OnJobStarted triggered for job: {}".format(job.JobId))
        self.ApplyMachineLimit(job)

    def OnJobResumed(self, job):
        self.LogInfo("OnJobResumed triggered for job: {}".format(job.JobId))
        self.ApplyMachineLimit(job)

    def OnJobRequeued(self, job):
        self.LogInfo("OnJobRequeued triggered for job: {}".format(job.JobId))
        self.ApplyMachineLimit(job)