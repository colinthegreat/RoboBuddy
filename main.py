import json
from kivy.config import Config

# Configure Full Screen Mode
# 'auto' tries to use the current screen resolution
# '0' would be windowed mode
Config.set('graphics', 'fullscreen', 'auto')

# Ensure window is maximized if not fullscreen
Config.set('graphics', 'window_state', 'maximized')

# Allow closing with Escape key (useful for testing)
Config.set('kivy', 'exit_on_escape', '1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from datetime import datetime
import threading, queue, subprocess, os
import platform
from pathlib import Path

# --- Motor Control Setup ---
try:
    from gpiozero import Motor
    print("GPIO Zero imported successfully.")
except ImportError:
    print("GPIO Zero not found. Simulating motors.")
    class Motor:
        def __init__(self, forward=None, backward=None):
            self.f = forward
            self.b = backward
        def forward(self):
            print(f"Motor ({self.f}, {self.b}) -> FORWARD")
        def backward(self):
            print(f"Motor ({self.f}, {self.b}) -> BACKWARD")
        def stop(self):
            print(f"Motor ({self.f}, {self.b}) -> STOP")
        def close(self):
            pass

# Initialize Motors (Pin configuration from motor_test.py)
# Motor 1 (Left?) connected to GPIO 5 and 6
motor_left = Motor(forward=5, backward=6)
# Motor 2 (Right?) connected to GPIO 13 and 19
motor_right = Motor(forward=13, backward=19)
# ---------------------------

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)  # keeps tasks.json and relative audio paths stable

_audio_q: "queue.Queue[Path]" = queue.Queue()

def _audio_worker():
    while True:
        p = _audio_q.get()
        try:
            print(f"Playing audio: {p}")
            if platform.system() == "Windows":
                # Use PowerShell to play wav file on Windows
                subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{str(p)}').PlaySync()"], check=True)
            else:
                # Use pw-play on Linux/Pi (PipeWire)
                subprocess.run(["pw-play", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Audio error playing {p}: {e}")
        finally:
            _audio_q.task_done()

threading.Thread(target=_audio_worker, daemon=True).start()

def enqueue_audio(path: str | None):
    if not path:
        return
    try:
        p = Path(path)
        if not p.is_absolute():
            p = BASE_DIR / p
        
        # Verify file exists
        if p.exists():
            print(f"Enqueuing audio: {p}")
            _audio_q.put(p)
        else:
            print(f"Audio file not found: {p}")
            
    except Exception as e:
        print(f"Error enqueuing audio: {e}")

class TaskItem(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    is_complete = BooleanProperty(False)
    finished_audio = StringProperty(None)
    next_audio = StringProperty(None)

    def on_press(self):
        new_val = not self.is_complete
        self.is_complete = new_val
        if new_val:
            app = App.get_running_app()
            app.root.handle_task_completion(self)

    # on_checkbox_active removed as CheckBox is now display-only

import pygame

class RoboBuddyRoot(BoxLayout):
    current_period = StringProperty("Morning")
    current_time = StringProperty("")
    task_list = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_tasks()
        self.set_period_by_time()
        self.update_time(0)
        Clock.schedule_interval(self.update_time, 1)
        
        # Initialize pygame and joystick for controller support
        try:
            pygame.init()
            pygame.joystick.init()
            self.joystick = None
            print(f"Pygame initialized. Controllers currently detected: {pygame.joystick.get_count()}")
        except Exception as e:
            self.joystick = None
            print(f"Error initializing pygame joystick: {e}")
            
        Clock.schedule_interval(self.check_controller_events, 0.1)

    def check_controller_events(self, dt):
        if not pygame.joystick.get_init():
            return
            
        try:
            # Pumping the events is required to get joystick state
            pygame.event.pump()
            
            # Manual Hot-plug polling (more reliable than pygame 2+ events sometimes)
            count = pygame.joystick.get_count()
            if count > 0 and self.joystick is None:
                try:
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()
                    print(f"Controller connected: {self.joystick.get_name()}")
                except Exception as e:
                    print(f"Failed to connect controller: {e}")
            elif count == 0 and self.joystick is not None:
                print("Controller disconnected.")
                self.joystick.quit()
                self.joystick = None

            for event in pygame.event.get():
                if event.type == pygame.JOYHATMOTION:
                    # D-Pad (Hat) Event to announce NEXT task
                    if event.value != (0, 0): # D-Pad was pressed in any direction
                        # In Kivy, BoxLayout children are added such that children[0] is the bottom, and children[-1] is the top.
                        # Using reversed() gets them from top-to-bottom as displayed.
                        tasks_list = list(reversed(self.ids.task_container.children))
                        
                        last_completed_task = None
                        first_incomplete_task = None
                        
                        for task in tasks_list:
                            if task.is_complete:
                                last_completed_task = task
                            else:
                                first_incomplete_task = task
                                break
                        
                        # If we have a completed task, its 'next_audio' points to the current task
                        if last_completed_task and last_completed_task.next_audio:
                            print(f"D-Pad found next task via previous task's next_audio: {last_completed_task.next_audio}")
                            enqueue_audio(last_completed_task.next_audio)
                        # If no tasks are completed yet, the current 'next_audio' structure doesn't have an audio file for the very first task.
                        # Instead of playing 'finished_audio' (which wrongly says you completed it), we play the startup sound or nothing.
                        elif first_incomplete_task:
                            print(f"D-Pad found very first task: {first_incomplete_task.text}. Playing startup sound as fallback.")
                            enqueue_audio("ElevenLabs_2026-02-22T01_49_37_RoboBuddy_startup.wav")
                                
                elif event.type == pygame.JOYBUTTONDOWN:
                    print(f"DEBUG: Controller Button Pressed: {event.button}") # This will help identify the "T" button
                    
                    # Standard mapping: A=0, B=1, X=2, Y=3
                    if event.button == 0:  # A button
                        self.ids.btn_left.state = 'down'
                        self.turn_left()
                    elif event.button == 1:  # B button
                        self.ids.btn_right.state = 'down'
                        self.turn_right()
                    elif event.button == 2:  # X button
                        self.ids.btn_forward.state = 'down'
                        self.move_forward()
                    elif event.button == 3:  # Y button
                        self.ids.btn_backward.state = 'down'
                        self.move_backward()
                    elif event.button == 7: # Changed from 8 to 7 (Start/Menu button on Xbox layout)
                        # 'T' Button / Start Button to COMPLETE current task
                        for task in reversed(self.ids.task_container.children):
                            if not task.is_complete:
                                print(f"Start/T button pressed: Completing task -> {task.text}")
                                task.is_complete = True
                                self.handle_task_completion(task)
                                break # Only complete the first incomplete task
                    
                    # L1, L2, R1, R2 buttons to UNDO (uncheck) the last completed task.
                    # Commonly, L1=4, R1=5, L2/View=6. We map multiple common shoulder button IDs just in case.
                    elif event.button in [4, 5, 6, 9, 10]:
                        print(f"Shoulder button {event.button} pressed: Undoing last task")
                        # We need to find the LAST completed task.
                        # Since children are stored bottom-to-top, reversed() gets them top-to-bottom.
                        tasks_list = list(reversed(self.ids.task_container.children))
                        last_completed_task = None
                        
                        for task in tasks_list:
                            if task.is_complete:
                                last_completed_task = task
                            else:
                                break # Stop at the first incomplete task
                                
                        if last_completed_task:
                            print(f"Undoing task -> {last_completed_task.text}")
                            last_completed_task.is_complete = False

                # Some controllers map L2/R2 as axes instead of buttons
                elif event.type == pygame.JOYAXISMOTION:
                    # Triggers are often axes 2, 4, or 5 depending on OS and controller
                    # We check if the axis is pressed more than halfway (0.5)
                    if event.axis in [2, 4, 5] and event.value > 0.5:
                        # Prevent rapid-fire undoing from a single trigger pull
                        if not hasattr(self, '_last_trigger_undo') or (datetime.now() - getattr(self, '_last_trigger_undo')).total_seconds() > 0.5:
                            self._last_trigger_undo = datetime.now()
                            print(f"Trigger axis {event.axis} pulled: Undoing last task")
                            tasks_list = list(reversed(self.ids.task_container.children))
                            last_completed_task = None
                            for task in tasks_list:
                                if task.is_complete:
                                    last_completed_task = task
                                else:
                                    break
                            if last_completed_task:
                                print(f"Undoing task -> {last_completed_task.text}")
                                last_completed_task.is_complete = False

                elif event.type == pygame.JOYBUTTONUP:
                    if event.button in (0, 1, 2, 3):
                        self.ids.btn_left.state = 'normal'
                        self.ids.btn_right.state = 'normal'
                        self.ids.btn_forward.state = 'normal'
                        self.ids.btn_backward.state = 'normal'
                        self.stop_motors()
        except Exception as e:
            print(f"Error reading controller: {e}")

    def update_time(self, dt):
        self.current_time = datetime.now().strftime("%b %d %Y, %I:%M %p")

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as f:
                self.all_tasks = json.load(f)
        except FileNotFoundError:
            self.all_tasks = {"Morning": [], "Afternoon": [], "Night": []}

    def set_period_by_time(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            self.switch_period("Morning")
        elif 12 <= hour < 18:
            self.switch_period("Afternoon")
        else:
            self.switch_period("Night")

    def switch_period(self, period):
        self.current_period = period
        self.ids.task_container.clear_widgets()
        tasks = self.all_tasks.get(period, [])
        for task_data in tasks:
            # Handle both old string format and new dict format for backward compatibility
            if isinstance(task_data, str):
                task_text = task_data
                finished_audio = None
                next_audio = None
            else:
                task_text = task_data.get("text", "")
                finished_audio = task_data.get("finished_audio")
                next_audio = task_data.get("next_audio")
            
            task_item = TaskItem(
                text=task_text,
                finished_audio=finished_audio,
                next_audio=next_audio
            )
            self.ids.task_container.add_widget(task_item)

    def handle_task_completion(self, task_item):
        # schedule so the touch event finishes first
        Clock.schedule_once(lambda dt: enqueue_audio(task_item.finished_audio), 0)
        if task_item.next_audio:
            Clock.schedule_once(lambda dt: enqueue_audio(task_item.next_audio), 0)

    def play_next_audio(self, next_audio_path):
        Clock.schedule_once(lambda dt: enqueue_audio(next_audio_path), 0)

    # --- Motor Control Methods ---
    def move_forward(self):
        print("Moving Forward")
        enqueue_audio("ElevenLabs_2026-02-25T03_22_52_RoboBuddy_Going_north.wav")
        motor_left.forward()
        motor_right.forward()

    def move_backward(self):
        print("Moving Backward")
        enqueue_audio("ElevenLabs_2026-02-25T03_23_14_RoboBuddy_Going_south.wav")
        motor_left.backward()
        motor_right.backward()

    def turn_left(self):
        print("Spinning Left")
        enqueue_audio("ElevenLabs_2026-02-25T03_22_33_RoboBuddy_Turning_left.wav")
        motor_left.backward()
        motor_right.forward()

    def turn_right(self):
        print("Spinning Right")
        enqueue_audio("ElevenLabs_2026-02-25T03_22_12_RoboBuddy_Turning_right.wav")
        motor_left.forward()
        motor_right.backward()

    def stop_motors(self):
        print("Stopping Motors")
        motor_left.stop()
        motor_right.stop()
    # -----------------------------

class RoboBuddyApp(App):
    def build(self):
        return RoboBuddyRoot()

if __name__ == '__main__':
    RoboBuddyApp().run()
