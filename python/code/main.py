import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file - handles both development and PyInstaller bundled execution
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    bundle_dir = sys._MEIPASS
else:
    # Running in development
    bundle_dir = Path(__file__).parent.parent

env_path = os.path.join(bundle_dir, '.env')
load_dotenv(env_path)

from gui.gui_main import IracingDataGUI
import tkinter as tk
from irsdk import IRSDK

if __name__=="__main__":
    root = tk.Tk()
    gui = IracingDataGUI(root)
    root.mainloop()



    
#     # from time import sleep
#     # while True:
#     #     irsdk_instance = IRSDK()
#     #     a = None
#         # # a = r"python/newdataset/data100.bin"
#         # irsdk_instance.startup(a)
#         # print(irsdk_instance['Lap'], irsdk_instance['LapLastLapTime'])
#         # sleep(0.25)
#     # print(irsdk_instance["IsOnTrack"], irsdk_instance["IsOnTrackCar"])
#     # print(irsdk_instance["PlayerCarTowTime"], irsdk_instance["FastRepairAvailable"])

#     # 'EventType': 'Practice'
#     # 'SeriesID': 591, 'SeasonID': 5932, 'SessionID': 295641631, 'SubSessionID': 82194959

#     # irsdk_instance["SessionInfo"]["SessionName"] - QUALIFY


#     # ir["SessionInfo"]["SessionType"] / ir["SessionInfo"]["SessionName"] - typ sesji
#     # ir["IsOnTrack"] - czy w aucie?
#     # ir["PlayerCarTowTime"] - car is being towed if >0
#     # ir["FastRepairAvailable"]
