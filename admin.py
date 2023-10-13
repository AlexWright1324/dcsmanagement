import asyncio
import websockets
import platform
import json
from shared import command_client_schema
from schema import SchemaError
import threading
import gi

import janus

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GLib

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="WebSocket Client")
        self.set_default_size(400, 300)
        self.connect("destroy", Gtk.main_quit)

        # Create the main VBox
        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)
        vbox.pack_start(self.stack, True, True, 0)

        login_page = Gtk.VBox(spacing=10)
        login_page.set_margin_top(30)
        login_page.set_margin_bottom(30)
        login_page.set_margin_start(30)
        login_page.set_margin_end(30)
        self.stack.add_titled(login_page, "login", "Login Page")
        label = Gtk.Label(label="Enter Password:")
        login_page.pack_start(label, False, False, 0)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        login_page.pack_start(self.password_entry, False, False, 0)
        self.connect_button = Gtk.Button(label="Connect")
        self.connect_button.connect("clicked", self.on_connect_clicked)
        login_page.pack_start(self.connect_button, False, False, 0)
        login_page.set_size_request(100, 100)

        clients_page = Gtk.HBox()
        self.stack.add_titled(clients_page, "clients", "Clients")
        self.liststore = Gtk.ListStore(str, str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.treeview.get_selection().connect("changed", self.on_client_selected)

        column = Gtk.TreeViewColumn("Clients")
        client = Gtk.CellRendererText()
        you = Gtk.CellRendererText()
        column.pack_start(client, True)
        column.add_attribute(client, "text", 0)

        column.pack_start(you, True)
        column.add_attribute(you, "text", 1)

        self.treeview.append_column(column)
        clients_page.pack_start(self.treeview, True, True, 0)

        button_box = Gtk.VBox(spacing=5)
        clients_page.pack_start(button_box, False, False, 0)
        self.logout_button = Gtk.Button(label="Logout")
        self.force_logout = Gtk.CheckButton(label="Force")
        logout_all_button = Gtk.Button(label="Logout All")
        self.logout_button.connect("clicked", self.on_logout_clicked)
        logout_all_button.connect("clicked", self.on_logout_clicked, True)
        button_box.pack_start(self.logout_button, False, False, 0)
        button_box.pack_start(self.force_logout, False, False, 0)
        button_box.pack_end(logout_all_button, False, False, 0)
        self.logout_button.set_sensitive(False)
        self.force_logout.set_sensitive(False)

    def start_async(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(connect_to_server(win))

    def on_connect_clicked(self, button):
        self.connect_button.set_sensitive(False)
        threading.Thread(target=self.start_async, daemon=True).start()

    def on_client_selected(self, selection):
        model, iter = selection.get_selected()
        if iter:
            _selected = model.get_value(iter, 0)
            self.logout_button.set_sensitive(True)
            self.force_logout.set_sensitive(True)
        else:
            self.logout_button.set_sensitive(False)
            self.force_logout.set_sensitive(False)

    def on_logout_clicked(self, button, all=False):
        selection = self.treeview.get_selection()
        (model, iter) = selection.get_selected()
        targets = []
        hostname = platform.node()
        if all:
            for row in model:
                if row[0] != hostname:
                    targets.append(row[0])
        elif iter:
                targets = [model.get_value(iter, 0)]
        if targets:
            data = {
                "targets": targets,
                "command": {
                    "command": "logout"
                }
            }
            if self.force_logout.get_active():
                data["command"]["args"] = ["force"]
            send_queue.sync_q.put(json.dumps(data))

    def update_clients(self, new):
        selection = self.treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter:
            selected = model.get_value(iter, 0)
            self.treeview.set_model(new)
            for row in new:
                if row[0] == selected:
                    iter = new.get_iter_from_string(row.path.to_string())
                    if iter:
                        selection.select_iter(iter)
                        self.treeview.scroll_to_cell(row.path, column=None, use_align=False, row_align=0.0, col_align=0.0)
                        break
        else:
            self.treeview.set_model(new)

async def recieve(websocket, win):
    async for message in websocket:
        try:
            data = json.loads(message)
            newlist = Gtk.ListStore(str, str)
            if "hostnames" in data:
                #data = hostname_schema.validate(data)
                for client in data["hostnames"]:
                    you = ""
                    if client == platform.node():
                        you = "(This PC)"
                    newlist.append([client, you])
                GLib.idle_add(win.update_clients, newlist)

        except json.JSONDecodeError as e:
            print("JSON Error: {e}")

        except SchemaError as e:
            print("Schema Error: {e}")

async def update_clients(websocket):
    while True:
        ls = {"command": {"command": "listclients"}}
        await websocket.send(json.dumps(ls))
        await asyncio.sleep(1)

class GtkAsyncRetrieve:
    def __init__(self, cmd, args=None):
        self.data = None
        self.cmd = cmd
        self.args = args

    def _retrieve_data(self):
        if self.args:
            self.data = self.cmd(*self.args)
        else:
            self.data = self.cmd()

    async def run(self):
        await asyncio.get_event_loop().run_in_executor(None, GLib.idle_add, self._retrieve_data)
        return self.data

async def send(websocket):
    while True:
        try:
            message = await send_queue.async_q.get()
            await websocket.send(message)
        except asyncio.QueueEmpty:
            pass
        await asyncio.sleep(0)

gather = None

async def connect_to_server(win):
    global send_queue, gather
    send_queue = janus.Queue()
    try:
        async with websockets.connect("ws://mc.uwcs.co.uk:3000") as websocket:
            msg = {
                "mode": "admin",
                "hostname": platform.node(),
                "password": await GtkAsyncRetrieve(win.password_entry.get_text).run()
            }
            await websocket.send(json.dumps(msg))

            authorised = await websocket.recv()
            if authorised == "authorised":#
                print("Connected to server")
                GLib.idle_add(win.stack.set_visible_child_name, "clients")
                gather = asyncio.gather(recieve(websocket, win), update_clients(websocket), send(websocket), )
                await gather
            else:
                print("Invalid password")

    except websockets.ConnectionClosedError:
        print("Connection to the server closed.")

    except Exception as e:
        print(f"Error: {e}")

    except asyncio.exceptions.CancelledError:
        return

    GLib.idle_add(win.connect_button.set_sensitive, True)
    GLib.idle_add(win.stack.set_visible_child_name, "login")

win = MyWindow()
win.show_all()

Gtk.main()

if gather:
    gather.cancel()
