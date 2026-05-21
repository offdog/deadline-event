import os
import re

from Deadline.Events import *
from Deadline.Scripting import *


def GetDeadlineEventListener():
    return PPIstartupEvent()


def CleanupDeadlineEventListener(deadlinePlugin):
    deadlinePlugin.CleanUp()


class PPIstartupEvent(DeadlineEventListener):
    def __init__(self):
        self.OnJobSubmittedCallback += self.OnJobSubmitted

    def CleanUp(self):
        del self.OnJobSubmittedCallback

    def OnJobSubmitted(self, job):
        self.LogInfo("[PPIstartup] OnJobSubmitted - JobID: {} Name: '{}' Plugin: {}".format(
            job.JobId, job.JobName, job.JobPlugin))

        if job.JobPlugin not in ("MayaBatch", "MayaCmd"):
            self.LogInfo("[PPIstartup] Skip - Plugin '{}' is not MayaBatch or MayaCmd".format(job.JobPlugin))
            return

        prefix = self.GetConfigEntryWithDefault("JobNamePrefix", "JJK")
        if not job.JobName.startswith(prefix):
            self.LogInfo("[PPIstartup] Skip - Job name '{}' does not start with prefix '{}'".format(
                job.JobName, prefix))
            return

        # --- MAYA_SCRIPT_PATH ---
        melPath = self.GetConfigEntryWithDefault(
            "UserSetupMelPath", "M:/_tech/mayaScript/ppi/jjk/startup/userSetup.mel")
        melPath = melPath.replace("\\", "/")
        scriptDir = os.path.dirname(melPath)

        existingScriptPath = job.GetJobEnvironmentKeyValue("MAYA_SCRIPT_PATH")
        if existingScriptPath:
            newScriptPath = existingScriptPath + ";" + scriptDir
        else:
            newScriptPath = scriptDir

        job.SetJobEnvironmentKeyValue("MAYA_SCRIPT_PATH", newScriptPath)
        self.LogInfo("[PPIstartup] MAYA_SCRIPT_PATH - Added '{}'".format(scriptDir))

        # --- Output Path ---
        projectPath = job.GetJobPluginInfoKeyValue("ProjectPath").replace("\\", "/").rstrip("/")
        sceneFile = job.GetJobPluginInfoKeyValue("SceneFile")

        if not projectPath or not sceneFile:
            self.LogWarning("[PPIstartup] Skip output path - ProjectPath or SceneFile is empty")
        else:
            sceneName = os.path.splitext(os.path.basename(sceneFile.replace("\\", "/")))[0]
            baseRenderPath = "{}/render/{}".format(projectPath, sceneName)

            nextRev = 1
            if os.path.isdir(baseRenderPath):
                revDirs = [d for d in os.listdir(baseRenderPath)
                           if os.path.isdir(os.path.join(baseRenderPath, d))
                           and re.match(r'^rev\d{4}$', d)]
                if revDirs:
                    nextRev = max(int(d[3:]) for d in revDirs) + 1

            outputPath = "{}/rev{:04d}".format(baseRenderPath, nextRev)
            job.SetJobPluginInfoKeyValue("OutputFilePath", outputPath)
            self.LogInfo("[PPIstartup] OutputFilePath - Set to '{}'".format(outputPath))

        RepositoryUtils.SaveJob(job)
        self.LogInfo("[PPIstartup] SUCCESS - Job saved")
