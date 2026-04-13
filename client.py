import socket
import struct
import tkinter as tk
from tkinter import messagebox
import threading
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999
POLL_ID = 1             # ← set your poll ID here

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq_no = 1

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
BG          = "#0D0F14"
SURFACE     = "#161A23"
CARD        = "#1C2130"
BORDER      = "#252B3B"
ACCENT      = "#4F8EF7"
ACCENT_GLOW = "#3A6ED4"
SUCCESS     = "#30D090"
ERROR       = "#FF4D6D"
TEXT        = "#E8EBF5"
MUTED       = "#5A6280"
FONT_TITLE  = ("Courier New", 22, "bold")
FONT_LABEL  = ("Courier New", 10, "bold")
FONT_ENTRY  = ("Courier New", 11)
FONT_SMALL  = ("Courier New", 9)
FONT_BTN    = ("Courier New", 12, "bold")
FONT_STATUS = ("Courier New", 9)

# ─────────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────────
class FlatEntry(tk.Entry):
    def __init__(self, master, **kw):
        super().__init__(
            master,
            bg=BG, fg=TEXT, insertbackground=ACCENT,
            relief="flat", bd=0,
            font=FONT_ENTRY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT,
            **kw
        )

class FlatRadio(tk.Radiobutton):
    def __init__(self, master, **kw):
        super().__init__(
            master,
            bg=CARD, fg=TEXT, selectcolor=CARD,
            activebackground=CARD, activeforeground=ACCENT,
            font=FONT_ENTRY,
            bd=0, relief="flat",
            cursor="hand2",
            **kw
        )

class GlowButton(tk.Canvas):
    """Animated glowing submit button."""
    def __init__(self, master, text, command, **kw):
        super().__init__(master, height=46, highlightthickness=0, bg=SURFACE, **kw)
        self._text = text
        self._command = command
        self._hover = False
        self._disabled = False
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def configure(self, **kw):
        if "state" in kw:
            self._disabled = (kw.pop("state") == "disabled")
            self._draw()
        super().configure(**kw)

    def _draw(self, hover=False):
        self.delete("all")
        w = self.winfo_reqwidth() or 320
        if self._disabled:
            fill, outline, fg = BORDER, BORDER, MUTED
            label = "✔  VOTE CAST"
        else:
            fill    = ACCENT if hover else ACCENT_GLOW
            outline = ACCENT
            fg      = TEXT
            label   = self._text
        self.create_rectangle(0, 0, w, 46, fill=fill, outline=outline, width=1)
        self.create_text(w//2, 23, text=label, fill=fg,
                         font=FONT_BTN, anchor="center")

    def _on_enter(self, _):
        if self._disabled:
            return
        self._hover = True
        self.configure(width=self.winfo_width())
        self._draw(hover=True)
        self.config(cursor="hand2")

    def _on_leave(self, _):
        self._hover = False
        if not self._disabled:
            self._draw(hover=False)
        self.config(cursor="")

    def _on_click(self, _):
        if not self._disabled:
            self._command()


# ─────────────────────────────────────────────
#  LOGIC
# ─────────────────────────────────────────────
def send_vote():
    global seq_no

    cid_raw = client_id_entry.get().strip()
    if not cid_raw:
        flash_status("⚠  Enter your Client ID", ERROR)
        return

    try:
        client_id = int(cid_raw)
        poll_id   = POLL_ID
        choice    = choice_var.get()

        packet = struct.pack("!I H B I", client_id, poll_id, choice, seq_no)
        sock.sendto(packet, (SERVER_IP, SERVER_PORT))

        data, _ = sock.recvfrom(1024)
        ack_client, ack_poll, ack_seq, status = struct.unpack("!I H I B", data)

        flash_status(
            f"✔  VOTE RECORDED  ·  client {ack_client}  ·  poll {ack_poll}  ·  seq {ack_seq}",
            SUCCESS
        )
        seq_no += 1
        pulse_accent()

    except Exception as e:
        flash_status(f"✘  {e}", ERROR)


def flash_status(msg, color):
    status_var.set(msg)
    status_label.config(fg=color)


def pulse_accent():
    """Quick highlight pulse on the border strip."""
    def _pulse():
        for _ in range(3):
            accent_bar.config(bg=SUCCESS)
            time.sleep(0.12)
            accent_bar.config(bg=ACCENT)
            time.sleep(0.12)
    threading.Thread(target=_pulse, daemon=True).start()


# ─────────────────────────────────────────────
#  ROOT WINDOW
# ─────────────────────────────────────────────
root = tk.Tk()
root.title("UDP Voting Terminal")
root.geometry("420x560")
root.resizable(False, False)
root.configure(bg=BG)

# ── top accent bar ──────────────────────────
accent_bar = tk.Frame(root, bg=ACCENT, height=3)
accent_bar.pack(fill="x")

# ── header ──────────────────────────────────
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=28, pady=(22, 0))

tk.Label(header, text="VOTE TERMINAL", font=FONT_TITLE,
         bg=BG, fg=TEXT).pack(anchor="w")
tk.Label(header, text=f"→ {SERVER_IP}:{SERVER_PORT}  ·  poll #{POLL_ID}",
         font=FONT_SMALL, bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))

# ── separator ───────────────────────────────
tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=28, pady=14)

# ── card ────────────────────────────────────
card = tk.Frame(root, bg=CARD, padx=22, pady=22)
card.pack(fill="both", padx=28, pady=0)

def labeled_entry(parent, label_text, row):
    tk.Label(parent, text=label_text, font=FONT_LABEL,
             bg=CARD, fg=MUTED).grid(row=row, column=0, sticky="w", pady=(0, 4))
    e = FlatEntry(parent, width=22)
    e.grid(row=row+1, column=0, sticky="ew", ipady=8, pady=(0, 16))
    return e

card.columnconfigure(0, weight=1)

tk.Label(card, text="CLIENT ID", font=FONT_LABEL,
         bg=CARD, fg=MUTED).grid(row=0, column=0, sticky="w", pady=(0, 4))
client_id_entry = FlatEntry(card, width=22)
client_id_entry.grid(row=1, column=0, sticky="ew", ipady=8, pady=(0, 16))

tk.Label(card, text="YOUR CHOICE", font=FONT_LABEL,
         bg=CARD, fg=MUTED).grid(row=2, column=0, sticky="w", pady=(0, 8))

choice_var = tk.IntVar(value=1)
options_frame = tk.Frame(card, bg=CARD)
options_frame.grid(row=3, column=0, sticky="ew")

for i, label in enumerate(["Option A", "Option B", "Option C"]):
    rb = FlatRadio(options_frame, text=f"  {label}", variable=choice_var, value=i+1)
    rb.pack(anchor="w", pady=2)

# ── separator ───────────────────────────────
tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=28, pady=16)

# ── submit button ───────────────────────────
btn_frame = tk.Frame(root, bg=BG, padx=28)
btn_frame.pack(fill="x")

btn = GlowButton(btn_frame, text="SUBMIT VOTE", command=send_vote, width=364)
btn.pack()

# ── status strip ────────────────────────────
status_frame = tk.Frame(root, bg=SURFACE, padx=28, pady=12)
status_frame.pack(fill="x", pady=(16, 0))

status_var = tk.StringVar(value="◌  ready — awaiting input")
status_label = tk.Label(status_frame, textvariable=status_var,
                        font=FONT_STATUS, bg=SURFACE, fg=MUTED,
                        anchor="w")
status_label.pack(fill="x")

# ── bottom accent ───────────────────────────
tk.Frame(root, bg=BORDER, height=1).pack(fill="x", pady=(10, 0))
tk.Label(root, text=f"seq #{seq_no}  ·  udp/dgram",
         font=FONT_SMALL, bg=BG, fg=MUTED).pack(anchor="e", padx=28, pady=6)

root.mainloop()