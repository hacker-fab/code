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
GUI: GUI_Controller = GUI_Controller(grid_size=(2,2),
                                     title = "Probe Station",
                                     add_window_size=(0,CHIN_SIZE),
                                     add_projector = False,
                                     )
debug: Debug = Debug(root=GUI.root)
GUI.add_widget("debug", debug)

#region: Camera
img_size = (GUI.window_size[0],(GUI.window_size[0]*9)//16)
camera_placeholder = rasterize(Image.new('RGB', img_size, (0,0,0)))
camera: Label = Label(
  GUI.root,
  image=camera_placeholder
  )
camera.grid(
  row = 0,
  column = 0,
  columnspan = 2,
  sticky='nesw')
GUI.add_widget("camera", camera)
#endregion

#region: get coords button
coords_button: Button = Button(
  GUI.root,
  text="get coords",
  command=lambda: print(GUI.get_coords("camera", img_size))
  )
coords_button.grid(
  row = 1,
  column = 0,
  sticky='nesw')
GUI.add_widget("button", coords_button)
#endregion

#region: show image ontop button
#offset calibration (different for each monitor)
monitor_offset: int = (3,25)
def show_image(size: tuple[int,int] = (3,3),
               color: tuple[int,int,int] = (255,0,0),
               location: tuple[int,int] = (0,0)) -> Tk:
  #alert=canvas.create_image(100,200,image=alert_panel,anchor=NW)
  test_img = rasterize(Image.new('RGB', size, color))
  top = Toplevel(GUI.root)
  # top.withdraw()
  top.overrideredirect(True) # make border-less window
  top.attributes('-topmost', True)
  # make it like a transparent window
  trans_color = '#ffffff'  # select a color not used by the alert image
  top.attributes('-transparentcolor', trans_color)
  # show the alert image
  alert = Label(top, image=test_img, bg=trans_color)
  alert.image = test_img
  alert.pack()
  # put the popup at the center of root window
  top.update()
  root_xy = (GUI.root.winfo_x(), GUI.root.winfo_y())
  # rw, rh = GUI.root.winfo_width(), GUI.root.winfo_height()
  # tw, th = top.winfo_width(), top.winfo_height()
  coords = add(add(add(location, root_xy), round_tuple(div(size,2))),monitor_offset)
  top.geometry(f"+{coords[0]}+{coords[1]}")
  return top

last_image: Tk = None
def show_click():
  GUI.root.update()
  global last_image
  if(last_image != None):
    last_image.destroy()
  last_image = show_image(location=GUI.get_coords(in_pixels=True))

image_button: Button = Button(
  GUI.root,
  text="show image",
  command=lambda: show_click()
  )
image_button.grid(
  row = 1,
  column = 1,
  sticky='nesw'
)



#endregion

#region: bind a stage
# stage: Stage_Controller = Stage_Controller(debug=debug, 
#   location_query = lambda: GUI.get_coords("camera", img_size))
# stage.calibrate((10,10), calibrate_backlash = 'None')

#endregion


GUI.mainloop()