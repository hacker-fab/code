from tkinter import *
#import sys and use path insert to add lib files
import sys
from os.path import join, dirname, realpath
sys.path.insert(0, join(dirname(dirname(realpath(__file__))), "lib"))
from gui_lib import *
from img_lib import *
from backend_lib import *

THUMBNAIL_SIZE: tuple[int,int] = (160,90)
CHIN_SIZE: int = 100
GUI: GUI_Controller = GUI_Controller(grid_size=(2,1),
                                     title = "Probe Station",
                                     add_window_size=(0,CHIN_SIZE),
                                     add_projector = False,
                                     )
debug: Debug = Debug(root=GUI.root)
GUI.add_widget("debug", debug)

#region: Camera
grid_cell = (0,0)
img_size = (GUI.window_size[0],(GUI.window_size[0]*9)//16)
camera_placeholder = rasterize(Image.new('RGB', img_size, (0,0,0)))
camera: Label = Label(
  GUI.root,
  image=camera_placeholder
  )
camera.grid(
  row = grid_cell[0],
  column = grid_cell[1],
  columnspan = GUI.grid_size[1],
  sticky='nesw')
GUI.root.grid_rowconfigure(grid_cell[0], weight=1, minsize=img_size[1])
GUI.add_widget("camera", camera)
#endregion

#region: button
button: Button = Button(
  GUI.root,
  text="get coords",
  command=lambda: print(GUI.get_coords("camera", img_size))
  )
button.grid(
  row = 1,
  column = 0,
  columnspan = GUI.grid_size[1],
  sticky='nesw')
GUI.add_widget("button", button)
#endregion

#region: Calibrate
# last_coords: tuple[int,int] = (0,0)
# def get_coords(event) -> tuple:
#   global last_coords
#   last_coords = (event.x, event.y)
#   print(last_coords)
# GUI.root.bind("<Button 1>",get_coords)
#endregion

GUI.mainloop()