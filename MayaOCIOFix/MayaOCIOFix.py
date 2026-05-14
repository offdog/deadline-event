from Deadline.Events import *
from Deadline.Scripting import *


def GetDeadlineEventListener():
    return MayaOCIOFixEvent()


def CleanupDeadlineEventListener(deadlinePlugin):
    deadlinePlugin.CleanUp()


class MayaOCIOFixEvent(DeadlineEventListener):
    def __init__(self):
        self.OnJobSubmittedCallback += self.OnJobSubmitted

    def CleanUp(self):
        del self.OnJobSubmittedCallback

    def OnJobSubmitted(self, job):
        self.LogInfo("[MayaOCIOFix] OnJobSubmitted triggered - JobID: {} Plugin: {}".format(job.JobId, job.JobPlugin))

        if job.JobPlugin not in ("MayaBatch", "MayaCmd"):
            self.LogInfo("[MayaOCIOFix] Skip - Plugin '{}' is not MayaBatch or MayaCmd".format(job.JobPlugin))
            return

        mayaVersion = self.GetConfigEntryWithDefault("MayaVersion", "2025")
        allowedVersions = [v.strip() for v in mayaVersion.split(",") if v.strip()]
        jobMayaVersion = job.GetJobPluginInfoKeyValue("Version")
        self.LogInfo("[MayaOCIOFix] Job Maya version: '{}', allowed: {}".format(jobMayaVersion, allowedVersions))

        if jobMayaVersion not in allowedVersions:
            self.LogInfo("[MayaOCIOFix] Skip - job version '{}' not in MayaVersion list".format(jobMayaVersion))
            return

        ocioConfigFile = job.GetJobPluginInfoKeyValue("OCIOConfigFile")
        self.LogInfo("[MayaOCIOFix] OCIOConfigFile: '{}'".format(ocioConfigFile))

        if not ocioConfigFile:
            self.LogInfo("[MayaOCIOFix] Skip OCIO patch - OCIOConfigFile is empty")
        elif "<MAYA_RESOURCES>" not in ocioConfigFile:
            self.LogInfo("[MayaOCIOFix] Skip OCIO patch - <MAYA_RESOURCES> not found, no replacement needed")
        else:
            mayaInstallBase = self.GetConfigEntryWithDefault(
                "MayaInstallBasePath", "C:/Program Files/Autodesk"
            )
            mayaResourcesPath = "{}/Maya{}/resources".format(mayaInstallBase, jobMayaVersion)
            self.LogInfo("[MayaOCIOFix] Replacing <MAYA_RESOURCES> with '{}'".format(mayaResourcesPath))

            newOCIOConfigFile = ocioConfigFile.replace("<MAYA_RESOURCES>", mayaResourcesPath)
            job.SetJobPluginInfoKeyValue("OCIOConfigFile", newOCIOConfigFile)
            RepositoryUtils.SaveJob(job)
            self.LogInfo("[MayaOCIOFix] SUCCESS - OCIOConfigFile updated: {} -> {}".format(ocioConfigFile, newOCIOConfigFile))

        abortOnError = self.GetConfigEntryWithDefault("AbortOnError", "Unchanged")
        self.LogInfo("[MayaOCIOFix] AbortOnError config: {}".format(abortOnError))

        if abortOnError != "Unchanged":
            value = "1" if abortOnError == "Enable" else "0"
            melCmd = 'setAttr "defaultArnoldRenderOptions.abortOnError" {};'.format(value)

            preRenderMel = job.GetJobPluginInfoKeyValue("PreRenderMel")
            if preRenderMel:
                preRenderMel = preRenderMel + " " + melCmd
            else:
                preRenderMel = melCmd

            job.SetJobPluginInfoKeyValue("PreRenderMel", preRenderMel)
            RepositoryUtils.SaveJob(job)
            self.LogInfo("[MayaOCIOFix] AbortOnError set to {} via PreRenderMel".format(value))
