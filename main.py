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
        layout.add_widget(Button(text="Drag/Release", on_press=self.toggle_drag_release))  # Combined button
        layout.add_widget(Button(text="Refresh Connection", on_press=self.refresh_connection))  # Refresh button

        # Connect to WebSocket
        Clock.schedule_once(lambda dt: asyncio.create_task(self.connect_to_server()), 1)  # Schedule connection
        Clock.schedule_interval(self.send_position, 0.1)  # Send position every 100 ms

        return layout

    async def connect_to_server(self):
        # Close any existing connection before establishing a new one
        if self.connected:
            await self.websocket.close()
            self.connected = False
            self.status_label.text = "Reconnecting..."

        try:
            # Replace with the server's IP address
            self.websocket = await websockets.connect("ws://192.168.1.4:3000")
            self.connected = True
            self.status_label.text = "Connected"
            print("WebSocket connection established.")
        except Exception as e:
            self.status_label.text = f"Connection failed: {e}"
            print(f"Failed to connect: {e}")

    def on_sensitivity_change(self, instance, value):
        self.sensitivity = value

    async def send_position_async(self):
        # Asynchronous position sending
        try:
            if self.connected and gyroscope.is_available():
                # Capture gyroscope data
                x, y = gyroscope.orientation[:2]  # Adjust based on your gyroscope API
                data = json.dumps({
                    "x": x * self.sensitivity,
                    "y": y * self.sensitivity
                })
                await self.websocket.send(data)  # Send data asynchronously
        except Exception as e:
            print(f"Error sending position data: {e}")
            self.status_label.text = "Connection lost"
            self.connected = False

    def send_position(self, dt):
        # Wrapper to handle asynchronous position sending
        if self.connected:
            asyncio.create_task(self.send_position_async())

    async def send_click_async(self, click_type):
        # Asynchronous click sending
        try:
            if self.connected:
                data = json.dumps({"click": click_type})
                await self.websocket.send(data)
        except Exception as e:
            print(f"Error sending click data: {e}")
            self.status_label.text = "Connection lost"
            self.connected = False

    def send_click(self, click_type):
        # Wrapper to handle asynchronous click sending
        asyncio.create_task(self.send_click_async(click_type))

    def toggle_drag_release(self, instance):
        # This toggles between drag and release with error handling
        if self.connected:
            # Schedule drag, then release after 100 ms
            asyncio.create_task(self.send_click_async("drag"))
            Clock.schedule_once(lambda dt: asyncio.create_task(self.send_click_async("release")), 0.1)

    def refresh_connection(self, instance):
        # Refresh connection by reconnecting
        self.status_label.text = "Reconnecting..."
        asyncio.create_task(self.connect_to_server())  # Reconnect

    async def on_stop(self):
        # Ensure WebSocket is closed on app stop
        if self.connected:
            await self.websocket.close()

if __name__ == "__main__":
    AirMouseClientApp().run()
