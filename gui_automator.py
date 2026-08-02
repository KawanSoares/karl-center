import customtkinter as ctk
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from automator import run_bulk_messages, split_messages
from version import VERSION


def _data_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self.window:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.window,
            text=self.text,
            background="#2a2a2a",
            foreground="#eeeeee",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3,
            font=("Segoe UI", 9),
        ).pack()

    def _hide(self, event=None):
        if self.window:
            self.window.destroy()
            self.window = None


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class WhatsAppAutomatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Karl Center - WhatsApp Bulk Messenger GUI v{VERSION}")
        self.geometry("800x950")
        self.running = False

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=2)
        self.grid_rowconfigure(5, weight=1)

        self.label_title = ctk.CTkLabel(
            self,
            text="☭ Karl Center - WhatsApp Bulk Sender",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.label_title.grid(row=0, column=0, columnspan=2, pady=20)

        self.label_msg = ctk.CTkLabel(self, text="Mensagens", anchor="w")
        self.label_msg.grid(row=1, column=0, padx=10, sticky="ew")

        self.label_nums = ctk.CTkLabel(
            self, text="Números (um por linha, com código do país)", anchor="w"
        )
        self.label_nums.grid(row=1, column=1, padx=10, sticky="ew")

        self.messages_container = ctk.CTkScrollableFrame(self, height=200)
        self.messages_container.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.messages_container.grid_columnconfigure(0, weight=1)
        self.message_items = []

        self.btn_add_message = ctk.CTkButton(
            self,
            text="+ Adicionar Mensagem",
            command=self.add_message_box,
            fg_color="#2a2a2a",
        )
        self.btn_add_message.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        Tooltip(self.btn_add_message, "Adicionar uma nova mensagem à sequência")

        self.textbox_nums = ctk.CTkTextbox(self, height=250)
        self.textbox_nums.grid(
            row=2, column=1, rowspan=2, padx=10, pady=5, sticky="nsew"
        )

        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.grid(
            row=4, column=0, columnspan=2, padx=20, pady=20, sticky="ew"
        )

        self.label_batch = ctk.CTkLabel(self.frame_settings, text="Limite de Envios:")
        self.label_batch.grid(row=0, column=0, padx=10, pady=10)
        self.entry_batch = ctk.CTkEntry(self.frame_settings, width=60)
        self.entry_batch.insert(0, "10")
        self.entry_batch.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(self.frame_settings, text="Delay entre Contatos (min/max):").grid(
            row=0, column=2, padx=10
        )
        self.entry_min = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_min.insert(0, "15")
        self.entry_min.grid(row=0, column=3, padx=5)

        self.entry_max = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_max.insert(0, "30")
        self.entry_max.grid(row=0, column=4, padx=5)

        ctk.CTkLabel(self.frame_settings, text="Delay entre Mensagens (min/max):").grid(
            row=1, column=2, padx=10, pady=(0, 10)
        )
        self.entry_msg_min = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_msg_min.insert(0, "5")
        self.entry_msg_min.grid(row=1, column=3, padx=5)

        self.entry_msg_max = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_msg_max.insert(0, "10")
        self.entry_msg_max.grid(row=1, column=4, padx=5)

        self.switch_reload = ctk.CTkSwitch(
            self.frame_settings,
            text="Recarregar WhatsApp a cada mensagem (mais confiável, porém mais lento)",
        )
        self.switch_reload.grid(
            row=2, column=0, columnspan=5, padx=10, pady=(0, 10), sticky="w"
        )
        Tooltip(
            self.switch_reload,
            "Ligado: recarrega o WhatsApp Web a cada mensagem (mais confiável).\n"
            "Desligado: digita direto na conversa aberta (mais rápido).",
        )

        self.log_view = ctk.CTkTextbox(
            self, height=250, state="disabled", fg_color="#1a1a1a", text_color="#00FF00"
        )
        self.log_view.grid(
            row=5, column=0, columnspan=2, padx=20, pady=10, sticky="nsew"
        )

        self.btn_start = ctk.CTkButton(
            self, text="INICIAR ENVIOS", command=self.start_thread, fg_color="#24a148"
        )
        self.btn_start.grid(row=6, column=0, columnspan=2, pady=20)
        Tooltip(self.btn_start, "Iniciar o envio das mensagens para todos os números")

        self.load_data()

    def add_message_box(self, initial_text="", attachment_path=None, insert_at=None):
        frame = ctk.CTkFrame(self.messages_container)
        frame.grid_columnconfigure(4, weight=1)

        item = {"frame": frame, "attachment_path": attachment_path}

        enabled_var = ctk.BooleanVar(value=True)
        item["enabled_var"] = enabled_var
        chk_enabled = ctk.CTkCheckBox(frame, text="", variable=enabled_var, width=20)
        chk_enabled.grid(row=0, column=0, padx=(5, 0), pady=5)
        Tooltip(chk_enabled, "Incluir/pular esta mensagem no envio")

        btn_up = ctk.CTkButton(
            frame, text="↑", width=28, command=lambda: self._move_item(item, -1)
        )
        btn_up.grid(row=0, column=1, padx=2)
        Tooltip(btn_up, "Mover para cima")

        btn_down = ctk.CTkButton(
            frame, text="↓", width=28, command=lambda: self._move_item(item, 1)
        )
        btn_down.grid(row=0, column=2, padx=2)
        Tooltip(btn_down, "Mover para baixo")

        btn_duplicate = ctk.CTkButton(
            frame, text="⧉", width=28, command=lambda: self._duplicate_item(item)
        )
        btn_duplicate.grid(row=0, column=3, padx=2)
        Tooltip(btn_duplicate, "Duplicar mensagem")

        attachment_label = ctk.CTkLabel(
            frame,
            text=os.path.basename(attachment_path) if attachment_path else "",
            anchor="w",
            text_color="#8ab4f8",
        )
        attachment_label.grid(row=0, column=4, padx=5, sticky="ew")
        item["attachment_label"] = attachment_label

        btn_attach = ctk.CTkButton(
            frame, text="📎", width=28, command=lambda: self._attach_file(item)
        )
        # TODO: re-grid once attachment sending works reliably (see
        # automator.py's _send_attachment)
        # btn_attach.grid(row=0, column=5, padx=2)
        Tooltip(btn_attach, "Anexar imagem ou documento")

        btn_clear_attach = ctk.CTkButton(
            frame,
            text="✕",
            width=28,
            fg_color="#5a2020",
            command=lambda: self._clear_attachment(item),
        )
        # TODO: re-grid once attachment sending works reliably (see
        # automator.py's _send_attachment)
        # btn_clear_attach.grid(row=0, column=6, padx=2)
        Tooltip(btn_clear_attach, "Remover anexo")

        btn_delete = ctk.CTkButton(
            frame,
            text="🗑",
            width=28,
            fg_color="#5a2020",
            command=lambda: self._delete_item(item),
        )
        btn_delete.grid(row=0, column=7, padx=(2, 5))
        Tooltip(btn_delete, "Excluir mensagem")

        textbox = ctk.CTkTextbox(frame, height=80)
        textbox.grid(row=1, column=0, columnspan=8, padx=5, pady=(0, 5), sticky="ew")
        if initial_text:
            textbox.insert("0.0", initial_text)
        item["textbox"] = textbox

        if insert_at is None:
            self.message_items.append(item)
        else:
            self.message_items.insert(insert_at, item)

        self._relayout_messages()

    def _relayout_messages(self):
        for i, item in enumerate(self.message_items):
            item["frame"].grid(row=i, column=0, padx=5, pady=5, sticky="ew")

    def _move_item(self, item, delta):
        idx = self.message_items.index(item)
        new_idx = idx + delta
        if 0 <= new_idx < len(self.message_items):
            self.message_items[idx], self.message_items[new_idx] = (
                self.message_items[new_idx],
                self.message_items[idx],
            )
            self._relayout_messages()

    def _duplicate_item(self, item):
        idx = self.message_items.index(item)
        text = item["textbox"].get("0.0", "end").strip()
        self.add_message_box(text, item["attachment_path"], insert_at=idx + 1)

    def _delete_item(self, item):
        item["frame"].destroy()
        self.message_items.remove(item)
        self._relayout_messages()

    def _attach_file(self, item):
        path = filedialog.askopenfilename(
            title="Selecionar imagem ou documento",
            filetypes=[
                (
                    "Imagens e Documentos",
                    "*.png *.jpg *.jpeg *.gif *.webp *.pdf *.doc *.docx *.xls *.xlsx",
                ),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if path:
            item["attachment_path"] = path
            item["attachment_label"].configure(text=os.path.basename(path))

    def _clear_attachment(self, item):
        item["attachment_path"] = None
        item["attachment_label"].configure(text="")

    def load_data(self):
        base = _data_dir()

        msg_path = os.path.join(base, "message.txt")
        chunks = []
        if os.path.exists(msg_path):
            with open(msg_path, "r", encoding="utf-8") as f:
                chunks = split_messages(f.read())
        for chunk in chunks or [""]:
            self.add_message_box(chunk)

        nums_path = os.path.join(base, "numbers.txt")
        if os.path.exists(nums_path):
            with open(nums_path, "r", encoding="utf-8") as f:
                self.textbox_nums.insert("0.0", f.read())

    def update_log_gui(self, text):
        self.log_view.configure(state="normal")
        self.log_view.insert("end", f"{text}\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def start_thread(self):
        if not self.running:
            self.running = True
            msgs = [
                {
                    "text": item["textbox"].get("0.0", "end").strip(),
                    "attachment": item["attachment_path"],
                }
                for item in self.message_items
                if item["enabled_var"].get()
                and (
                    item["textbox"].get("0.0", "end").strip() or item["attachment_path"]
                )
            ]
            nums = [
                n.strip()
                for n in self.textbox_nums.get("0.0", "end").split("\n")
                if n.strip()
            ]

            args = (
                nums,
                msgs,
                int(self.entry_batch.get()),
                int(self.entry_min.get()),
                int(self.entry_max.get()),
                int(self.entry_msg_min.get()),
                int(self.entry_msg_max.get()),
                bool(self.switch_reload.get()),
            )
            thread = threading.Thread(target=self.execute, args=args, daemon=True)
            thread.start()

    def execute(
        self, nums, msgs, batch, contact_min, contact_max, msg_min, msg_max, reload
    ):
        run_bulk_messages(
            nums,
            msgs,
            batch,
            contact_min,
            contact_max,
            msg_min,
            msg_max,
            reload_between_messages=reload,
            log_callback=self.update_log_gui,
        )
        self.running = False
        self.btn_start.configure(text="INICIAR ENVIOS")


if __name__ == "__main__":
    app = WhatsAppAutomatorGUI()
    app.mainloop()
