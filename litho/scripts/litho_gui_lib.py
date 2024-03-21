from __future__ import annotations
from tkinter import Tk, Button, Toplevel, Entry, IntVar, DoubleVar, Variable, filedialog, Label, Widget
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
from time import time
from os.path import basename
from litho_img_lib import *
from typing import Callable, Literal, Union


# widget to display info, errors, warning, and text
class Debug():
  __widget__: Label
  __enabled__: bool
  text_color: tuple[str, str]
  warn_color: tuple[str, str]
  err_color:  tuple[str, str]
  
  # create new widget
  def __init__(self, root: Tk,
               text_color: tuple[str, str] = ("black", "white"),
               warn_color: tuple[str, str] = ("black", "orange"),
               err_color:  tuple[str, str] = ("white", "red")):
    self.__enabled__ = True
    self.text_color = text_color
    self.warn_color = warn_color
    self.err_color = err_color
    self.__widget__ = Label(
      root,
      justify = "left",
      anchor = "w"
    )
    self.__set_color__(text_color)
  
  # show text in the debug widget
  def info(self, text:str):
    if(not self.__enabled__):
      return
    self.__widget__.config(text = text)
    self.__set_color__(self.text_color)
    print("i "+text)
  
  # show warning in the debug widget
  def warn(self, text:str):
    if(not self.__enabled__):
      return
    self.__widget__.config(text = text)
    self.__set_color__(self.warn_color)
    print("w "+text)
    
  # show error in the debug widget
  def error(self, text:str):
    if(not self.__enabled__):
      return
    self.__widget__.config(text = text)
    self.__set_color__(self.err_color)
    print("e "+text)
  
  # enable prints
  def enable(self):
    self.__enabled__ = True
    
  # disable prints
  def disable(self):
    self.__enabled__ = False
  
  # place widget on the grid
  def grid(self, row: int | None = None, col: int | None = None, colspan: int = 1, rowspan: int = 1):
    if(row == None or col == None):
      self.__widget__.grid()
    else:
      self.__widget__.grid(row = row,
                       column = col,
                       rowspan = rowspan,
                       columnspan = colspan,
                       sticky = "nesw")
  
  # remove widget from the grid
  def grid_remove(self):
    self.__widget__.grid_remove()
  
  # set the text and background color
  def __set_color__(self, colors: tuple[str,str]):
    self.__widget__.config(fg = colors[0],
                       bg = colors[1])

# creates a button that cycles through states
# each state contains: text, colors, and entering / exiting functions
class Cycle():
  # global counter to ensure unique names
  __total_cycles__: int = 0
  # mandatory / main fields
  __widget__: Button
  __gui__: GUI_Controller
  state: int
  # user-inputted fields
  # tuple structure: (text, (fg, bg), (enter, exit))
  cycle_state_t = tuple[str, tuple[str,str], tuple[Callable | None, Callable | None]]
  __states__: list[cycle_state_t]
  func_always: Callable | None
  
  # create new Cycle widget
  def __init__( self, gui: GUI_Controller,
          name: str | None = None,
          func_always: Callable | None = None):
    self.__gui__ = gui
    self.func_always = func_always
    self.state = 0
    self.__states__ = []
    self.__widget__ = Button(gui.root, command=self.cycle)
    if(name == None):
      gui.add_widget("unnamed cycle widget "+str(Cycle.__total_cycles__), self)
      Cycle.__total_cycles__ += 1
    else:
      gui.add_widget(name, self)
    
  # place widget on the grid
  def grid(self, row: int | None = None, col: int | None = None, colspan: int = 1, rowspan: int = 1):
    if(row == None or col == None):
      self.__widget__.grid()
    else:
      self.__widget__.grid(row = row,
                       column = col,
                       rowspan = rowspan,
                       columnspan = colspan,
                       sticky = "nesw")
      
  # remove widget from the grid
  def grid_remove(self):
    self.__widget__.grid_remove()
    
  # add a new state to the cycle
  def add_state(self,
                text: str = "",
                colors: tuple[str,str] = ("black", "white"),
                enter: Callable | None = None,
                exit: Callable | None = None):
    self.__states__.append((text, colors, (enter, exit)))
    # update widget cosmetics to the first state added
    if(len(self.__states__) == 1):
      self.__widget__.config( text = text,
                          fg = colors[0],
                          bg = colors[1])
  
  # update widget to reflect specified state
  def update(self, index: int = 0):
    # check if index is valid
    if(index < 0 or index >= len(self.__states__)):
      if(self.__gui__.debug != None):
        self.__gui__.debug.error("invalid cycle update target "+str(index)+" > "+str(len(self.__states__)-1))
      return
    # call exit function of previous state
    if(self.__states__[self.state][2][1] != None):
      self.__states__[self.state][2][1]()
    # update state
    self.state = index
    self.__widget__.config( text = self.__states__[index][0],
                        fg = self.__states__[index][1][0],
                        bg = self.__states__[index][1][1])
    if(self.__gui__.debug != None):
      self.__gui__.debug.info("Cycle set to "+str(index)+": "+self.__states__[index][0])
    # call enter function of new state
    if(self.__states__[index][2][0] != None):
      self.__states__[index][2][0]()
    # call always function if specified
    if(self.func_always != None):
      self.func_always()
      
  def cycle(self):
    if(len(self.__states__) == 0):
      if(self.__gui__.debug != None):
        self.__gui__.debug.warn("Tried to cycle with no states")
      return
    self.update((self.state + 1)% len(self.__states__))

  def state_name(self) -> str:
    return self.__states__[self.state][0]
  
  def get_state_names(self) -> list[str]:
    return [state[0] for state in self.__states__]
  
# creates thumbnail / image import widget
class Thumbnail():
  __widget__: Button
  __gui__: GUI_Controller
  __total_thumbnails__: int = 0
  # image stuff
  image: Smart_Image
  thumb_size: tuple[int, int]
  # optional fields
  text: str
  accept_alpha: bool
  func_on_success: Callable | None
  
  def __init__(self, gui: GUI_Controller,
               thumb_size: tuple[int,int],
               name: str | None = None,
               text: str = "",
               accept_alpha: bool = False,
               func_on_success: Callable | None = None):
    # assign vars
    self.__gui__ = gui
    self.thumb_size = thumb_size
    self.text = text
    self.accept_alpha = accept_alpha
    self.func_on_success = func_on_success
    # build widget
    button: Button = Button(
      gui.root,
      command = self.__import_image__
      )
    if(self.text != ""):
      button.config(text = self.text,
                    compound = "top")
    self.__widget__ = button
    # create placeholder images
    placeholder = Image.new("RGB", self.thumb_size)
    self.image = Smart_Image(placeholder)
    if(name == None):
      gui.add_widget("unnamed thumbnail widget "+str(Cycle.__total_cycles__), self)
      Thumbnail.__total_thumbnails__ += 1
    else:
      gui.add_widget(name, self)
    self.update(placeholder)
  
  # prompt user for a new image
  def __import_image__(self):
    def is_valid_ext(path: str) -> bool:
      ext: str = path[-5:].lower()
      match ext[-4:]:
        case ".jpg":
          return True
        case ".png":
          return True
      match ext[-5:]:
        case ".jpeg":
          return True
      return False
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(self.__gui__.debug != None):
      if(path == ''):
        self.__gui__.debug.warn(self.text+(" " if self.text!="" else "")+"import cancelled")
        return
      if(not is_valid_ext(path)):
        self.__gui__.debug.error(self.text+(" " if self.text!="" else "")+"invalid file type: "+path[-3:])
        return
      else:
        self.__gui__.debug.info(self.text+(" " if self.text!="" else "")+"set to "+basename(path))
    img = Image.open(path).copy()
    # check type
    # ensure image is RGB or L
    match img.mode:
      case "RGB":
        pass
      case "L":
        pass
      case "RGBA":
        if(not self.accept_alpha):
          img = RGBA_to_RGB(img)
          if(self.__gui__.debug != None):
            self.__gui__.debug.warn("RGBA images are not permitted, auto converted to RGB")
      case "LA":
        if(not self.accept_alpha):
          img = LA_to_L(img)
          if(self.__gui__.debug != None):
            self.__gui__.debug.warn("LA images are not permitted, auto converted to L")
      case _:
        if(self.__gui__.debug != None):
          self.__gui__.debug.error("Invalid image mode: "+img.mode)
        return
    # update image
    self.image = Smart_Image(img)
    self.image.add("path", path, True)
    # update
    self.update()
    # call optional func if specified
    if(self.func_on_success != None):
      self.func_on_success()
    
  # update the thumbnail, optionally specify a new image
  # new image will only apply to preview, not stored smart image
  def update(self, new_image: Image.Image | None = None):
    img: Image.Image
    if(new_image == None):
      img = self.image.image
    else:
      img = new_image
    new_size: tuple[int, int] = fit_image(img, win_size=self.thumb_size)
    
    if(new_size != img.size):
      img = img.resize(new_size, Image.Resampling.NEAREST)
    
    photoImage = rasterize(img)
    self.__widget__.config(image = photoImage)
    self.__widget__.image = photoImage
    
  # place widget on the grid
  def grid(self, row: int | None = None, col: int | None = None, colspan: int = 1, rowspan: int = 1):
    if(row == None or col == None):
      self.__widget__.grid()
    else:
      self.__widget__.grid(row = row,
                       column = col,
                       rowspan = rowspan,
                       columnspan = colspan,
                       sticky = "nesw")

  # remove widget from the grid
  def grid_remove(self):
    self.__widget__.grid_remove()
    
# creates a better int input field
class Intput():
  __widget__: Entry
  __gui__: GUI_Controller
  __total_intputs__: int = 0
  var: Variable
  # user fields
  min: int | None
  max: int | None
  name: str
  invalid_color: str
  # revert displayed value to last valid value if invalid?
  auto_fix: bool
  # optional validation function, true if input is valid
  extra_validation: Callable[[int], bool] | None
  # the value that will be returned: always valid
  __value__: int
  # value checked by changed()
  last_diff: int
  
  def __init__( self, gui: GUI_Controller,
                name: str | None = None,
                default: int = 0,
                min: int | None = None,
                max: int | None = None,
                justify: Literal['left', 'center', 'right'] = "center",
                extra_validation: Callable[[int], bool] | None = None,
                auto_fix: bool = True,
                invalid_color: str = "red"
                ):
    # store user inputs
    self.__gui__ = gui
    self.min = min
    self.max = max
    self.extra_validation = extra_validation
    self.auto_fix = auto_fix
    self.invalid_color = invalid_color
    # setup var
    self.var = IntVar()
    self.var.set(default)
    self.value = self.min
    self.last_diff = default
    # setup widget
    self.__widget__ = Entry(gui.root,
                        textvariable = self.var,
                        justify=justify
                        )
    #set name
    if(name == None):
      self.name = "unnamed intput widget "+str(Intput.__total_intputs__)
      Intput.__total_intputs__ += 1
      gui.add_widget(self.name, self)
    else:
      gui.add_widget(name, self)
    # update
    self.__update__()
  
  # place widget on the grid
  def grid(self, row: int | None = None, col: int | None = None, colspan: int = 1, rowspan: int = 1):
    if(row == None or col == None):
      self.__widget__.grid()
    else:
      self.__widget__.grid(row = row,
                       column = col,
                       rowspan = rowspan,
                       columnspan = colspan,
                       sticky = "nesw")

  # remove widget from the grid
  def grid_remove(self):
    self.__widget__.grid_remove()
    
  # get the more recent vaid value
  def get(self, update: bool = True) -> int:
    if(update):
      self.__update__()
    return self.__value__
  
  
  # try and set a new value
  def set(self, user_value: int):
    self.__update__(user_value)
  
  # has the value changed since the last time this method was called
  def changed(self) -> bool:
    if(self.get() != self.last_diff):
      self.last_diff = self.get()
      return True
    return False
    
  
  # updates widget and value
  def __update__(self, new_value: int | None = None):
    # get new potential value
    new_val: int
    if(new_value == None):
      new_val = self.var.get()
    else:
      new_val = new_value
    # validate and update accordingly
    if(self.__validate__(new_val)):
      self.__value__ = new_val
      self.var.set(new_val)
      self.__widget__.config(bg="white")
    else:
      if(self.auto_fix):
        self.var.set(self.__value__)
      else:
        self.__widget__.config(bg=self.invalid_color)
      if(self.__gui__.debug != None):
        self.__gui__.debug.error("Invalid value for "+self.name+": "+str(new_val))
    self.__widget__.update()
    
  # check if the current value is valid
  def __validate__(self, new_val: int) -> bool:
    # check min / max
    if(self.min != None and new_val < self.min):
      return False
    if(self.max != None and new_val > self.max):
      return False
    # check extra validation
    if(self.extra_validation != None and not self.extra_validation(new_val)):
      return False
    # passed all checks
    return True

# creates a better float input field
class Floatput():
  # private fields
  __widget__: Entry
  __gui__: GUI_Controller
  __total_floatputs__: int = 0
  accuracy: int
  var: Variable
  # user fields
  min: float | None
  max: float | None
  name: str
  invalid_color: str
  # revert displayed value to last valid value if invalid
  auto_fix: bool
  # optional validation function, true if input is valid
  extra_validation: Callable[[float], bool] | None
  # the value that will be returned: always valid
  __value__: float
  # value checked by changed()
  last_diff: float
  
  def __init__( self, gui: GUI_Controller,
                name: str | None = None,
                default: float = 0,
                display_accuracy: int = 2,
                min: float | None = None,
                max: float | None = None,
                justify: Literal['left', 'center', 'right'] = "center",
                extra_validation: Callable[[float], bool] | None = None,
                auto_fix: bool = True,
                invalid_color: str = "red"
                ):
    # store user inputs
    self.__gui__ = gui
    self.accuracy = display_accuracy
    self.min = min
    self.max = max
    self.extra_validation = extra_validation
    self.auto_fix = auto_fix
    self.invalid_color = invalid_color
    # setup var
    self.var = DoubleVar()
    self.var.set(default)
    self.value = self.min
    self.last_diff = default
    # setup widget
    self.__widget__ = Entry(gui.root,
                            textvariable = self.var,
                            justify=justify
                            )
    #set name
    if(name == None):
      self.name = "unnamed floatput widget "+str(floatput.__total_floatputs__)
      floatput.__total_floatputs__ += 1
      gui.add_widget(self.name, self)
    else:
      gui.add_widget(name, self)
    # update
    self.__update__()
  
  # place widget on the grid
  def grid(self, row: int | None = None, col: int | None = None, colspan: int = 1, rowspan: int = 1):
    if(row == None or col == None):
      self.__widget__.grid()
    else:
      self.__widget__.grid(row = row,
                       column = col,
                       rowspan = rowspan,
                       columnspan = colspan,
                       sticky = "nesw")

  # remove widget from the grid
  def grid_remove(self):
    self.__widget__.grid_remove()
    
  # get the more recent vaid value
  def get(self, update: bool = True) -> float:
    if(update):
      self.__update__()
    return self.__value__
  
  
  # try and set a new value
  def set(self, user_value: float):
    self.__update__(user_value)
  
  # has the value changed since the last time this method was called
  def changed(self) -> bool:
    if(self.get() != self.last_diff):
      self.last_diff = self.get()
      return True
    return False
    
  
  # updates widget and value
  def __update__(self, new_value: float | None = None):
    # get new potential value
    new_val: float
    if(new_value == None):
      new_val = self.var.get()
    else:
      new_val = new_value
    # validate and update accordingly
    if(self.__validate__(new_val)):
      self.__value__ = new_val
      self.var.set(round(new_val,self.accuracy))
      self.__widget__.config(bg="white")
    else:
      if(self.auto_fix):
        self.var.set(self.__value__)
      else:
        self.__widget__.config(bg=self.invalid_color)
      if(self.__gui__.debug != None):
        self.__gui__.debug.error("Invalid value for "+self.name+": "+str(new_val))
    self.__widget__.update()
    
  # check if the current value is valid
  def __validate__(self, new_val: float) -> bool:
    # check min / max
    if(self.min != None and new_val < self.min):
      return False
    if(self.max != None and new_val > self.max):
      return False
    # check extra validation
    if(self.extra_validation != None and not self.extra_validation(new_val)):
      return False
    # passed all checks
    return True

# creates a fullscreen window and displays specified images to it
class Projector_Controller():
  ### Internal Fields ###
  __TL__: Toplevel
  __label__: Label
  __root__: Tk
  __is_patterning__: bool = False
  # just a black image to clear with
  __clearImage__: ImageTk.PhotoImage
  ### optional user args ###
  debug: Debug | None
  progressbar: Progressbar | None
  
  def __init__( self,
                root: Tk,
                title: str = "Projector",
                background: str = "#000000",
                debug: Debug | None = None
                ):
    # store user inputs
    self.title = title
    self.__root__ = root
    self.debug = debug
    # setup projector window
    self.__TL__ = Toplevel(root)
    self.__TL__.title(self.title)
    self.__TL__.attributes('-fullscreen',True)
    self.__TL__['background'] = background
    self.__TL__.grid_columnconfigure(0, weight=1)
    self.__TL__.grid_rowconfigure(0, weight=1)
    # create projection Label
    self.__label__ = Label(self.__TL__, bg='black')
    self.__label__.grid(row=0,column=0,sticky="nesw")
    # generate dummy black image
    self.__clearImage__ = rasterize(Image.new("L", self.size())) 
    self.update()
    
  # show an image
  # if a duration is specified, show the image for that many milliseconds
  def show(self, image: Image.Image, duration: int = 0) -> bool:
    if(self.__is_patterning__):
      if(self.debug != None):
        self.debug.warn("Tried to show image while another is still showing")
      return False
    # warn if image isn't correct size
    if(image.size != fit_image(image, self.size())):
      if(self.debug != None):
        self.debug.warn("projecting image with incorrect size:\n  "+str(image.size)+" instead of "+str(self.size()))
    photo: ImageTk.PhotoImage = rasterize(image)
    self.__label__.config(image = photo)
    self.__label__.image = photo
    if(duration > 0):
      self.__is_patterning__ = True
      end = time() + duration / 1000
      # update and begin
      self.update()
      while(time() < end and self.__is_patterning__):
        if(self.progressbar != None):
          self.progressbar['value'] = 100 - ((end - time()) / duration * 100000)
          self.__root__.update()
        pass
      self.clear()
    else:
      self.update()
    return True
  
  # clear the projector window
  def clear(self):
    self.__label__.config(image = self.__clearImage__)
    self.__label__.image = self.__clearImage__
    self.__is_patterning__ = False
    if(self.progressbar != None):
      self.progressbar['value'] = 0
    self.update()

  # get size of projector window
  def size(self, update: bool = True) -> tuple[int,int]:
    if(update): self.update()
    return (self.__TL__.winfo_width(), self.__TL__.winfo_height())
  
  #update the projector window
  def update(self):
    self.__root__.update()
    self.__TL__.update()

# creates a new window with specified text. Useful for a help menu
class TextPopup():
  ### Internal Fields ###
  __TL__: Toplevel
  __label__: Label
  __root__: Tk
  __widget__: Button
  ### User Fields ###
  button_text: str
  popup_text: str
  debug: Debug | None
  
  def __init__(self, root: Tk,
               button_text: str = "",
               popup_text: str = "",
               title: str = "Popup",
               debug: Debug | None = None):
    # assign vars
    self.__root__ = root
    self.button_text = button_text
    self.popup_text = popup_text
    self.title = title
    self.debug = debug
    # build button widget
    button: Button = Button(
      root,
      command = self.show
      )
    if(button_text != ""):
      button.config(text = button_text,
                    compound = "top")
    self.__widget__ = button

  #show the text popup
  def show(self):
    self.__TL__ = Toplevel(self.__root__)
    self.__TL__.title(self.title)
    self.__TL__.grid_columnconfigure(0, weight=1)
    self.__TL__.grid_rowconfigure(0, weight=1)
    self.__label__ = Label(self.__TL__, text=self.popup_text, justify="left")
    self.__label__.grid(row=0,column=0,sticky="nesw")
    if(self.debug != None):
      self.debug.info("Showing "+self.button_text+" popup")
    self.update()

  # place widget on the grid
  def grid(self, row: int | None = None, col: int | None = None, colspan: int = 1, rowspan: int = 1):
    if(row == None or col == None):
      self.__widget__.grid()
    else:
      self.__widget__.grid(row = row,
                       column = col,
                       rowspan = rowspan,
                       columnspan = colspan,
                       sticky = "nesw")

  # remove widget from the grid
  def grid_remove(self):
    self.__widget__.grid_remove()
    
  def update(self, new_text: str = ""):
    if(new_text != ""):
      self.text = new_text
      self.__label__.config(text = new_text)
    self.__root__.update()
    self.__TL__.update()

# TODO auto adjust rows and cols when adding children
# TODO auto debug widget creation and application to children
# GUI controller and widget manager
class GUI_Controller():
  # list of accepted widget types
  gui_widgets = Union[Widget, Cycle, Thumbnail, Debug, Intput, Floatput, TextPopup]
  #region: fields
  ### Internal Fields ###
  root: Tk
  __widgets__: dict[str, gui_widgets]
  ### User Fields ###
  # Mandatory
  grid_size: tuple[int,int]
  # Optional
  title: str
  window_size: tuple[int,int]
  resizeable: bool
  debug: Debug | None
  colors: dict[str, tuple[str,str]]
  #endregion
  
  def __init__( self,
                grid_size: tuple[int,int],
                set_window_size: tuple[int,int] = (0, 0),
                add_window_size: tuple[int,int] = (0, 0),
                title: str = "GUI Controller",
                resizeable: bool = True,
                add_projector: bool = True,
                ):
    # store user input variables
    self.grid_size = grid_size
    self.title = title
    self.resizeable = resizeable
    # setup root / gui window
    self.root = Tk()
    self.window_size = set_window_size
    if(set_window_size == (0,0)):
      self.window_size = (self.root.winfo_screenwidth()//2, self.root.winfo_screenheight()//2)
    if(add_window_size != (0,0)):
      self.window_size = (self.window_size[0]+add_window_size[0], self.window_size[1]+add_window_size[1])
    self.root.title(self.title)
    self.root.geometry(str(self.window_size[0])+"x"+str(self.window_size[1]))
    self.root.resizable(width = self.resizeable, height = self.resizeable)
    for row in range(self.grid_size[0]):
      self.root.grid_rowconfigure(row, weight=1)
    for col in range(self.grid_size[1]):
      self.root.grid_columnconfigure(col, weight=1)
    # create projector window
    if(add_projector):
      self.proj: Projector_Controller = Projector_Controller(self.root)
    # create dictionary of widgets
    self.__widgets__ = {}

  #TODO test if typing like this actually works
  def add_widget(self, name: str, widget: gui_widgets):
    # if a debug widget is added, save it as the debug field
    if(type(widget) == Debug):
      self.debug = widget
      self.proj.debug = widget
    else:
      self.__widgets__[name] = widget
    self.update()
      
  # return widget by name, or None if not found
  def get_widget(self, name: str) -> gui_widgets | None:
    return self.__widgets__.get(name, None)
  
  # remove widget by name
  def del_widget(self, name: str):
    # remove widget from dictionary
    widget = self.__widgets__.pop(name, None)
    # check if widget was found
    if(widget == None):
      if(self.debug != None):
        self.debug.warn("Tried to remove widget "+name+" but it was not found")
      return
    # report success
    self.debug.info("Removed widget "+name)
    self.update()
  
  # update the GUI window  
  def update(self):
    self.root.update()
    
  # start the main loop
  def mainloop(self):
    self.root.mainloop()

# TODO add theta?
# TODO make floats?
# TODO add changed() function
# class to manage global stage coordinates. 
# can specify list of functions to call when updating coords
# can add debug widget to print info at various verbosity levels:
# <=0: no info
#   1: basic info
#   2: basic info + function calls
class Stage_Controller():
  update_funcs: dict[Literal['x','y','z','any'], dict[str, Callable]]
  debug: Debug | None
  step_size: tuple[float,float,float]
  __coords__: tuple[float,float,float]
  __verbosity__: int
  __locked__: bool = False
  
  def __init__(self,
               starting_coords: tuple[float,float,float] = (0,0,0),
               step_sizes: tuple[float,float,float] = (1,1,1),
               debug: Debug | None = None,
               verbosity: int = 1):
    self.update_funcs = {'x':{}, 'y':{}, 'z':{}, 'any':{}}
    self.__coords__ = starting_coords
    self.step_size = step_sizes
    self.debug = debug
    self.__verbosity__ = verbosity
  
  def __str2key__(self, axis: str) -> Literal['x','y','z','any'] | None:
    match axis[-1]:
      case 'x':
        return 'x'
      case 'y':
        if(axis == 'any'):
          return 'any'
        else:
          return 'y'
      case 'z':
        return 'z'
  
  def __call_funcs__(self, axis: str):
    # convert arbitrary string to literal
    key: Literal['x','y','z','any']|None = self.__str2key__(axis)
    if(key == None):
      return
    # call all functions
    for func in self.update_funcs.get(key,{}):
      self.update_funcs.get(key,{}).get(func, lambda: None)()

  #region: Convenience Getters
  def x(self) -> float:
    return self.__coords__[0]
  def y(self) -> float:
    return self.__coords__[1]
  def z(self) -> float:
    return self.__coords__[2]
  def xy(self) -> tuple[float,float]:
    return (self.__coords__[0], self.__coords__[1])
  def xz(self) -> tuple[float,float]:
    return (self.__coords__[0], self.__coords__[2])
  def yz(self) -> tuple[float,float]:
    return (self.__coords__[1], self.__coords__[2])
  def xyz(self) -> tuple[float,float,float]:
    return self.__coords__
  #endregion
  
  def lock(self):
    self.__locked__ = True
    
  def unlock(self):
    self.__locked__ = False
  
  def step(self, axis: Literal['-x','x','+x','-y','y','+y','-z','z','+z'], size: float = 0, update: bool = True):
    if(self.__locked__):
      if(self.debug != None):
        self.debug.warn("Tried to move stage while locked")
      return
    delta: tuple[float,float,float] = (0,0,0)
    if(size == 0):
      match axis[-1]:
        case 'x':
          delta = (self.step_size[0],0,0)
        case 'y':
          delta = (0,self.step_size[1],0)
        case 'z':
          delta = (0,0,self.step_size[2])
    else:
      match axis[-1]:
        case 'x':
          delta = (size,0,0)
        case 'y':
          delta = (0,size,0)
        case 'z':
          delta = (0,0,size)
    if(axis[0] == '-'):
      delta = mult(delta, -1)
    self.__coords__ = add(self.__coords__, delta)
    if(update):
      self.__call_funcs__(axis)
      self.__call_funcs__('any')
    #region: debug
    if(self.debug != None and self.__verbosity__ > 0):
      debug_str: str = ""
      if(self.__verbosity__ >= 1):
        debug_str+="stage stepped "+str(delta)+" to "+str(self.__coords__)
      if(self.__verbosity__ >= 2 and update):
        debug_str += " and called:"
        # convert arbitrary string to literal
        key: Literal['x','y','z','any']|None = self.__str2key__(axis)
        if(key != None):
          for func in self.update_funcs.get(key,{}):
            debug_str += "\n  "+axis[-1]+": "+func
        for func in self.update_funcs.get('any',{}):
          debug_str += "\n  any: "+func
      self.debug.info(debug_str)

  # set coords from a list of set of floats
  def set(self, x:float, y:float, z:float, update: bool = True):
    if(self.__locked__):
      if(self.debug != None):
        self.debug.warn("Tried to move stage while locked")
      return
    self.__coords__ = (x,y,z)
    if(update):
      self.__call_funcs__('x')
      self.__call_funcs__('y')
      self.__call_funcs__('z')
      self.__call_funcs__('any')
    #region: debug
    if(self.debug != None and self.__verbosity__ > 0):
      debug_str: str = ""
      if(self.__verbosity__ >= 1):
        debug_str+="stage set to "+str((x,y,z))
      if(self.__verbosity__ >= 2 and update):
        debug_str += " and called:"
        for func in self.update_funcs.get('x',{}):
          debug_str += "\n  x: "+func
        for func in self.update_funcs.get('y',{}):
          debug_str += "\n  y: "+func
        for func in self.update_funcs.get('z',{}):
          debug_str += "\n  z: "+func
        for func in self.update_funcs.get('any',{}):
          debug_str += "\n  any: "+func
      self.debug.info(debug_str)
    #endregion
  #endregion
 
# Class takes an image and slicing parameters and returns slices
class Slicer():
  # pattern types
  pattern_type = Literal['snake', 'row major', 'col major']
  pattern_list: list[Literal['snake', 'row major', 'col major']] = ['snake', 'row major', 'col major']
  #fields
  __full_image__: Image.Image | None = None
  __sliced_images__: tuple[Image.Image,...] = ()
  __index__: int = 0
  __pattern__: pattern_type
  __horizontal_slices__: int = 0
  __vertical_slices__: int = 0
  __grid_size__: tuple[int,int] = (0,0)
  debug: Debug | None
  
  def __init__(self, 
               image: Image.Image|None = None, 
               horizontal_tiles: int = 0,
               vertical_tiles: int = 0,
               tiling_pattern: pattern_type = 'snake',
               debug: Debug | None = None):
    if(horizontal_tiles >= 0):
      self.__horizontal_slices__ = horizontal_tiles
    if(vertical_tiles >= 0):
      self.__vertical_slices__ = vertical_tiles
    self.__pattern__ = tiling_pattern
    if(image != None):
      self.__full_image__ = image.copy()
      (self.__grid_size__, self.__sliced_images__) = slice( self.__full_image__,
                                                            self.__horizontal_slices__,
                                                            self.__vertical_slices__)
    self.debug = debug
  
  #convert internal index counter to specified pattern index
  def __convert_index__(self, index: int = -1) -> int:
    if(index == -1):
      index = self.__index__
    match self.__pattern__:
      case 'row major':
        return index
      case 'col major':
        return self.__grid_size__[0]*(index % self.__grid_size__[1]) + index // self.__grid_size__[1]
      case 'snake':
        row: int = index // self.__grid_size__[0]
        if(row % 2 == 0):
          return index
        else:
          return self.__grid_size__[0]*(row+1) - (index % self.__grid_size__[0]) - 1
    return 0
  
  # increment index, false if at end of list
  def next(self, increment: int = 1) -> bool:
    if(increment < 1):
      return False
    elif(self.__index__ + increment >= len(self.__sliced_images__)):
      return False
    else:
      self.__index__ += increment
      return True
  
  # decrement index, false if at beginning of list
  def prev(self, decrement: int = 1) -> bool:
    if(decrement < 1):
      return False
    elif(self.__index__ - decrement < 0):
      return False
    else:
      self.__index__ -= decrement
      return True
  
  # returns current image
  def image(self) -> Image.Image:
    result: Image.Image = self.__sliced_images__[self.__convert_index__()]
    return result
  
  # returns next image, if possible, without incrementing index
  def peek(self) -> Image.Image | None:
    result = None
    if(self.next()):
      result = self.image()
      self.prev()
    return result
  
  # returns number of tiles
  def tile_count(self) -> int:
    return len(self.__sliced_images__)
  
  # rests tile index to 0
  def restart(self):
    self.__index__ = 0
  
  # update slicer parameters
  # will reset index, so calling with no args is equivalent to resetting 
  def update( self, 
              image: Image.Image|None = None,
              horizontal_tiles: int = 0,
              vertical_tiles: int = 0,
              tiling_pattern: pattern_type = 'snake'):
    
    reslice: bool = False
    self.__index__ = 0
    
    if(image!=None):
      self.__full_image__ = image.copy()
      reslice = True
      
    if(self.__horizontal_slices__ != horizontal_tiles and horizontal_tiles >= 0):
      self.__horizontal_slices__ = horizontal_tiles
      reslice = True
    
    if(self.__vertical_slices__ != vertical_tiles and vertical_tiles >= 0):
      self.__vertical_slices__ = vertical_tiles
      reslice = True  
    
    if(self.__pattern__ != tiling_pattern):
      self.__pattern__ = tiling_pattern
      reslice = True
      
    if(reslice and self.__full_image__ != None):
      (self.__grid_size__, self.__sliced_images__) = slice( self.__full_image__,
                                                            self.__horizontal_slices__,
                                                            self.__vertical_slices__)

# swaps around groups of widgets
# Requires a GUI controller
# hides widgets with grid_remove()
class Smart_Area():
  # gui controller to query widgets from
  __gui__: GUI_Controller
  # list of widget lists
  __widgets__: list[list[GUI_Controller.gui_widgets]]
  # list of special fucntions to call when switching groups
  # show first, hide second (show, hide)
  __funcs__: list[tuple[Callable | None, Callable | None]]
  # current index of the list
  __index__: int = 0
  # debug widget
  debug: Debug | None
  name: str | None
  #endregion
  
  def __init__( self,
                gui: GUI_Controller,
                debug: Debug | None = None,
                name: str | None = None):
    self.__widgets__ = []
    self.__funcs__ = []
    self.__gui__ = gui
    self.debug = debug
    self.name = name
    
  def __hide__(self, group: int, func_first: bool = True):
    if(func_first and self.__funcs__[group][1] != None):
      self.__funcs__[group][1]()
    for widget in self.__widgets__[group]:
      widget.grid_remove()
    if(not func_first and self.__funcs__[group][1] != None):
      self.__funcs__[group][1]()
    
  def __show__(self, group: int, func_first: bool = True):
    if(func_first and self.__funcs__[group][0] != None):
      self.__funcs__[group][0]()
    for widget in self.__widgets__[group]:
      widget.grid()
    if(not func_first and self.__funcs__[group][0] != None):
      self.__funcs__[group][0]()
  
  # add one or several widgets to specified group
  # disable hide to leave widgets visible after adding (not recommended, use jump() instead)
  def add(self, group: int, widgets: str | list[str], hide: bool = True):
    #normalize to list
    names: list[str]
    if(type(widgets) == str):
      names = [widgets]
    elif(type(widgets) == list):
      names = widgets
    else:
      raise Exception("widgets must be a string or a list of strings")
    
    # check group number
    if(group < 0):
      raise Exception("only positive group numbers are allowed")
    elif(group > len(self.__widgets__)):
      if(self.debug != None):
        msg: str = "non-consecutive group number, added filler groups"
        if(self.name != None):
          msg = self.name+" "+msg
        self.debug.warn(msg)
      for i in range(len(self.__widgets__), group+1):
        self.__widgets__.append([])
        self.__funcs__.append((None, None))
    elif(group == len(self.__widgets__)):
      self.__widgets__.append([])
      self.__funcs__.append((None, None))
      
    # add widgets to list
    for name in names:
      widget: GUI_Controller.gui_widgets | None = self.__gui__.get_widget(name)
      if(widget == None):
        if(self.debug != None):
          msg: str = "Tried to add non-existent widget \""+name+"\" to group "+str(group)
          if(self.name != None):
            msg = self.name+" "+msg
          self.debug.error(msg)
      else:
        self.__widgets__[group].append(widget)
    
    if(hide):
      self.__hide__(group)
  
  # add special functions when showing or hiding a group
  def add_func(self, group: int, show: Callable | None = None, hide: Callable | None = None):
    if(group < 0 or group >= len(self.__funcs__)):
      if(self.debug != None):
        msg: str = "can only add special functions to existing groups, add an empty group first"
        if(self.name != None):
          msg = self.name+" "+msg
        self.debug.error(msg)
      return
    self.__funcs__[group] = (show, hide)
    
  
  # hide current widget and jump to specified group
  # if order matters, toggle the func_first parameter (show, hide)
  def jump(self, group: int, func_first: tuple[bool,bool] = (True, True)):
    if(self.debug != None):
      msg: str = "switched from group "+str(self.__index__)+" to "+str(group % len(self.__widgets__))
      if(self.name != None):
        msg = self.name+" "+msg
      self.debug.info(msg)
    self.__hide__(self.__index__, func_first[1])
    self.__index__ = group % len(self.__widgets__)
    self.__show__(self.__index__, func_first[0])
  
  def next(self, func_first: tuple[bool,bool] = (True, True)):
    self.jump(self.__index__ + 1, func_first)
    
  def prev(self, func_first: tuple[bool,bool] = (True, True)):
    self.jump(self.__index__ - 1, func_first)

  def index(self) -> int:
    return self.__index__

# a widget that stores an image and various other useful info
# intentionally no way to change original image after creation
# to avoid confusion
class Smart_Image():
  __original_image__: Image.Image
  __permanent_attr__: dict
  __attr__: dict
  image: Image.Image
  
  def __init__(self, image: Image.Image, perm_attr: dict = {}):
    self.__original_image__ = image.copy()
    self.image = image.copy()
    self.__permanent_attr__ = perm_attr
    self.__attr__ = {}
  
  # permanent attributes are reapplied on reset
  def add(self, key, value, permanent: bool = False):
    self.__attr__[key] = value
    if(permanent):
      self.__permanent_attr__[key] = value
      
  def get(self, key, default = None):
    return self.__attr__.get(key, default)

  def pop(self, key, default = None):
    return self.__attr__.pop(key, default)
  
  def copy(self):
    new_img = Smart_Image(self.image.copy())
    new_img.__original_image__ = self.__original_image__.copy()
    new_img.__permanent_attr__ = self.__permanent_attr__.copy()
    new_img.__attr__ = self.__attr__.copy()
    new_img.image = self.image.copy()
    return new_img
    
  # reset image to original
  # resets all attributes except those specified in keep_attr
  def reset(self, keep_attr: list = []):
    self.image = self.__original_image__.copy()
    new_attr = self.__permanent_attr__.copy()
    for key in keep_attr:
      if(self.__attr__.get(key, None) != None):
        new_attr[key] = self.__attr__[key]
    self.__attr__ = new_attr
  
  # return image size
  def size(self) -> tuple[int,int]:
    return self.image.size
  
  # return image mode
  def mode(self) -> str:
    return self.image.mode
  
