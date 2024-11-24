import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import gyroscope

class AirMouseClientApp(App):
    def build(self):
        self.sensitivity = 1.0
        self.drag_active = False
        self.usb_file_path = "/data/local/tmp/usb_input.txt"  # Path for USB communication

        # Build the layout
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text="Ready", font_size=20)
        layout.add_widget(self.status_label)

        # Sensitivity control slider
        self.sensitivity_slider = Slider(min=0.5, max=3.0, value=1.0)
        self.sensitivity_slider.bind(value=self.on_sensitivity_change)
        layout.add_widget(self.sensitivity_slider)

        # Mouse action buttons
        layout.add_widget(Button(text="Left Click", on_press=lambda _: self.send_click("leftClick")))
        layout.add_widget(Button(text="Right Click", on_press=lambda _: self.send_click("rightClick")))
        layout.add_widget(Button(text="Drag/Release", on_press=self.toggle_drag_release))  # Combined button
        layout.add_widget(Button(text="Refresh", on_press=self.refresh_connection))

        # Enable gyroscope
        try:
            gyroscope.enable()
        except Exception as e:
            print(f"Gyroscope initialization error: {e}")
            self.status_label.text = "Gyroscope unavailable"

        # Schedule sending position
        Clock.schedule_interval(self.send_position, 0.1)  # Every 100ms

        return layout

    def on_sensitivity_change(self, instance, value):
        self.sensitivity = value

    def send_position(self, dt):
        if self.is_gyroscope_available():
            try:
                x, y = gyroscope.orientation[:2]
                data = {
                    "x": x * self.sensitivity,
                    "y": y * self.sensitivity,
                    "action": "move"
                }
                self.write_to_usb(data)
            except Exception as e:
                print(f"Error sending position: {e}")
        else:
            self.status_label.text = "Gyroscope unavailable"

    def send_click(self, click_type):
        try:
            data = {"action": click_type}
            self.write_to_usb(data)
        except Exception as e:
            print(f"Error sending click: {e}")

    def toggle_drag_release(self, instance):
        try:
            action = "drag" if not self.drag_active else "release"
            data = {"action": action}
            self.write_to_usb(data)
            self.drag_active = not self.drag_active
        except Exception as e:
            print(f"Error toggling drag/release: {e}")

    def refresh_connection(self, instance):
        self.status_label.text = "Refreshing..."

    def is_gyroscope_available(self):
        try:
            return gyroscope.is_available()
        except Exception as e:
            print(f"Gyroscope check error: {e}")
            return False

    def write_to_usb(self, data):
        """
        Write data to a shared file that the PC script reads via USB.
        """
        try:
            with open(self.usb_file_path, "w") as usb_file:
                usb_file.write(json.dumps(data) + "\n")
            self.status_label.text = "Data sent"
        except Exception as e:
            self.status_label.text = "USB write error"
            print(f"USB write error: {e}")

if __name__ == "__main__":
    AirMouseClientApp().run()
