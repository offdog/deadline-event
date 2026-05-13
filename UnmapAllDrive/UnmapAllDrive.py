from Deadline.Events import DeadlineEventListener
from Deadline.Scripting import SystemUtils

import subprocess
import os


def GetDeadlineEventListener():
    return EventAction()

def CleanupDeadlineEventListener( deadlinePlugin ):
    deadlinePlugin.Cleanup()

class EventAction (DeadlineEventListener):
    def __init__( self ):
        self.OnSlaveIdleCallback += self.UnmapAll
        self.OnSlaveStoppedCallback += self.UnmapAll
        self.OnSlaveStalledCallback += self.UnmapAll
        self.OnMachineRestartCallback += self.UnmapAll

    def Cleanup ( self ):
        del self.OnSlaveIdleCallback
        del self.OnSlaveStoppedCallback
        del self.OnSlaveStalledCallback
        del self.OnMachineRestartCallback

    def UnmapAll(self, *args):
        username = os.getlogin()
        self.LogInfo("User ::: " + username)

        user_filter = self.GetConfigEntry("UserFilter").strip()

        # ===== Logic =====
        if user_filter == "":
            self.LogInfo("UserFilter empty → skip unmap")
            return

        if user_filter != "*":
            allowed_users = [u.strip() for u in user_filter.split(",") if u.strip()]
            if username not in allowed_users:
                self.LogInfo("User not in filter list → skip")
                return

        try:
            result = subprocess.run(['net', 'use'], capture_output=True, text=True)
            mapped_drives = []

            for line in result.stdout.splitlines():
                if line.startswith('OK'):
                    parts = line.split()
                    if len(parts) > 1:
                        mapped_drives.append(parts[1])

            if not mapped_drives:
                self.LogInfo("No mapped drives found")
                return

            result = subprocess.run(['net', 'use', '/del', '/y', '*'], capture_output=True, text=True)

            if result.returncode == 0:
                self.LogInfo(f"Successfully unmapped all network drives: {result.stdout}")
            else:
                self.LogInfo(f"Failed to unmap network drives: {result.stdout}")

        except Exception as e:
            self.LogInfo(f"Exception occurred while unmapping drives: {e}")
