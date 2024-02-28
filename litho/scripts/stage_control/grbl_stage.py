# Hacker Fab
# J. Kent Wirant
# GRBL Stage Controller

import stage_controller
import io

class GrblStage(StageController):
    # only x, y, and z axes are supported by this interface
    # may support alternative axes schemes in the future
    def __init__(self, 
                 controller_target: str, 
                 bounds: tuple[tuple[float,float],tuple[float,float],tuple[float,float]] = ((-10,10),(-10,10),(-10,10)), 
                 # axes: tuple[str] = ('x','y','z'),
                 position: tuple[float,float,float]=(0,0,0)):
        self.controller_target = controller_target

        try:
            self.controller_file = io.open(self.controller_target, 'w')
            self.controller_file.write(f'G92 {-position[0]} {-position[1]} {-position[2]}') # set origin based on initial position
        except:
            print(f'Error: Could not open motor control file "{controller_target}"')

        if len(position) == len(bounds): # == len(axes):
            self.bounds = bounds
            self.axes = ('x', 'y', 'z')
            self.position = position
        else:
            # this should never be printed under current logic
            print('Error: Axes, bounds, and/or position tuples have mismatching dimensions.')

        for b in bounds:
            assert b[0] <= b[1]

    def __del__(self):
        self.controller_file.close()

    # pass in list of amounts to move by. Dictionary in "axis: amount" format
    def move_by(self, amounts: dict[str, float]):
        # first make sure axes are valid
        if self.__axes_valid__(amounts.keys):
            x, y, z = self.__adjust_coordinates__(amounts, True)
            self.controller_file.write('G91') # set relative movement mode
            self.controller_file.write(f'G0 {x} {y} {z}') # move by this amount
            # if that worked, update internal position
            self.position[0] += x
            self.position[1] += y
            self.position[2] += z

    def move_to(self, amounts: dict[str, float]):
        # first make sure axes are valid
        if self.__axes_valid__(amounts.keys):
            x, y, z = self.__adjust_coordinates__(amounts, False)
            self.controller_file.write('G90') # set absolute movement mode
            self.controller_file.write(f'G0 {x} {y} {z}') # move by this amount
            # if that worked, update internal position
            self.position[0] = x
            self.position[1] = y
            self.position[2] = z

    def __axes_valid__(self, axes):
        for axis in axes:
            if axis not in self.axes or axis != 'x' or axis != 'y' or axis != 'z':
                return False
        return True
    
    def __adjust_coordinates__(self, amounts: dict[str, float], relative: bool):
        coords = [0, 0, 0]
        clamped_amt = [0, 0, 0]
        coords[0] = amounts.get('x')
        coords[1] = amounts.get('y')
        coords[2] = amounts.get('z')

        for i in range(0, len(coords)):
            if coords[i] == None:
                if relative:
                    coords[i] = 0
                else:
                    coords[i] = self.position[i]
            else:
                # if bounds exceeded, set target coordinate to the boundary
                if relative:
                    if coords[i] + self.position[i] > self.bounds[i][1]:
                        clamped_amt[i] = self.bounds[i][1] - self.position[i]
                    elif coords[i] + self.position[i] < self.bounds[i][0]:
                        clamped_amt[i] = self.bounds[i][0] - self.position[i]
                    else:
                        clamped_amt[i] = coords[i] + self.position[i]
                else:
                    if coords[i] > self.bounds[i][1]:
                        clamped_amt[i] = self.bounds[i][1]
                    elif coords[i] < self.bounds[i][0]:
                        clamped_amt[i] = self.bounds[i][0]
                    else:
                        clamped_amt = coords[i]

        return clamped_amt
