import asyncio
import json
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import gyroscope  # For accessing gyroscope data on Android
import websockets

class AirMouseClientApp(App):
    def build(self):
        self.sensitivity = 1.0
        self.connected = False
        self.websocket = None

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
        layout.add_widget(Button(text="Drag", on_press=lambda _: self.send_click("drag")))
        layout.add_widget(Button(text="Release", on_press=lambda _: self.send_click("release")))

        # Connect to WebSocket
        Clock.schedule_once(lambda dt: asyncio.run(self.connect_to_server()), 1)
        Clock.schedule_interval(self.send_position, 0.1)  # Send position every 100 ms

        return layout

    async def connect_to_server(self):
        try:
            # Replace with the server's IP address
            self.websocket = await websockets.connect("ws://192.168.1.4:3000")
            self.connected = True
            self.status_label.text = "Connected"
        except Exception as e:
            self.status_label.text = f"Connection failed: {e}"

    def on_sensitivity_change(self, instance, value):
        self.sensitivity = value

    def send_position(self, dt):
        if self.connected and gyroscope.is_available():
            # Capture gyroscope data
            x, y = gyroscope.orientation[:2]  # Adjust based on your gyroscope API
            data = json.dumps({
                "x": x * self.sensitivity,
                "y": y * self.sensitivity
            })
            asyncio.run(self.websocket.send(data))

    def send_click(self, click_type):
        if self.connected:
            data = json.dumps({"click": click_type})
            asyncio.run(self.websocket.send(data))

    async def on_stop(self):
        if self.connected:
            await self.websocket.close()

if __name__ == "__main__":
    AirMouseClientApp().run()
