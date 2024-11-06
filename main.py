import asyncio
import json
from threading import Thread
from kivy.app import App
from kivy.uix.button import Button
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

        # Mouse action buttons
        layout.add_widget(Button(text="Left Click", on_press=lambda _: self.send_click("leftClick")))
        layout.add_widget(Button(text="Right Click", on_press=lambda _: self.send_click("rightClick")))
        layout.add_widget(Button(text="Drag/Release", on_press=self.toggle_drag_release))
        layout.add_widget(Button(text="Refresh Connection", on_press=self.refresh_connection))

        # Start a separate thread for WebSocket communication
        self.websocket_thread = Thread(target=self.start_websocket_loop, daemon=True)
        self.websocket_thread.start()

        # Schedule periodic sending of position
        Clock.schedule_interval(self.send_position, 0.1)

        return layout

    def start_websocket_loop(self):
        # Run the asyncio event loop in a separate thread
        asyncio.run(self.websocket_loop())

    async def websocket_loop(self):
        while True:
            if not self.connected:
                await self.connect_to_server()
            await asyncio.sleep(1)  # Prevent tight loop if not connected

    async def connect_to_server(self):
        try:
            # Replace with the server IP address
            self.websocket = await websockets.connect("ws://192.168.1.4:3000")
            self.connected = True
            self.update_status("Connected")
            print("WebSocket connection established.")
        except Exception as e:
            self.update_status(f"Connection failed: {e}")

    def update_status(self, message):
        # Update UI elements from the main thread
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', message))

    def send_position(self, dt):
        # Only try to send data if connected and gyroscope is available
        if self.connected and gyroscope.is_available():
            x, y = gyroscope.orientation[:2]  # Adjust based on your gyroscope API
            data = json.dumps({
                "x": x * self.sensitivity,
                "y": y * self.sensitivity
            })
            # Send position asynchronously
            asyncio.run_coroutine_threadsafe(self.websocket.send(data), asyncio.get_event_loop())

    def send_click(self, click_type):
        if self.connected:
            data = json.dumps({"click": click_type})
            asyncio.run_coroutine_threadsafe(self.websocket.send(data), asyncio.get_event_loop())

    def toggle_drag_release(self, instance):
        # Toggle between drag and release
        if self.connected:
            data = json.dumps({"click": "drag"})
            asyncio.run_coroutine_threadsafe(self.websocket.send(data), asyncio.get_event_loop())
            # Release after a short delay
            Clock.schedule_once(lambda dt: asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps({"click": "release"})), asyncio.get_event_loop()
            ), 0.1)

    def refresh_connection(self, instance):
        # Disconnect and reconnect
        self.connected = False
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), asyncio.get_event_loop())
        self.update_status("Reconnecting...")

    def on_stop(self):
        if self.connected and self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), asyncio.get_event_loop())

if __name__ == "__main__":
    AirMouseClientApp().run()
