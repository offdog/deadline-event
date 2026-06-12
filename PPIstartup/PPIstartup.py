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

    def _build_output_path(self, job):
        rawProjectPath = job.GetJobPluginInfoKeyValue("ProjectPath")
        projectPath = rawProjectPath.replace("\\", "/").rstrip("/") if rawProjectPath else ""
        sceneFile = job.GetJobPluginInfoKeyValue("SceneFile")

        if not projectPath or not sceneFile:
            self.LogWarning("[PPIstartup] Skip output path - ProjectPath or SceneFile is empty")
            return None

        sceneName = os.path.splitext(os.path.basename(sceneFile.replace("\\", "/")))[0]
        baseRenderPath = "{}/render/{}".format(projectPath, sceneName)

        nextRev = 1
        if os.path.isdir(baseRenderPath):
            revDirs = [d for d in os.listdir(baseRenderPath)
                       if os.path.isdir(os.path.join(baseRenderPath, d))
                       and re.match(r'^rev\d{4}$', d)]
            if revDirs:
                nextRev = max(int(d[3:]) for d in revDirs) + 1

        return "{}/rev{:04d}".format(baseRenderPath, nextRev)

    def _project_code_matches_job(self, job, projectCode):
        if not projectCode:
            return False

        if job.JobName.startswith(projectCode):
            return True

        rawProjectPath = job.GetJobPluginInfoKeyValue("ProjectPath")
        projectPath = rawProjectPath.replace("\\", "/").strip("/") if rawProjectPath else ""
        return "/{}/".format(projectCode) in "/{}/".format(projectPath)

    def _find_project_config(self, job, ppiProject):
        for i in range(1, 4):
            projectCode = self.GetConfigEntryWithDefault("Prefix{}".format(i), "").strip()
            if not projectCode:
                continue

            if ppiProject:
                if ppiProject != projectCode:
                    continue
            elif not self._project_code_matches_job(job, projectCode):
                continue

            melPath = self.GetConfigEntryWithDefault("MelPath{}".format(i), "").strip()
            return projectCode, melPath, i

        return None, None, None

    def OnJobSubmitted(self, job):
        self.LogInfo("[PPIstartup] OnJobSubmitted - JobID: {} Name: '{}' Plugin: {}".format(
            job.JobId, job.JobName, job.JobPlugin))

        if job.JobPlugin not in ("MayaBatch", "MayaCmd"):
            self.LogInfo("[PPIstartup] Skip - Plugin '{}' is not MayaBatch or MayaCmd".format(job.JobPlugin))
            return

        # --- Find matching PPI project & MEL path ---
        pipeline = (job.GetJobExtraInfoKeyValue("Pipeline") or "").strip().lower()
        ppiProject = (job.GetJobExtraInfoKeyValue("PPIProject") or "").strip()

        if pipeline == "ppi" and not ppiProject:
            self.LogWarning("[PPIstartup] Pipeline is ppi but PPIProject extra info is empty; using fallback detection")
        elif pipeline != "ppi":
            self.LogInfo("[PPIstartup] Pipeline extra info is '{}'; using fallback detection".format(pipeline))
            ppiProject = ""

        projectCode, matchedMelPath, entryIndex = self._find_project_config(job, ppiProject)
        if matchedMelPath is None:
            if ppiProject:
                self.LogWarning("[PPIstartup] Skip - PPIProject '{}' does not match any configured project code".format(
                    ppiProject))
            else:
                self.LogInfo("[PPIstartup] Skip - No extra info or fallback project match for job '{}'".format(
                    job.JobName))
            return

        self.LogInfo("[PPIstartup] Matched PPI project '{}' (entry {})".format(projectCode, entryIndex))

        # --- MAYA_SCRIPT_PATH ---
        melPath = matchedMelPath.replace("\\", "/")
        scriptDir = os.path.dirname(melPath)

        existingScriptPath = job.GetJobEnvironmentKeyValue("MAYA_SCRIPT_PATH")
        if existingScriptPath:
            newScriptPath = existingScriptPath + ";" + scriptDir
        else:
            newScriptPath = scriptDir

        job.SetJobEnvironmentKeyValue("MAYA_SCRIPT_PATH", newScriptPath)
        self.LogInfo("[PPIstartup] MAYA_SCRIPT_PATH - Added '{}'".format(scriptDir))

        # --- Output Path ---
        outputPath = self._build_output_path(job)
        if outputPath:
            job.SetJobPluginInfoKeyValue("OutputFilePath", outputPath)
            self.LogInfo("[PPIstartup] OutputFilePath - Set to '{}'".format(outputPath))

        RepositoryUtils.SaveJob(job)
        self.LogInfo("[PPIstartup] SUCCESS - Job saved")
