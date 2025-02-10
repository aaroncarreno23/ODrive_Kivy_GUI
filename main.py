""" After you have tested each example, l
et us finish by making a Kivy GUI. You will find template
files in the KivyTemplate folder of this repository. Your goal
with this GUI is to have the following –

A button that toggles between moving the motor 5
rotations clockwise and counterclockwise

A slider that controls the velocity of the motor
A second slider that controls the acceleration of the
motor (i.e. two sliders to handle ramped velocity)

Consider changing your velocity slider to use ramped velocity and
retrieve the acceleration value from the second slider.

Another screen that controls the motor with trapezoidal trajectory
control. Have text boxes for acceleration, target position, and
deceleration plus a submit button to send the command to the motor.

Another screen which utilizes a GPIO pin to move the motor when a
sensor or switch is activated."""

import os
import sys

from IPython.utils.wildcard import dict_dir
from aptdaemon.policykit1 import get_pid_from_dbus_name
# os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition, SlideTransition

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from dpea_odrive.odrive_helpers import digital_read
import time
from kivy.clock import Clock

#ax.home_with_endstop(1, 0.05, 2)

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")
from dpea_odrive.odrive_helpers import *
od = find_odrive("207935A1524B")
# 0x207935a1524b - serial number
assert od.config.enable_brake_resistor is True, 'Check for faulty brake resistor'
print(dir(od.config))
#ax = ODriveAxis(od.axis0)
ax = ODriveAxis(od.axis1)
#print("Axis 0 state:", od.axis0.current_state)
print("Axis 1 state:", od.axis1.current_state)

if not ax.is_calibrated():
    print('calibrating...')
    ax.calibrate_with_current_lim(10)

print("Current Limit:", ax.get_current_limit())
print("Velocity Limit:", ax.get_current_limit())
dump_errors(od)

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
TRAJ_SCREEN_NAME = 'traj'
GPIO_SCREEN_NAME = 'gpio'
ADMIN_SCREEN_NAME = 'admin'
SETTINGS_SCREEN_NAME = 'settings'
RATE_SCREEN_NAME = 'rate'

velocity_value = 0
acceleration_value = 0
pin_num = 8
#digital_read(od, pin_num)
#NOT TOUCHING SWITCH IS 1 AND TOUCHING SWITCH IS 0

#ax.set_vel_limit(1)
#ax.set_relative_pos(5)
#ax.wait_for_motor_to_stop()
#print("Current Position in Turns = ", round(ax.get_pos(), 2))

#ax.set_relative_pos(-1)
#ax.wait_for_motor_to_stop()

#13 revolutions from one end to the other
# negative for toward switch, positive for away from switch

#TRY TO MAKE IF IT RAN 13 NEGATIVE THE NEXT 13 ARE POSITIVE TO PREVENT CRASHING

#ax.home_with_endstop(vel, offset, min_gpio_num)

class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER

Window.clearcolor = (1, 1, 1, 1)  # White

class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.direction_CW = False
        #self.start_sensor_updates()

    def change_direction(self):
        if self.direction_CW:
            self.direction_CW = False
            self.ids.rotation_direction.text = "Counter ClockWise"
            print("CCW")

        else:
            self.direction_CW = True
            self.ids.rotation_direction.text = "ClockWise"
            print("CW")

    def five_rotations(self):

        if self.direction_CW:
            ax.set_relative_pos(1)
            ax.wait_for_motor_to_stop()
            print("Current Position in Turns = ", round(ax.get_pos(), 2))
        else:
             ax.set_relative_pos(-1)
             ax.wait_for_motor_to_stop()
             print("Current Position in Turns = ", round(ax.get_pos(), 2))

    def switch_to_settings(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='left')
        SCREEN_MANAGER.current = SETTINGS_SCREEN_NAME

    def switch_to_admin(self):
        SCREEN_MANAGER.transition = FallOutTransition()
        SCREEN_MANAGER.current = ADMIN_SCREEN_NAME

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'

    def endstop(self):
            print("Homeing...")
            ax.home_with_endstop(1, 0, 8)
            print("Homed")

        #pin_state_before = digital_read(od, pin_num)
        #print(pin_state_before)
        #ax.home_with_endstop(1, 0, 8)
        #print(ax.set_home())
        #pin_state_after = digital_read(od, pin_num)
        #print(pin_state_after)
        #if pin_state_after == 0:
        #    print("Endstop touched after homing")
        #    ax.set_relative_pos(1)

        #else:
        #    print("Endstop untouched after homing")
        #    ax.set_relative_pos(9)

class TrajectoryScreen(Screen):
    """
    Class to handle the trajectory control screen and its associated touch events
    """

    def switch_screen_settings(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='right')
        SCREEN_MANAGER.current = SETTINGS_SCREEN_NAME

    def trajectory(self, slider, value):
        pass

    #ax.set_pos_traj(5, 1, 10,1)  # position 5(turns), acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
    #ax.set_pos_traj(-5, 1, 10,1)  # position -5(turns), acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
    #ax.idle()

class GPIOScreen(Screen):
    """
    Class to handle the GPIO screen and its associated touch/listening events
    """

    def switch_screen_settings(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='right')
        SCREEN_MANAGER.current = SETTINGS_SCREEN_NAME

class SettingsScreen(Screen):

    def switch_to_main(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='right')
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def switch_to_gpio(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='left')
        SCREEN_MANAGER.current = GPIO_SCREEN_NAME

    def switch_to_traj(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='left')
        SCREEN_MANAGER.current = TRAJ_SCREEN_NAME

    def switch_to_rate(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='left')
        SCREEN_MANAGER.current = RATE_SCREEN_NAME

class RateScreen(Screen):

    def switch_to_settings(self):
        SCREEN_MANAGER.transition = SlideTransition(direction='right')
        SCREEN_MANAGER.current = SETTINGS_SCREEN_NAME

    def velocity(self, slider, value):
        global velocity_value
        velocity_value = value
        ax.set_vel_limit(value)
        self.ids.velocity_label.text = f"Velocity {int(value)} turns per second"
        print(f"Velocity {int(value)} turns per second")

    def acceleration(self, slider, value):
        ax.set_ramped_vel(velocity_value, value)
        self.ids.acceleration_label.text = f"Acceleration {int(value)}"
        print(f"Acceleration: {int(value)}")

class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """
    def switch_to_main(self):
        SCREEN_MANAGER.transition = FallOutTransition()
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()

"""
Widget additions
"""

Builder.load_file('main.kv')
print("Loaded main.kv")
Builder.load_file('SettingsScreen.kv')
print("Loaded SettingsScreen.kv")
Builder.load_file('GPIOScreen.kv')
print("Loaded GPIOScreen.kv")
Builder.load_file('TrajectoryScreen.kv')
print("Loaded TrajectoryScreen.kv")
Builder.load_file('RateScreen.kv')
print("Loaded RateScreen.kv")
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(TrajectoryScreen(name=TRAJ_SCREEN_NAME))
SCREEN_MANAGER.add_widget(GPIOScreen(name=GPIO_SCREEN_NAME))
SCREEN_MANAGER.add_widget(SettingsScreen(name=SETTINGS_SCREEN_NAME))
SCREEN_MANAGER.add_widget(RateScreen(name=RATE_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""

def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()

if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()