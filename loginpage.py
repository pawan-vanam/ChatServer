import customtkinter as ctk
from PIL import Image, ImageDraw
from supabase import create_client, Client
from CTkMessagebox import CTkMessagebox
import os
from tkinter import filedialog
from tkcalendar import Calendar
from datetime import datetime
import subprocess
import sys
import json

# --- Supabase Configuration ---
SUPABASE_URL = "https://cxfblokxotpejgtuvrng.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN4ZmJsb2t4b3RwZWpndHV2cm5nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MjEyNzUsImV4cCI6MjA3Mjk5NzI3NX0.YnhlAV22vx3k8bZ6XTSbNWYKyfJoTqGXD6kvNBrD3X8"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # --- App Setup ---
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self.title("Chatify")
        self.geometry("550x750")
        self.resizable(True, True)
        self.minsize(550, 750)
        self.configure(fg_color="#F5F7FA")

        # --- State Management ---
        self.current_session = None
        self.avatar_filepath = None

        # --- Supabase Initialization ---
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to connect to backend: {e}", icon="cancel")
            self.destroy()
            return

        # --- Load Assets ---
        placeholder_img = Image.new('RGBA', (128, 128), (200, 200, 200, 255))
        self.default_avatar_img = self.mask_image_to_circle(placeholder_img)
        self.default_avatar = ctk.CTkImage(light_image=self.default_avatar_img, size=(128, 128))

        self.eye_on_icon = ctk.CTkImage(light_image=Image.open("eye.png"), size=(24, 24))
        self.eye_off_icon = ctk.CTkImage(light_image=Image.open("eye-off.png"), size=(24, 24))

        # --- Main Frames ---
        self.login_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20)
        self.signup_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20)
        self.profile_setup_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20)
        
        # This frame is no longer used but kept to prevent errors if referenced
        self.chat_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20)


        # --- Create all UI elements ---
        self.create_login_frame()
        self.create_signup_frame()
        self.create_profile_setup_frame()

        self.show_login()

    # --- PAGE NAVIGATION ---
    def show_login(self):
        self.hide_all_frames()
        self.login_frame.pack(expand=True, ipadx=70, ipady=50)

    def show_signup(self):
        self.hide_all_frames()
        self.signup_frame.pack(expand=True, ipadx=70, ipady=50)

    def show_profile_setup(self):
        self.hide_all_frames()
        self.profile_setup_frame.pack(expand=True, ipadx=70, ipady=50)

    def launch_chat_app(self):
        """Launches the main chat application and closes the login window."""
        user_id = self.current_session.user.id
        profile_res = self.supabase.table('profiles').select("username, avatar_url").eq('id', user_id).single().execute()
        
        user_data = {
            "user_id": user_id,
            "username": "User",
            "avatar_url": None
        }

        if profile_res.data:
            user_data["username"] = profile_res.data.get('username')
            user_data["avatar_url"] = profile_res.data.get('avatar_url')

        user_data_json = json.dumps(user_data)

        try:
            # sys.executable is the path to the current Python interpreter
            subprocess.Popen([sys.executable, 'chatify.py', user_data_json])
            self.destroy() # Close the login window
        except FileNotFoundError:
            CTkMessagebox(title="Error", message="chatify.py not found. Make sure it's in the same directory.", icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Could not launch chat application: {e}", icon="cancel")


    def show_chat_page(self):
        print("Login successful. Launching chat app...")
        self.launch_chat_app()


    def hide_all_frames(self):
        for frame in [self.login_frame, self.signup_frame, self.profile_setup_frame]:
            frame.pack_forget()

    # --- UI HELPERS ---
    def toggle_password(self, entry, btn):
        if entry.cget("show") == "*":
            entry.configure(show="")
            btn.configure(image=self.eye_off_icon)
        else:
            entry.configure(show="*")
            btn.configure(image=self.eye_on_icon)

    def mask_image_to_circle(self, img):
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img.size, fill=255)
        output = Image.new('RGBA', img.size)
        output.paste(img, (0, 0), mask)
        return output

    # --- WIDGET CREATION ---
    def create_login_frame(self):
        header_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        header_frame.pack(pady=(20, 20))
        ctk.CTkLabel(header_frame, text="Welcome to Chatify", font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"), text_color="#2E7D32").pack()
        ctk.CTkLabel(header_frame, text="Sign in to start chatting", font=ctk.CTkFont(family="Helvetica", size=18), text_color="#4CAF50").pack(pady=(5,0))
        email_frame = ctk.CTkFrame(self.login_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#B0BEC5")
        email_frame.pack(pady=20, padx=20, fill="x")
        self.login_email_entry = ctk.CTkEntry(email_frame, placeholder_text="Email or Username", height=50, corner_radius=10, border_width=0, fg_color="#FFFFFF", text_color="#212121", font=ctk.CTkFont(size=14))
        self.login_email_entry.pack(pady=5, padx=10, expand=True, fill="x")
        password_frame = ctk.CTkFrame(self.login_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#B0BEC5")
        password_frame.pack(pady=20, padx=20, fill="x")
        self.login_password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", height=50, corner_radius=10, border_width=0, fg_color="#FFFFFF", text_color="#212121", font=ctk.CTkFont(size=14))
        toggle_btn = ctk.CTkButton(password_frame, text="", image=self.eye_on_icon, width=32, height=32, corner_radius=10, fg_color="transparent", hover_color="#E0E0E0", command=lambda: self.toggle_password(self.login_password_entry, toggle_btn))
        toggle_btn.pack(side="right", padx=(0, 10), pady=10)
        self.login_password_entry.pack(side="left", pady=10, padx=10, expand=True, fill="x")
        ctk.CTkButton(self.login_frame, text="Sign In", height=50, corner_radius=12, fg_color="#4CAF50", hover_color="#388E3C", font=ctk.CTkFont(size=18, weight="bold"), command=self.login_action).pack(pady=25, padx=20, fill="x")
        switch_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        switch_frame.pack(pady=10)
        ctk.CTkLabel(switch_frame, text="Don't have an account? ", font=ctk.CTkFont(size=16), text_color="#616161").pack(side="left")
        signup_link = ctk.CTkLabel(switch_frame, text="Sign Up", font=ctk.CTkFont(size=16, weight="bold"), text_color="#2E7D32", cursor="hand2")
        signup_link.pack(side="left")
        signup_link.bind("<Button-1>", lambda e: self.show_signup())

    def create_signup_frame(self):
        header_frame = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
        header_frame.pack(pady=(20, 20))
        ctk.CTkLabel(header_frame, text="Create your Account", font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"), text_color="#2E7D32").pack()
        ctk.CTkLabel(header_frame, text="Join the conversation", font=ctk.CTkFont(family="Helvetica", size=18), text_color="#4CAF50").pack(pady=(5,0))
        email_frame = ctk.CTkFrame(self.signup_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#B0BEC5")
        email_frame.pack(pady=15, padx=20, fill="x")
        self.signup_email_entry = ctk.CTkEntry(email_frame, placeholder_text="Email", height=50, corner_radius=10, border_width=0, fg_color="#FFFFFF", text_color="#212121", font=ctk.CTkFont(size=14))
        self.signup_email_entry.pack(pady=5, padx=10, expand=True, fill="x")
        username_frame = ctk.CTkFrame(self.signup_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#B0BEC5")
        username_frame.pack(pady=15, padx=20, fill="x")
        self.signup_username_entry = ctk.CTkEntry(username_frame, placeholder_text="Username", height=50, corner_radius=10, border_width=0, fg_color="#FFFFFF", text_color="#212121", font=ctk.CTkFont(size=14))
        self.signup_username_entry.pack(pady=5, padx=10, expand=True, fill="x")
        password_frame = ctk.CTkFrame(self.signup_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#B0BEC5")
        password_frame.pack(pady=15, padx=20, fill="x")
        self.signup_password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", height=50, corner_radius=10, border_width=0, fg_color="#FFFFFF", text_color="#212121", font=ctk.CTkFont(size=14))
        toggle_btn = ctk.CTkButton(password_frame, text="", image=self.eye_on_icon, width=32, height=32, corner_radius=10, fg_color="transparent", hover_color="#E0E0E0", command=lambda: self.toggle_password(self.signup_password_entry, toggle_btn))
        toggle_btn.pack(side="right", padx=(0, 10), pady=10)
        self.signup_password_entry.pack(side="left", pady=10, padx=10, expand=True, fill="x")
        ctk.CTkButton(self.signup_frame, text="Sign Up", height=50, corner_radius=12, fg_color="#4CAF50", hover_color="#388E3C", font=ctk.CTkFont(size=18, weight="bold"), command=self.signup_action).pack(pady=25, padx=20, fill="x")
        switch_frame = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
        switch_frame.pack(pady=10)
        ctk.CTkLabel(switch_frame, text="Already have an account? ", font=ctk.CTkFont(size=16), text_color="#616161").pack(side="left")
        login_link = ctk.CTkLabel(switch_frame, text="Sign In", font=ctk.CTkFont(size=16, weight="bold"), text_color="#2E7D32", cursor="hand2")
        login_link.pack(side="left")
        login_link.bind("<Button-1>", lambda e: self.show_login())
    
    def create_profile_setup_frame(self):
        header_frame = ctk.CTkFrame(self.profile_setup_frame, fg_color="transparent")
        header_frame.pack(pady=(20, 10))
        ctk.CTkLabel(header_frame, text="Set Up Your Profile", font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"), text_color="#2E7D32").pack()
        ctk.CTkLabel(header_frame, text="Add a few details to get started", font=ctk.CTkFont(family="Helvetica", size=18), text_color="#4CAF50").pack(pady=(5,0))

        avatar_frame = ctk.CTkFrame(self.profile_setup_frame, fg_color="transparent")
        avatar_frame.pack(pady=20)
        self.avatar_label = ctk.CTkLabel(avatar_frame, text="", image=self.default_avatar)
        self.avatar_label.pack()
        ctk.CTkButton(avatar_frame, text="Upload Image", command=self.upload_avatar_action, height=40, font=ctk.CTkFont(size=14)).pack(pady=(10,0))

        self.profile_username_entry = ctk.CTkEntry(self.profile_setup_frame, placeholder_text="Username", height=50, corner_radius=10, font=ctk.CTkFont(size=14))
        self.profile_username_entry.pack(pady=10, padx=20, fill="x")
        
        birthday_frame = ctk.CTkFrame(self.profile_setup_frame, fg_color="transparent")
        birthday_frame.pack(pady=10, padx=20, fill="x")
        self.profile_birthday_entry = ctk.CTkEntry(birthday_frame, placeholder_text="Birthday (DD-MM-YYYY)", height=50, corner_radius=10, font=ctk.CTkFont(size=14))
        self.profile_birthday_entry.pack(side="left", expand=True, fill="x")
        self.calendar_button = ctk.CTkButton(birthday_frame, text="📅", width=50, height=50, command=self.open_calendar, font=ctk.CTkFont(size=24))
        self.calendar_button.pack(side="left", padx=(10, 0))
        
        self.profile_phone_entry = ctk.CTkEntry(self.profile_setup_frame, placeholder_text="Phone Number", height=50, corner_radius=10, font=ctk.CTkFont(size=14))
        self.profile_phone_entry.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(self.profile_setup_frame, text="Save Profile", height=50, corner_radius=12, font=ctk.CTkFont(size=18, weight="bold"), command=self.save_profile_action).pack(pady=25, padx=20, fill="x")

    # --- ACTIONS ---
    def open_calendar(self):
        def on_date_select():
            selected_date = cal.get_date()
            self.profile_birthday_entry.delete(0, 'end')
            self.profile_birthday_entry.insert(0, selected_date)
            top.destroy()

        top = ctk.CTkToplevel(self)
        top.title("Select Birthday")
        top.geometry("350x350")
        top.transient(self); top.grab_set()

        cal = Calendar(top, selectmode='day', date_pattern='dd-MM-yyyy', background="white", foreground="black", headersbackground="#E0E0E0", normalbackground="#F5F5F5", weekendbackground="#F5F5F5", selectbackground="#4CAF50", selectforeground="white")
        cal.pack(pady=20, padx=20, expand=True, fill="both")
        ctk.CTkButton(top, text="Select", command=on_date_select).pack(pady=(0, 20))

    def login_action(self):
        identifier = self.login_email_entry.get(); password = self.login_password_entry.get()
        try:
            if '@' in identifier: res = self.supabase.auth.sign_in_with_password({"email": identifier, "password": password})
            else:
                profile_res = self.supabase.table('profiles').select("email").eq('username', identifier).execute()
                if not profile_res.data: CTkMessagebox(title="Error", message="Username not found.", icon="cancel"); return
                email = profile_res.data[0]['email']
                res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            self.current_session = res; user_id = self.current_session.user.id
            profile = self.supabase.table('profiles').select("*").eq('id', user_id).single().execute()
            if profile.data and profile.data.get('birth_date') is None:
                self.profile_username_entry.delete(0, 'end'); self.profile_username_entry.insert(0, profile.data.get('username', ''))
                self.show_profile_setup()
            else: self.show_chat_page()
        except Exception as e: CTkMessagebox(title="Login Failed", message=str(e), icon="cancel")
    
    def signup_action(self):
        email = self.signup_email_entry.get(); password = self.signup_password_entry.get(); username = self.signup_username_entry.get()
        if not all([email, password, username]): CTkMessagebox(title="Error", message="Please fill all fields.", icon="cancel"); return
        try:
            res = self.supabase.auth.sign_up({"email": email, "password": password, "options": {"data": { "username": username }}})
            CTkMessagebox(title="Signup Successful", message="Please check your email to confirm your account.", icon="check", option_1="OK"); self.show_login()
        except Exception as e: CTkMessagebox(title="Signup Failed", message=str(e), icon="cancel")

    def upload_avatar_action(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")]);
        if not filepath: return
        self.avatar_filepath = filepath
        img = Image.open(filepath).convert("RGB"); img.thumbnail((128, 128))
        circular_img = self.mask_image_to_circle(img)
        ctk_img = ctk.CTkImage(light_image=circular_img, size=(128, 128))
        self.avatar_label.configure(image=ctk_img)

    def save_profile_action(self):
        user_id = self.current_session.user.id
        username = self.profile_username_entry.get(); birth_date_str = self.profile_birthday_entry.get(); phone = self.profile_phone_entry.get()
        avatar_url = None
        if not username: CTkMessagebox(title="Error", message="Username cannot be empty.", icon="cancel"); return
        try:
            if self.avatar_filepath:
                file_ext = os.path.splitext(self.avatar_filepath)[1]
                storage_path = f"{user_id}/avatar{file_ext}"
                with open(self.avatar_filepath, 'rb') as f: file_content = f.read()
                try: self.supabase.storage.from_('avatars').remove([storage_path])
                except Exception: pass
                self.supabase.storage.from_('avatars').upload(path=storage_path, file=file_content, file_options={"content-type": f"image/{file_ext.replace('.', '')}"})
                avatar_url = self.supabase.storage.from_('avatars').get_public_url(storage_path)
            formatted_birth_date = None
            if birth_date_str:
                try:
                    date_obj = datetime.strptime(birth_date_str, '%d-%m-%Y')
                    formatted_birth_date = date_obj.strftime('%Y-%m-%d')
                except ValueError: CTkMessagebox(title="Error", message="Invalid birthday format.", icon="cancel"); return
            profile_data = {'username': username, 'birth_date': formatted_birth_date, 'phone': phone if phone else None}
            if avatar_url: profile_data['avatar_url'] = avatar_url
            self.supabase.table('profiles').update(profile_data).eq('id', user_id).execute()
            CTkMessagebox(title="Success", message="Profile saved successfully!", icon="check")
            self.show_chat_page()
        except Exception as e: CTkMessagebox(title="Error", message=f"Failed to save profile: {e}", icon="cancel")

if __name__ == "__main__":
    app = App()
    app.mainloop()

