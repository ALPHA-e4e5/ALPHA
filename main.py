import json
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import gyroscope
from kivy.utils import platform

class AirMouseClientApp(App):
    def build(self):
        self.sensitivity = 1.0
        self.gyro_available = self.is_gyroscope_available()
        self.gyro_enabled = False
        self.data_file_path = self.get_data_file_path()

        # Build the layout
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text="Initializing...", font_size=20)
        layout.add_widget(self.status_label)

        # Sensitivity slider
        self.sensitivity_slider = Slider(min=0.5, max=3.0, value=1.0)
        self.sensitivity_slider.bind(value=self.on_sensitivity_change)
        layout.add_widget(Label(text="Sensitivity"))
        layout.add_widget(self.sensitivity_slider)

        # Mouse action buttons
        layout.add_widget(Button(text="Left Click", on_press=lambda _: self.send_click("leftClick")))
        layout.add_widget(Button(text="Right Click", on_press=lambda _: self.send_click("rightClick")))
        layout.add_widget(Button(text="Drag/Release", on_press=self.toggle_drag_release))

        # Initialize gyroscope
        if self.gyro_available:
            try:
                gyroscope.enable()
                self.gyro_enabled = True
                self.status_label.text = "Gyroscope enabled"
                Clock.schedule_interval(self.send_position, 0.1)  # Send position every 100ms
            except Exception as e:
                self.status_label.text = f"Error enabling gyroscope: {e}"
        else:
            self.status_label.text = "Gyroscope unavailable"

        return layout

    def is_gyroscope_available(self):
        """
        Check if the gyroscope is available on the device.
        """
        try:
            return gyroscope.is_available()
        except Exception as e:
            print(f"Error checking gyroscope availability: {e}")
            return False

    def get_data_file_path(self):
        """
        Get the path to the app's internal storage directory.
        """
        app_storage_dir = self.user_data_dir
        if not os.path.exists(app_storage_dir):
            os.makedirs(app_storage_dir)
        return os.path.join(app_storage_dir, "gyro_data.json")

    def on_sensitivity_change(self, instance, value):
        """
        Update the sensitivity factor based on slider value.
        """
        self.sensitivity = value

    def send_position(self, dt):
        """
        Capture and send gyroscope data to the PC.
        """
        if self.gyro_enabled:
            try:
                # Read gyroscope data
                x, y, _ = gyroscope.orientation
                data = {
                    "x": x * self.sensitivity,
                    "y": y * self.sensitivity
                }
                self.write_data_to_file(data)
            except Exception as e:
                print(f"Error reading gyroscope data: {e}")
                self.status_label.text = "Error reading gyroscope data"

    def send_click(self, click_type):
        """
        Send mouse click events to the PC.
        """
        try:
            data = {"click": click_type}
            self.write_data_to_file(data)
        except Exception as e:
            print(f"Error sending click event: {e}")

    def toggle_drag_release(self, instance):
        """
        Toggle drag and release actions.
        """
        try:
            # Send drag
            self.write_data_to_file({"click": "drag"})
            Clock.schedule_once(lambda dt: self.write_data_to_file({"click": "release"}), 0.1)  # Release after 100ms
        except Exception as e:
            print(f"Error sending drag/release event: {e}")

    def write_data_to_file(self, data):
        """
        Write data to the app's internal storage directory.
        """
        try:
            with open(self.data_file_path, "w") as f:
                f.write(json.dumps(data))
            print(f"Data written: {data}")
        except Exception as e:
            print(f"Error writing data to file: {e}")
            self.status_label.text = f"Error writing data: {e}"

    def on_stop(self):
        """
        Cleanup on app exit.
        """
        if self.gyro_enabled:
            try:
                gyroscope.disable()
            except Exception as e:
                print(f"Error disabling gyroscope: {e}")

if __name__ == "__main__":
    AirMouseClientApp().run()
