import json
import subprocess
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import gyroscope  # For accessing gyroscope data on Android

class AirMouseClientApp(App):
    def build(self):
        self.sensitivity = 1.0
        self.connected = False

        # Build the layout
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text="Not connected", font_size=20)
        layout.add_widget(self.status_label)

        # Sensitivity control slider
        self.sensitivity_slider = Slider(min=0.5, max=3.0, value=1.0)
        self.sensitivity_slider.bind(value=self.on_sensitivity_change)
        layout.add_widget(self.sensitivity_slider)

        # Mouse action buttons
        layout.add_widget(Button(text="Left Click", on_press=lambda _: self.send_click("leftClick")))
        layout.add_widget(Button(text="Right Click", on_press=lambda _: self.send_click("rightClick")))
        layout.add_widget(Button(text="Drag/Release", on_press=self.toggle_drag_release))  # Combined button
        layout.add_widget(Button(text="Refresh Connection", on_press=self.refresh_connection))  # Refresh button

        # Schedule data sending
        Clock.schedule_interval(self.send_position, 0.1)

        return layout

    def on_sensitivity_change(self, instance, value):
        self.sensitivity = value

    def send_position(self, dt):
        if gyroscope.is_available():
            # Capture gyroscope data
            try:
                x, y = gyroscope.orientation[:2]
                data = f"{x * self.sensitivity},{y * self.sensitivity}"
                self.send_to_pc(data)
            except Exception as e:
                self.status_label.text = f"Gyro Error: {e}"

    def send_click(self, click_type):
        self.send_to_pc(f"CLICK:{click_type}")

    def toggle_drag_release(self, instance):
        self.send_to_pc("CLICK:drag")
        Clock.schedule_once(lambda dt: self.send_to_pc("CLICK:release"), 0.1)

    def refresh_connection(self, instance):
        self.status_label.text = "Refreshing connection..."
        # Add connection handling logic if necessary.

    def send_to_pc(self, data):
        try:
            subprocess.run(
                ["adb", "shell", f"echo {data} > /data/local/tmp/gyro_data"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except Exception as e:
            self.status_label.text = f"Send Error: {e}"

if __name__ == "__main__":
    AirMouseClientApp().run()
