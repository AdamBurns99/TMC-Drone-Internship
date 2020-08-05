import wx
import app_gui
from pyparrot.Bebop import Bebop
import math
import enum

class CmdType(enum.Enum):
    Direct="direct"
    Relative="relative"
    Sleep="sleep"
    TakeOff="takeoff"
    Land="land"
    Flip="flip"

class PyParrot(app_gui.MyFrame1):
    def __init__(self, parent):
        app_gui.MyFrame1.__init__(self, parent)
        self.statusBar.SetStatusWidths([100, -1])
        self.statusBar.SetStatusText('Not Connected')
        self.lc_commands.InsertColumn(0, 'command', width=300)

        self.bebop = Bebop()
        self.isConnected = False
        # TODO try to load JSON file from in this method
    
    def OnConnect( self, event ):
        self.isConnected = self.bebop.connect(10)
        statusText = 'Connected'
        if not self.isConnected:
            statusText = 'Not ' + statusText
        self.statusBar.SetStatusText(statusText)

    def OnDisconnect( self, event ):
        self.bebop.disconnect()
        self.isConnected = False
        self.statusBar.SetStatusText('Disconnected')
        self.statusBar.SetStatusText(f'Battery: {self.bebop.sensors.battery}%', 1)

    def OnTakeOff( self, event ):
        self.bebop.safe_takeoff(10)

        # By default, setting the status text only sets the first
        # one. So we must specify the second status text (index 1
        # , instead of index 0)
        self.statusBar.SetStatusText('Taking off', 1)

    def OnLand( self, event ):
        self.bebop.safe_land(10)
        self.statusBar.SetStatusText('Landing', 1)

    def OnAddTakeOff( self, event ):
        self._addCommand(f'{CmdType.TakeOff.value},10')

    def OnAddLand( self, event ):
        self._addCommand(f'{CmdType.Land.value},10')

    def OnAddRelative( self, event ):
        x = int(self.fld_x.GetValue())
        y = int(self.fld_y.GetValue())
        z = int(self.fld_z.GetValue())
        rads = int(self.fld_radians.GetValue())
        self._addCommand(f'{CmdType.Relative.value},{x},{y},{z},{rads}')

    def OnAddDirect( self, event ):
        roll = int(self.fld_roll.GetValue())
        pitch = int(self.fld_pitch.GetValue())
        yaw = int(self.fld_yaw.GetValue())
        vertical = int(self.fld_vertical.GetValue())
        duration = int(self.fld_duration.GetValue())
        self._addCommand(f'{CmdType.Direct.value},{roll},{pitch},{yaw},{vertical},{duration}')

    def OnAddSleep( self, event ):
        sleep = int(self.fld_sleep.GetValue())
        self._addCommand(f'{CmdType.Sleep.value},{sleep}')

    def OnAddFlip( self, event ):
        dir = str(self.fld_direction.GetValue())
        self._addCommand(f'{CmdType.Flip.value},{dir}')

    def OnAddFlyGrid(self, event):
        print('Not implemented yet') # TODO implement this method

    def OnRemove( self, event ):
        self.lc_commands.DeleteItem(self.lc_commands.GetFocusedItem())

    def OnUp( self, event ):
        """Swap the selected item with the one above it"""
        index = self.lc_commands.GetFocusedItem()
        if index >= 1:
            selItemStr = self.lc_commands.GetItemText(index)
            aboveItemStr = self.lc_commands.GetItemText(index-1)
            self.lc_commands.SetItemText(index, aboveItemStr)
            self.lc_commands.SetItemText(index-1, selItemStr)
            self.lc_commands.Focus(index-1)

    def OnDown( self, event ):
        """Swap the selected item with the one below it"""
        index = self.lc_commands.GetFocusedItem()
        if index < self.lc_commands.GetItemCount() - 1:
            selItemStr = self.lc_commands.GetItemText(index)
            belowItemStr = self.lc_commands.GetItemText(index+1)
            self.lc_commands.SetItemText(index, belowItemStr)
            self.lc_commands.SetItemText(index+1, selItemStr)
            self.lc_commands.Focus(index+1)

    def OnClear( self, event ):
        self.lc_commands.DeleteAllItems()

    def OnRunFromSelection( self, event ):
        print('Not implemented yet')
        event.Skip()

    def OnRunCommands( self, event ):
        """Go through each item in lc_commands and convert the string to 
        a list. Then use the first item in the list to determine the 
        command type, and the rest of the items are the params"""
        # TODO check if we are truly connected to the drone by using:
        # self.bebop.drone_connection.is_connected
        if not self.isConnected:
            return

        for i in range(self.lc_commands.GetItemCount()):
            args = self.lc_commands.GetItemText(i).split(',')
            self.statusBar.SetStatusText(f'Executing command: {args}', 1)

            if (args[0] == CmdType.Sleep.value):
                self.bebop.smart_sleep(int(args[1]))

            elif args[0] == CmdType.TakeOff.value:
                self.bebop.safe_takeoff(int(args[1]))

            elif args[0] == CmdType.Land.value:
                self.bebop.safe_land(int(args[1]))

            elif args[0] == CmdType.Direct.value:
                self.bebop.fly_direct(int(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5]))

            elif args[0] == CmdType.Relative.value:
                self.bebop.move_relative(int(args[1]), int(args[2]), int(args[3]), math.radians(int(args[4])))

            elif args[0] == CmdType.Flip.value:
                self.bebop.flip(str(args[1]))
    
    def _addCommand(self, cmd: str):
        self.lc_commands.InsertItem(self.lc_commands.GetItemCount(), cmd)
        self.statusBar.SetStatusText(f'Added command: {cmd}', 1)
# end of class
if __name__ == "__main__":
    try:
        application = wx.App(False) # create new application
        PyParrot(None).Show(True) # build and show our frame
        application.MainLoop() # run the application
    except Exception as e:
        print(e)