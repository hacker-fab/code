# library for probe station script
from tkinter import Label

# class to handle getting screen coordinates
class Screen_Coords:
  
  def __get_coords__(self, event) -> None:
    self.last_coords = (event.x, event.y)
    self.changed = True
  
  def __init__(self, target, button: str = "<Button 1>"):
    self.target = target
    self.last_coords: tuple[int,int] = (0,0)
    self.target.bind(button, self.__get_coords__)
    self.changed: bool = False
  
  