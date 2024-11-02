import json
import asyncio
import threading
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
        self.is_dragging = False  # Track the drag/release state

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

        # Drag/Release toggle button
        self.drag_button = Button(text="Drag")
        self.drag_button.bind(on_press=self.toggle_drag_release)
        layout.add_widget(self.drag_button)

        # Add Refresh Connection button
        self.refresh_button = Button(text="Refresh Connection")
        self.refresh_button.bind(on_press=self.refresh_connection)
        layout.add_widget(self.refresh_button)

        # Start WebSocket connection in a separate thread
        threading.Thread(target=self.connect_to_server).start()

        # Schedule gyroscope data sending
        Clock.schedule_interval(self.send_position, 0.1)  # Send position every 100 ms

        return layout

    def connect_to_server(self):
        asyncio.run(self.websocket_handler())

    async def websocket_handler(self):
        try:
            # Replace with the server's IP address
            async with websockets.connect("ws://192.168.1.4:3000") as websocket:
                self.websocket = websocket
                self.connected = True
                self.update_status("Connected")
                await self.receive_messages()  # Listening to any messages from the server
        except Exception as e:
            self.update_status(f"Connection failed: {e}")
            self.connected = False

    def refresh_connection(self, instance):
        """Close existing connection and reconnect."""
        if self.connected:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), asyncio.get_event_loop())
            self.connected = False
        self.status_label.text = "Reconnecting..."
        threading.Thread(target=self.connect_to_server).start()

    def update_status(self, status):
        # Use Kivy’s Clock.schedule_once to safely update the label in the main thread
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', status), 0)

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
            # Send data in the WebSocket thread
            asyncio.run_coroutine_threadsafe(self.websocket.send(data), asyncio.get_event_loop())

    def send_click(self, click_type):
        if self.connected:
            data = json.dumps({"click": click_type})
            asyncio.run_coroutine_threadsafe(self.websocket.send(data), asyncio.get_event_loop())

    def toggle_drag_release(self, instance):
        """Toggle between drag and release states."""
        if self.connected:
            if self.is_dragging:
                # Send release command
                self.send_click("release")
                self.drag_button.text = "Drag"  # Change button text back to "Drag"
            else:
                # Send drag command
                self.send_click("drag")
                self.drag_button.text = "Release"  # Change button text to "Release"
            # Toggle the drag state
            self.is_dragging = not self.is_dragging

    async def receive_messages(self):
        try:
            async for message in self.websocket:
                print(f"Message from server: {message}")
        except websockets.exceptions.ConnectionClosed:
            self.update_status("Disconnected")

    async def on_stop(self):
        if self.connected:
            await self.websocket.close()

if __name__ == "__main__":
    AirMouseClientApp().run()
