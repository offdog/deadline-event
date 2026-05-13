from Deadline.Events import *
from Deadline.Scripting import *


def GetDeadlineEventListener():
    return UsersSuspendJobEventListener()


def CleanupDeadlineEventListener(eventListener):
    eventListener.Cleanup()


class UsersSuspendJobEventListener(DeadlineEventListener):
    def __init__(self):
        self.OnJobSubmittedCallback += self.OnJobSubmitted

    def Cleanup(self):
        del self.OnJobSubmittedCallback

    def OnJobSubmitted(self, job):
        suspend_users_str = self.GetConfigEntryWithDefault("SuspendUsers", "dvisual")
        suspend_users = [u.strip().lower() for u in suspend_users_str.split(",") if u.strip()]

        job_user = job.JobUserName.lower()

        if job_user in suspend_users:
            self.LogInfo(
                "UsersSuspendJob: Suspending job '%s' (ID: %s) submitted by '%s'"
                % (job.JobName, job.JobId, job.JobUserName)
            )
            RepositoryUtils.SuspendJob(job)
        else:
            self.LogInfo(
                "UsersSuspendJob: Job '%s' by '%s' not in suspend list, skipping."
                % (job.JobName, job.JobUserName)
            )
