###############################################################
## Imports
###############################################################
from __future__ import absolute_import
import os
import subprocess

from Deadline.Events import DeadlineEventListener
from Deadline.Scripting import PathUtils, RepositoryUtils

###############################################################
## Give Deadline an instance of this class so it can use it.
###############################################################
def GetDeadlineEventListener():
    return NukeTmpFilesCleanUpListener()

def CleanupDeadlineEventListener( eventListener ):
    eventListener.Cleanup()

###############################################################
## The NukeTmpFilesCleanUpListener event listener class.
###############################################################
class NukeTmpFilesCleanUpListener ( DeadlineEventListener ):
    def __init__( self ):
        self.OnJobFinishedCallback += self.OnJobFinished
        #self.OnJobStartedCallback += self.OnJobStarted
        self.OnSlaveStartingJobCallback += self.OnSlaveStartingJob  # fix OnJobStarted not work

    def Cleanup( self ):
        del self.OnJobFinishedCallback
        #del self.OnJobStartedCallback
        del self.OnSlaveStartingJobCallback                         # fix OnJobStarted not work

    '''
    def OnJobStarted( self, job ):
        eventType = self.GetConfigEntryWithDefault( "CleanTmpFilesEvent", "On Job Started" )

        if 'Nuke' in job.PluginName and ( eventType == "On Job Started" or eventType == "On Job Started and On Job Finished" ):
            self.LogInfo( "[ER] - Job started, cleaning up Temp files" )
            self.RemoveFiles( job )
    '''

    # fix OnJobStarted not work
    def OnSlaveStartingJob(self, slaveName, job):
        eventType = self.GetConfigEntryWithDefault( "CleanTmpFilesEvent", "On Job Started" )

        if 'Nuke' in job.PluginName and ( eventType == "On Job Started" or eventType == "On Job Started and On Job Finished" ):
            self.LogInfo( "[ER] - Job started, cleaning up Temp files" )
            self.RemoveFiles( job )
    #------------------------------------------------------------------------------------

    def OnJobFinished( self, job ):
        eventType = self.GetConfigEntryWithDefault( "CleanTmpFilesEvent", "On Job Finished" )

        if 'Nuke' in job.PluginName and ( eventType == "On Job Finished" or eventType == "On Job Started and On Job Finished" ):
            self.LogInfo( "[ER] - Job finished, cleaning up Temp files" )
            self.RemoveFiles( job )
    
    def RemoveFiles( self, job ):
        self.LogInfo( "[ER] - Cleaning up of *.tmp files started" )

        removed = 0
        total_files = 0

        for d in job.JobOutputDirectories:
            d = RepositoryUtils.CheckPathMapping( d, False )
            d = PathUtils.ToPlatformIndependentPath( d )

            self.LogInfo("[ER] - Cleaning %s" % d)

            try:
                for f in os.listdir(os.path.realpath( d )):
                    total_files += 1
                    if os.path.splitext( f )[-1] == ".tmp":
                        try:
                            tmpfile = os.path.join( d, f )
                            os.remove( tmpfile )
                            removed += 1
                        except OSError:
                            self.LogWarning( "[ER] - Can't delete: %s" % tmpfile )
            except FileNotFoundError:
                print(f"The path {d} does not exist.")
            except subprocess.CalledProcessError as e:
                print(f"Error occurred: {e}")

        self.LogInfo( "[ER] - Total files %s - Temp files removed: %s" % ( total_files, removed ) )
        self.LogInfo( "[ER] - Cleaning up of *.tmp files finished" )
