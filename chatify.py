import customtkinter as ctk
from PIL import Image, ImageDraw
import sys
import json
import requests
from io import BytesIO
from functools import partial
import subprocess # To relaunch the login page
import os # To check for the logout icon

# --- Enhanced Color Palette ---
BG_COLOR = "#FFFFFF"
SIDEBAR_COLOR = "#FFFFFF"
CHAT_AREA_COLOR = "#F7F9FC"
PRIMARY_GREEN = "#07BC4C"
LIGHT_GREEN_HOVER = "#F1FAF5"
TEXT_COLOR = "#0F1111"
SECONDARY_TEXT_COLOR = "#565F64"
SENT_BUBBLE_COLOR = "#E6F8D8"
RECEIVED_BUBBLE_COLOR = "#FFFFFF"
BORDER_COLOR = "#E8ECEF"

class ChatifyApp(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()

        # --- APP SETUP ---
        self.user_data = user_data
        self.title("Chatify")
        self.geometry("1100x750")
        self.minsize(800, 600)
        ctk.set_appearance_mode("light")
        self.configure(fg_color=BG_COLOR)
        
        # List to hold message labels for dynamic resizing
        self.message_labels = []

        # --- LAYOUT CONFIGURATION for a responsive, proportional sidebar ---
        # The sidebar (column 0) now has a smaller minsize and a smaller
        # weight relative to the chat area (column 1).
        self.grid_columnconfigure(0, weight=1, minsize=300) 
        self.grid_columnconfigure(1, weight=3)              
        self.grid_rowconfigure(0, weight=1)

        # --- WIDGET CREATION ---
        self.create_sidebar()
        self.create_chat_area()
        self.show_placeholder() # Show the placeholder initially

    # --- UI STATE MANAGEMENT ---
    def show_placeholder(self):
        # Hide the main chat widgets and show the placeholder
        self.main_chat_frame.grid_remove()
        self.placeholder_frame.grid()

    def select_contact(self, contact_data, event=None):
        # Hide the placeholder and show the main chat widgets
        self.placeholder_frame.grid_remove()
        self.main_chat_frame.grid()

        # Update the top bar with the selected contact's info
        self.contact_name_label.configure(text=contact_data["name"])
        contact_avatar = self.load_image_from_url(contact_data.get("avatar_url"))
        self.contact_avatar_label.configure(image=contact_avatar)

        # Clear previous messages
        for widget in self.messages_area.winfo_children():
            widget.destroy()
        self.message_labels = []
        
        # --- Load and display new messages (using placeholder data for now) ---
        messages = [
            {"sender": "them", "text": f"This is a chat with {contact_data['name']}", "time": "10:30 AM"},
            {"sender": "me", "text": "Got it!", "time": "10:31 AM"},
        ]
        self.display_messages(messages)
        self.update_idletasks()
        self._on_chat_area_resize()
    
    def logout(self):
        """Closes the chat window and relaunches the login page."""
        self.destroy()
        # Use sys.executable to ensure we use the same python interpreter
        # that is running the current script.
        subprocess.Popen([sys.executable, "loginpage.py"])


    # --- DYNAMIC WRAPLENGTH CALLBACK ---
    def _on_chat_area_resize(self, event=None):
        width = event.width if event else self.messages_area.winfo_width()
        new_wraplength = width * 0.75
        if new_wraplength < 1: return

        for label in self.message_labels:
            label.configure(wraplength=new_wraplength)

    # --- UI HELPER METHODS ---
    def mask_image_to_circle(self, img_data, size):
        try:
            img = Image.open(BytesIO(img_data)).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
        except Exception:
            img = Image.new('RGBA', size, (220, 220, 220, 255))
        
        mask = Image.new('L', size, 0); draw = ImageDraw.Draw(mask); draw.ellipse((0, 0) + size, fill=255)
        output = Image.new('RGBA', size); output.paste(img, (0, 0), mask)
        return ctk.CTkImage(light_image=output, size=size)
        
    def load_image_from_url(self, url, size=(40, 40)):
        try:
            response = requests.get(url, timeout=5); response.raise_for_status()
            return self.mask_image_to_circle(response.content, size)
        except (requests.RequestException, IOError, TypeError):
            img = Image.new('RGBA', size, (220, 220, 220, 255))
            with BytesIO() as bio: img.save(bio, 'PNG'); img_bytes = bio.getvalue()
            return self.mask_image_to_circle(img_bytes, size)

    def display_messages(self, messages):
        for msg in messages:
            is_sent = msg["sender"] == "me"
            anchor = "e" if is_sent else "w"
            bubble_color = SENT_BUBBLE_COLOR if is_sent else RECEIVED_BUBBLE_COLOR
            
            message_container = ctk.CTkFrame(self.messages_area, fg_color="transparent")
            message_container.grid(sticky=anchor, padx=(0, 150) if not is_sent else (150, 0), pady=2)

            bubble = ctk.CTkFrame(message_container, fg_color=bubble_color, corner_radius=15); bubble.pack(anchor=anchor, pady=2)
            
            msg_label = ctk.CTkLabel(bubble, text=msg["text"], justify="left", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR)
            msg_label.pack(padx=15, pady=10)
            self.message_labels.append(msg_label)
            
            time_label = ctk.CTkLabel(message_container, text=msg["time"], font=ctk.CTkFont(size=10), text_color=SECONDARY_TEXT_COLOR); time_label.pack(anchor=anchor, padx=10, pady=(0, 5))

    # --- WIDGETS ---
    def create_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        sidebar_frame.grid(row=0, column=0, sticky="nswe")
        sidebar_frame.grid_rowconfigure(2, weight=1); sidebar_frame.grid_columnconfigure(0, weight=1)

        profile_frame = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
        profile_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=25)
        profile_frame.grid_columnconfigure(1, weight=1) # Make username label expand
        
        user_avatar = self.load_image_from_url(self.user_data.get("avatar_url"), size=(50, 50))
        avatar_label = ctk.CTkLabel(profile_frame, text="", image=user_avatar); avatar_label.grid(row=0, column=0, sticky="w")
        username_label = ctk.CTkLabel(profile_frame, text=self.user_data.get("username", "User"), font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_COLOR, anchor="w")
        username_label.grid(row=0, column=1, sticky="ew", padx=15)
        
        # --- LOGOUT BUTTON ---
        logout_icon_path = "logout.png"
        if os.path.exists(logout_icon_path):
            logout_image = ctk.CTkImage(Image.open(logout_icon_path).resize((24, 24), Image.Resampling.LANCZOS))
            logout_button = ctk.CTkButton(profile_frame, text="", image=logout_image, width=32, height=32,
                                          fg_color="transparent", hover_color=LIGHT_GREEN_HOVER, command=self.logout)
            logout_button.grid(row=0, column=2, sticky="e")
        else:
            print(f"Warning: '{logout_icon_path}' not found. Logout button will not be displayed.")


        search_frame = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search contacts...", height=40, corner_radius=12, fg_color=CHAT_AREA_COLOR, border_width=1, border_color=BORDER_COLOR)
        search_entry.pack(fill="x", expand=True)

        contacts_frame = ctk.CTkScrollableFrame(sidebar_frame, fg_color="transparent", scrollbar_button_color=PRIMARY_GREEN, scrollbar_button_hover_color=PRIMARY_GREEN)
        contacts_frame.grid(row=2, column=0, sticky="nswe", padx=10, pady=0)
        
        for i in range(10):
            contact_data = {"name": f"Contact {i+1}", "avatar_url": None, "id": i}
            contact_item_frame = ctk.CTkFrame(contacts_frame, fg_color="transparent", height=65, corner_radius=10, cursor="hand2")
            contact_item_frame.pack(fill="x", pady=2, padx=10)

            callback = partial(self.select_contact, contact_data)
            contact_item_frame.bind("<Button-1>", callback)

            def on_enter(e, frame=contact_item_frame): frame.configure(fg_color=LIGHT_GREEN_HOVER)
            def on_leave(e, frame=contact_item_frame): frame.configure(fg_color="transparent")
            contact_item_frame.bind("<Enter>", on_enter); contact_item_frame.bind("<Leave>", on_leave)

            contact_item_frame.grid_columnconfigure(1, weight=1)
            contact_avatar = self.load_image_from_url(None, size=(45,45))
            avatar = ctk.CTkLabel(contact_item_frame, text="", image=contact_avatar); avatar.grid(row=0, column=0, rowspan=2, padx=(10, 15), pady=10)
            username = ctk.CTkLabel(contact_item_frame, text=contact_data["name"], font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_COLOR, anchor="w"); username.grid(row=0, column=1, sticky="sew", pady=(15, 0))
            message = ctk.CTkLabel(contact_item_frame, text="Last message...", font=ctk.CTkFont(size=12), text_color=SECONDARY_TEXT_COLOR, anchor="w"); message.grid(row=1, column=1, sticky="new", pady=(0, 15))
            
            avatar.bind("<Button-1>", callback)
            username.bind("<Button-1>", callback)
            message.bind("<Button-1>", callback)


    def create_chat_area(self):
        # This frame is the main container for both the placeholder and the chat view
        container = ctk.CTkFrame(self, fg_color=CHAT_AREA_COLOR, corner_radius=0)
        container.grid(row=0, column=1, sticky="nswe")
        container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)

        # --- Placeholder Frame ---
        self.placeholder_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.placeholder_frame.grid(row=0, column=0, sticky="nswe")
        ctk.CTkLabel(self.placeholder_frame, text="Select a conversation to start chatting", font=ctk.CTkFont(size=18, weight="bold"), text_color=SECONDARY_TEXT_COLOR).pack(expand=True)

        # --- Main Chat Frame (initially hidden) ---
        self.main_chat_frame = ctk.CTkFrame(container, fg_color=CHAT_AREA_COLOR, corner_radius=0)
        self.main_chat_frame.grid(row=0, column=0, sticky="nswe")
        self.main_chat_frame.grid_rowconfigure(1, weight=1); self.main_chat_frame.grid_columnconfigure(0, weight=1)

        # Top Bar
        top_bar = ctk.CTkFrame(self.main_chat_frame, fg_color=SIDEBAR_COLOR, corner_radius=0, height=75, border_width=1, border_color=BORDER_COLOR); top_bar.grid(row=0, column=0, sticky="ew")
        self.contact_avatar_label = ctk.CTkLabel(top_bar, text=""); self.contact_avatar_label.pack(side="left", padx=20)
        self.contact_name_label = ctk.CTkLabel(top_bar, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR); self.contact_name_label.pack(side="left")
        
        # Message Display Area
        self.messages_area = ctk.CTkScrollableFrame(self.main_chat_frame, fg_color="transparent"); self.messages_area.grid(row=1, column=0, sticky="nswe", padx=20, pady=10); self.messages_area.grid_columnconfigure(0, weight=1)
        self.messages_area.bind("<Configure>", self._on_chat_area_resize)

        # Input Bar
        input_bar = ctk.CTkFrame(self.main_chat_frame, fg_color=SIDEBAR_COLOR, corner_radius=0, height=85, border_width=1, border_color=BORDER_COLOR); input_bar.grid(row=2, column=0, sticky="ew")
        message_entry = ctk.CTkEntry(input_bar, placeholder_text="Type a message...", height=45, fg_color=CHAT_AREA_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=15, font=ctk.CTkFont(size=14)); message_entry.pack(side="left", expand=True, fill="x", padx=20, pady=15)
        send_button = ctk.CTkButton(input_bar, text="➤", font=ctk.CTkFont(size=24), width=45, height=45, corner_radius=22.5, fg_color=PRIMARY_GREEN, hover_color="#06A542"); send_button.pack(side="right", padx=(0,20), pady=15)

if __name__ == "__main__":
    user_info = {"user_id": "test_id", "username": "Test User With a Longer Name", "avatar_url": None}
    if len(sys.argv) > 1:
        try: user_info = json.loads(sys.argv[1])
        except json.JSONDecodeError: print("Failed to decode user data.")
    
    app = ChatifyApp(user_data=user_info)
    app.mainloop()

