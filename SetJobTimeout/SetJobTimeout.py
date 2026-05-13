###############################################################
# Imports
###############################################################
from Deadline.Events import *
from Deadline.Scripting import *


def GetDeadlineEventListener():
    return SetJobTimeout()


def CleanupDeadlineEventListener(eventListener):
    eventListener.Cleanup()


###############################################################
# The event listener class.
###############################################################
class SetJobTimeout(DeadlineEventListener):
    def __init__(self):
        self.OnJobSubmittedCallback += self.OnJobSubmitted

    def Cleanup(self):
        del self.OnJobSubmittedCallback

    def OnJobSubmitted(self, job):
        software = job.PluginName

        # Read allowed software list from config (comma-separated)
        allowed_raw = self.GetConfigEntryWithDefault("AllowedSoftware", "MayaBatch,MayaCmd,CommandLine")
        allowSoftware = [s.strip() for s in allowed_raw.split(",") if s.strip()]

        self.LogInfo("Software : " + software)
        self.LogInfo("Allowed Software : " + ", ".join(allowSoftware))

        if software in allowSoftware:
            # Maximum timeout (hours + minutes + seconds)
            max_hours   = self.GetIntegerConfigEntryWithDefault("MaxHour",   0)
            max_minutes = self.GetIntegerConfigEntryWithDefault("MaxMinute", 0)
            max_seconds = self.GetIntegerConfigEntryWithDefault("MaxSecond", 0)
            max_total_seconds = (max_hours * 3600) + (max_minutes * 60) + max_seconds

            # Minimum timeout (hours + minutes + seconds)
            min_hours   = self.GetIntegerConfigEntryWithDefault("MinHour",   0)
            min_minutes = self.GetIntegerConfigEntryWithDefault("MinMinute", 0)
            min_seconds = self.GetIntegerConfigEntryWithDefault("MinSecond", 5)
            min_total_seconds = (min_hours * 3600) + (min_minutes * 60) + min_seconds

            do_task = self.GetConfigEntryWithDefault("DoTask", "")

            self.LogInfo(
                "Setting Maximum Timeout: {0}h {1}m {2}s ({3} seconds total)".format(
                    max_hours, max_minutes, max_seconds, max_total_seconds
                )
            )
            self.LogInfo(
                "Setting Minimum Timeout: {0}h {1}m {2}s ({3} seconds total)".format(
                    min_hours, min_minutes, min_seconds, min_total_seconds
                )
            )
            self.LogInfo("On Task Timeout : " + do_task)

            job.JobTaskTimeoutSeconds = max_total_seconds
            job.JobMinRenderTimeSeconds = min_total_seconds
            job.JobOnTaskTimeout = do_task

            RepositoryUtils.SaveJob(job)
        else:
            self.LogInfo("No Set Timeout")
