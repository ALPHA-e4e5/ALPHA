import json
import threading
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import gyroscope  # For accessing gyroscope data on Android
import websockets
import time

class AirMouseClientApp(App):
    def build(self):
        self.sensitivity = 1.0
        self.connected = False
        self.websocket = None
        self.websocket_thread = None
        self.should_stop = False

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

        # Start WebSocket connection thread
        self.start_websocket_connection()

        # Schedule position sending every 100 ms
        Clock.schedule_interval(self.send_position, 0.1)  

        return layout

    def start_websocket_connection(self):
        # Start a new thread for the WebSocket connection
        self.should_stop = False
        self.websocket_thread = threading.Thread(target=self.connect_to_server)
        self.websocket_thread.start()

    def connect_to_server(self):
        # Connect to the WebSocket server
        try:
            self.websocket = websockets.connect("ws://192.168.1.4:3000")
            self.connected = True
            self.status_label.text = "Connected"
            print("WebSocket connection established.")
        except Exception as e:
            self.status_label.text = f"Connection failed: {e}"
            print(f"Failed to connect: {e}")
            self.connected = False

    def on_sensitivity_change(self, instance, value):
        self.sensitivity = value

    def send_position(self, dt):
        if self.connected and gyroscope.is_available():
            try:
                # Capture gyroscope data
                x, y = gyroscope.orientation[:2]
                data = json.dumps({
                    "x": x * self.sensitivity,
                    "y": y * self.sensitivity
                })
                # Send position data in a separate thread
                threading.Thread(target=self.send_data, args=(data,)).start()
            except Exception as e:
                print(f"Error sending position data: {e}")
                self.status_label.text = "Connection lost"
                self.connected = False

    def send_click(self, click_type):
        # Send click data in a separate thread
        if self.connected:
            data = json.dumps({"click": click_type})
            threading.Thread(target=self.send_data, args=(data,)).start()

    def toggle_drag_release(self, instance):
        # Send drag command, then release after 100 ms
        if self.connected:
            self.send_click("drag")
            time.sleep(0.1)  # Small delay
            self.send_click("release")

    def send_data(self, data):
        # Thread-safe sending of data through WebSocket
        if self.websocket and self.connected:
            try:
                self.websocket.send(data)
            except Exception as e:
                print(f"Error sending data: {e}")
                self.status_label.text = "Connection lost"
                self.connected = False

    def refresh_connection(self, instance):
        # Refresh connection by stopping the current thread and starting a new one
        self.connected = False
        self.should_stop = True
        if self.websocket_thread and self.websocket_thread.is_alive():
            self.websocket_thread.join()
        self.start_websocket_connection()

    def on_stop(self):
        # Ensure WebSocket is closed on app stop
        self.should_stop = True
        if self.connected:
            self.websocket.close()

if __name__ == "__main__":
    AirMouseClientApp().run()
