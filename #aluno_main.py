# aluno_main.py 
import re
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

INSTITUTION_DOMAIN = "unip.br"
USERS_FILE = "usuarios.json"


# Validação com senha, email e RA
def is_valid_password(pw: str) -> bool:
    return bool(re.fullmatch(r"\d{5}", pw))


def is_valid_ra(ra: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9]{7}", ra))


def is_valid_email(email: str) -> bool:
    return bool(re.fullmatch(rf"[A-Za-z0-9._%+-]+@{re.escape(INSTITUTION_DOMAIN)}", email))


def is_valid_birthdate(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False


#Bilioteca JSON
def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_users(users: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# 
class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.default_fg = self.cget("foreground")
        self._has_placeholder = False
        self._put_placeholder()
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)

    def _put_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(foreground="#777")
            self._has_placeholder = True

    def _focus_in(self, _):
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.default_fg)
            self._has_placeholder = False

    def _focus_out(self, _):
        if not self.get():
            self._put_placeholder()

    def get_value(self):
        val = self.get()
        return "" if (self._has_placeholder or val == self.placeholder) else val


# Tela 
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tela de Aluno - Sistema")
        self.geometry("460x620")
        self.configure(bg="#C5E1DC")

        self.users = load_users()

        #Layout
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "TLabel",
            background="#C5E1DC",
            foreground="#222",
            font=("Helvetica", 10)
        )
        style.configure(
            "Title.TLabel",
            font=("Helvetica", 18, "bold"),
            background="#C5E1DC",
            foreground="#1B1B1B"
        )
        style.configure(
            "TEntry",
            padding=8,
            relief="flat",
            foreground="#000",
            fieldbackground="#9CC8B8"
        )
        style.map("TEntry", fieldbackground=[("active", "#2140A3")])
        style.configure(
            "TButton",
            background="#417F6A",
            foreground="white",
            font=("Helvetica", 11, "bold"),
            padding=8,
            borderwidth=0
        )
        style.map(
            "TButton",
            background=[("active", "#316D5C")],
            foreground=[("disabled", "#ccc")]
        )
        style.configure("Invalid.TEntry", fieldbackground="#2140A3")

        #Estrutura visual
        container = tk.Frame(self, bg="#2140A3")
        container.pack(fill="both", expand=True, pady=30)

        ttk.Label(container, text="Cadastro", style="Title.TLabel").pack(pady=(0, 10))

        self.mode = tk.StringVar(value="register")

        self.register_frame = self._build_register_frame(container)
        self.register_frame.pack(fill="both", expand=True, padx=30, pady=10)

    #Cadastro do aluno
    def _build_register_frame(self, parent):
        frame = tk.Frame(parent, bg="#2140A3")

        self.reg_nome = ttk.Entry(frame, width=35)
        self._placeholder_row(frame, "Nome completo", self.reg_nome).pack(pady=6)

        self.reg_ra = ttk.Entry(frame, width=35)
        self._placeholder_row(frame, "RA", self.reg_ra).pack(pady=6)

        self.reg_pw = ttk.Entry(frame, show="*", width=35)
        self._placeholder_row(frame, "Senha - 5 dígitos", self.reg_pw).pack(pady=6)

        ttk.Button(
            frame, text="Cadastrar", command=self._handle_register, style="TButton"
        ).pack(pady=(20, 0), fill="x")

        return frame

    #Layout simplificado
    def _placeholder_row(self, parent, placeholder, entry):
        row = tk.Frame(parent, bg="#C5E1DC")
        ph = PlaceholderEntry(row, placeholder=placeholder)
        ph.pack(fill="x", ipady=6)
        return row

    #Validação do cadastro e salvamento de dados em JSON
    def _handle_register(self):
        nome = self.reg_nome.get().strip()
        ra = self.reg_ra.get().strip()
        pw = self.reg_pw.get().strip()

        self._clear_field_style([self.reg_nome, self.reg_ra, self.reg_pw])

        errors = []
        if not nome:
            self._mark_invalid(self.reg_nome)
            errors.append("Informe o nome completo.")
        if not is_valid_ra(ra):
            self._mark_invalid(self.reg_ra)
            errors.append("RA deve ter exatamente 7 caracteres alfanuméricos.")
        if not is_valid_password(pw):
            self._mark_invalid(self.reg_pw)
            errors.append("Senha deve ter exatamente 5 dígitos numéricos.")
        if ra in self.users:
            errors.append("RA já cadastrado.")

        if errors:
            messagebox.showerror("Erro", "\n".join(errors))
            return

        self.users[ra] = {"nome": nome, "senha": pw}
        save_users(self.users)
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")

    # ---------- Helpers ----------
    def _mark_invalid(self, entry_widget):
        entry_widget.configure(style="Invalid.TEntry")

    def _clear_field_style(self, entries):
        for e in entries:
            try:
                e.configure(style="TEntry")
            except tk.TclError:
                pass


if __name__ == "__main__":
    app = App()
    app.mainloop()

