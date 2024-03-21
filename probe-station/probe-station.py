# TODO create actual library

#import sys and use path insert to add lib files
import sys
from os.path import join, dirname, realpath
sys.path.insert(0, join(join(dirname(dirname(realpath(__file__))), "litho"), "scripts"))

from litho_gui_lib import *
from litho_img_lib import *

THUMBNAIL_SIZE: tuple[int,int] = (160,90)
CHIN_SIZE: int = 0
GUI: GUI_Controller = GUI_Controller(grid_size=(1,1),
                                     title = "Probe Station",
                                     add_window_size=(0,CHIN_SIZE),
                                     add_projector = False)

#region: Camera
camera_placeholder = rasterize(Image.new('RGB', (GUI.window_size[0],(GUI.window_size[0]*9)//16), (0,0,0)))
camera: Label = Label(
  GUI.root,
  image=camera_placeholder
  )
camera.grid(
  row = 0,
  column = 0,
  columnspan = GUI.grid_size[1],
  sticky='nesw')
GUI.add_widget("camera", camera)
#endregion

#region: Calibrate

last_coords: tuple[int,int] = (0,0)
def get_coords(event) -> tuple:
  global last_coords
  last_coords = (event.x, event.y)
  print(last_coords)
GUI.root.bind("<Button 1>",get_coords)
#endregion

GUI.mainloop()