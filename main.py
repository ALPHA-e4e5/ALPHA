import json
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import gyroscope
from android.storage import app_storage_path
from android.permissions import request_permissions, Permission, check_permission


class AirMouseClientApp(App):
    def build(self):
        # Request necessary permissions
        self.request_android_permissions()

        # Define gyro file path
        self.sensitivity = 1.0
        self.gyro_file_path = os.path.join(app_storage_path(), "gyro_data.json")

        # Create UI layout
        layout = BoxLayout(orientation="vertical")
        self.status_label = Label(text="Checking gyroscope...", font_size=20)
        layout.add_widget(self.status_label)

        # Sensitivity slider
        self.sensitivity_slider = Slider(min=0.5, max=3.0, value=1.0)
        self.sensitivity_slider.bind(value=self.on_sensitivity_change)
        layout.add_widget(self.sensitivity_slider)

        # Buttons
        layout.add_widget(Button(text="Left Click", on_press=lambda _: self.write_action("leftClick")))
        layout.add_widget(Button(text="Right Click", on_press=lambda _: self.write_action("rightClick")))
        layout.add_widget(Button(text="Drag/Release", on_press=lambda _: self.write_action("drag_release")))

        # Check gyroscope availability
        Clock.schedule_once(self.check_gyroscope, 1)
        Clock.schedule_interval(self.update_gyroscope, 0.1)

        return layout

    def request_android_permissions(self):
        """Request permissions required for the app."""
        permissions = [
            Permission.INTERNET,
            Permission.BODY_SENSORS,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
        ]
        request_permissions(permissions)
        for perm in permissions:
            if not check_permission(perm):
                raise Exception(f"Permission not granted: {perm}")

    def check_gyroscope(self, dt):
        """Check gyroscope availability."""
        try:
            if gyroscope.is_available():
                self.status_label.text = "Gyroscope is active!"
                gyroscope.enable()
            else:
                self.status_label.text = "Gyroscope unavailable."
        except Exception as e:
            self.status_label.text = f"Gyroscope error: {str(e)}"

    def on_sensitivity_change(self, instance, value):
        """Update sensitivity from slider."""
        self.sensitivity = value

    def update_gyroscope(self, dt):
        """Capture gyroscope data."""
        try:
            if gyroscope.is_available():
                x, y = gyroscope.orientation[:2]
                gyro_data = {
                    "x": x * self.sensitivity,
                    "y": y * self.sensitivity,
                }
                self.write_to_file(gyro_data)
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    def write_action(self, action):
        """Write action to the file."""
        action_data = {"action": action}
        self.write_to_file(action_data)

    def write_to_file(self, data):
        """Safely write data to the gyro file."""
        os.makedirs(os.path.dirname(self.gyro_file_path), exist_ok=True)
        try:
            with open(self.gyro_file_path, "w") as gyro_file:
                json.dump(data, gyro_file)
        except Exception as e:
            self.status_label.text = f"File error: {str(e)}"

    def on_stop(self):
        """Disable gyroscope on app stop."""
        if gyroscope.is_available():
            gyroscope.disable()


if __name__ == "__main__":
    AirMouseClientApp().run()
