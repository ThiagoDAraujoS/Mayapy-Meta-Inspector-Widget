import sys
import importlib
import importlib.util
from importlib.abc import MetaPathFinder
import os
import maya.api.OpenMaya as om
from maya import cmds


def maya_useNewAPI():
    """ This is a special method, used by maya, it let maya knows I am using the maya.api 2.0 """
    pass


class MetaWindowCmd(om.MPxCommand):
    """ This is my plugin's main body class """

    kPluginCmdName = "metaWindow"
    """ This is my command's name, once this plugin is loaded I will be able to do cmds.metaWindow() """

    def __init__(self):
        super(MetaWindowCmd, self).__init__()

    def doIt(*args, **kwargs):
        """ This is the function that is run once cmds.metaWindow() is called """
        print("Dont use this command directly")

    @staticmethod
    def creator():
        """ This method creates the plugin """
        return MetaWindowCmd()


class MetaWindowModuleFinder(MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        """ find_spec concrete implementation, it tries to reload modules found if they are already loaded if not try to use maya's cmds.pluginInfo to scope for new modules"""
        plugin_path = os.path.dirname(cmds.pluginInfo("MetaWindow", query=True, path=True))    # <- Find the plugin's folder path using maya's cmds.pluginInfo
        location = os.path.normpath(f"{plugin_path}/MetaWindow/scripts/{fullname}.py")         # <- Find the module's path

        if not os.path.exists(location):     # <- If the path doesn't exist
            return None                      # <- return nothing since there's nothing to be imported here

        spec = importlib.util.spec_from_file_location(fullname, location)  # <- if the path exists, build a spec object from the module name and file path
        return spec                                                        # <- return the spec so the module builder will be able to build the module


finder = MetaWindowModuleFinder()
""" Reference to the finder object """


def initializePlugin(plugin):
    """ This method is used by maya when the plugin is registered, it automatically fires on plugin load """
    vendor = "Thiago de Araujo Silva"
    version = "1.0.0"

    pluginFn = om.MFnPlugin(plugin, vendor, version)    # <- Create a plugin object

    try:
        pluginFn.registerCommand(MetaWindowCmd.kPluginCmdName, MetaWindowCmd.creator)  # <- Try to register the plugin

        global finder
        if finder not in sys.meta_path:     # If this finder is not present in the sys.meta_path list
            sys.meta_path.append(finder)    # Include it there, so maya can now use MetaWindowCmd as a module finder too
    except:
        om.MGlobal.displayError("Failed to register command: {0}".format(MetaWindowCmd.kPluginCmdName))


def uninitializePlugin(plugin):
    """ This method is used by maya when the plugin is deregistered, it automatically fires on plugin unload """
    pluginFn = om.MFnPlugin(plugin)

    try:
        pluginFn.deregisterCommand(MetaWindowCmd.kPluginCmdName)

        global finder
        if finder in sys.meta_path:         # If this finder is present in the sys.meta_path list
            sys.meta_path.remove(finder)    # Remove it from there, so maya will stop recognizing MetaWindowCmd as a module finder
    except:
        om.MGlobal.displayError("Failed to unregister command: {0}".format(MetaWindowCmd.kPluginCmdName))
