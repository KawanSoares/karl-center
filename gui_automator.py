import customtkinter as ctk
import os
import threading
from automator import run_bulk_messages

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class WhatsAppAutomatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kalr Center - WhatsApp Bulk Messenger GUI")
        self.geometry("800x800")
        self.running = False


        self.grid_columnconfigure((0,1), weight=1)

        self.label_title = ctk.CTkLabel(self, text="☭ Kalr Center - WhatsApp Bulk Sender", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, columnspan=2, pady=20)

        self.textbox_msg = ctk.CTkTextbox(self, height=200)
        self.textbox_msg.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.textbox_nums = ctk.CTkTextbox(self, height=200)
        self.textbox_nums.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")


        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.label_batch = ctk.CTkLabel(self.frame_settings, text="Limite de Envios:")
        self.label_batch.grid(row=0, column=0, padx=10, pady=10)
        self.entry_batch = ctk.CTkEntry(self.frame_settings, width=60)
        self.entry_batch.insert(0, "10")
        self.entry_batch.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(self.frame_settings, text="Delays (min/max):").grid(row=0, column=2, padx=10)
        self.entry_min = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_min.insert(0, "15")
        self.entry_min.grid(row=0, column=3, padx=5)

        self.entry_max = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_max.insert(0, "30")
        self.entry_max.grid(row=0, column=4, padx=5)

        self.log_view = ctk.CTkTextbox(self, height=250, state="disabled", fg_color="#1a1a1a", text_color="#00FF00")
        self.log_view.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.btn_start = ctk.CTkButton(self, text="INICIAR ENVIOS", command=self.start_thread, fg_color="#24a148")
        self.btn_start.grid(row=5, column=0, columnspan=2, pady=20)

        self.load_data()

    def load_data(self):
        if os.path.exists("message.txt"):
            with open("message.txt", "r", encoding="utf-8") as f: self.textbox_msg.insert("0.0", f.read())
        if os.path.exists("numbers.txt"):
            with open("numbers.txt", "r", encoding="utf-8") as f: self.textbox_nums.insert("0.0", f.read())

    def update_log_gui(self, text):
        self.log_view.configure(state="normal")
        self.log_view.insert("end", f"{text}\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def start_thread(self):
        if not self.running:
            self.running = True
            msg = self.textbox_msg.get("0.0", "end").strip()
            nums = [n.strip() for n in self.textbox_nums.get("0.0", "end").split('\n') if n.strip()]

            args = (nums, msg, int(self.entry_batch.get()), int(self.entry_min.get()), int(self.entry_max.get()))
            thread = threading.Thread(target=self.execute, args=args, daemon=True)
            thread.start()

    def execute(self, nums, msg, batch, min_d, max_d):
        run_bulk_messages(nums, msg, batch, min_d, max_d, log_callback=self.update_log_gui)
        self.running = False
        self.btn_start.configure(text="INICIAR ENVIOS")

if __name__ == "__main__":
    app = WhatsAppAutomatorGUI()
    app.mainloop()