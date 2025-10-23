# professor com cores
import re
import json
import os
import tkinter as tk
from tkinter import messagebox

#  Configurações
PROFESSOR_DOMAINS = ["prof.unip.br", "docente.unip.br"]
USERS_FILE = "professores.json"


# Validação de senha e email
  # senha com 5 dígitos
def is_valid_password(pw: str) -> bool:
    return bool(re.fullmatch(r"\d{5}", pw))

#email com @prof.unip.br
def is_valid_prof_email(email: str) -> bool:
    domains = "|".join(re.escape(d) for d in PROFESSOR_DOMAINS) 
    pattern = rf"^[A-Za-z0-9._%+-]+@(?:{domains})$"
    return bool(re.fullmatch(pattern, email))


# biblioteca JSON
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


#Criação de telas
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema - Tela de Professor")
        self.geometry("400x600")
        self.minsize(360, 520)
        self.configure(bg="#DCDDE1")  # fundo

        self.users = load_users()
        self.active_frame = None

        self._show_login()

    def _clear_screen(self):
        if self.active_frame:
            self.active_frame.destroy()
            self.active_frame = None

    def _show_login(self):
        self._clear_screen()
        self.active_frame = LoginFrame(
            self, self.users, on_go_register=self._show_register)
        self.active_frame.pack(expand=True, fill="both")

    def _show_register(self):
        self._clear_screen()
        self.active_frame = RegisterFrame(
            self, self.users, on_done=self._show_login)
        self.active_frame.pack(expand=True, fill="both")


#Frame de login
class LoginFrame(tk.Frame):
    def __init__(self, master, users, on_go_register):
        super().__init__(master, bg=master["bg"])
        self.master = master
        self.users = users
        self.on_go_register = on_go_register

        tk.Label(self, text="Login", font=("Arial", 24, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(60, 6))
        tk.Label(self, text="Acesse com seu e-mail institucional",
                 font=("Arial", 10), bg=self["bg"], fg="#242964").pack(pady=(0, 18))

        # E-mail
        self.email_entry = self._entry_with_placeholder(
            "E-mail institucional (prof)")
        self.email_entry.pack(pady=8, ipady=6)

        # Senha
        self.pw_entry = self._entry_with_placeholder(
            "Senha (5 dígitos)", is_password=True)
        self._attach_digit_limiter(self.pw_entry, max_len=5)
        self.pw_entry.pack(pady=8, ipady=6)

        # Botões
        tk.Button(
            self,
            text="Entrar",
            command=self._handle_login,
            bg="#6C5CE7",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            width=24,
            padx=6,
            pady=6
        ).pack(pady=(22, 10))

        tk.Label(self, text="Ainda não tem conta?", bg=self["bg"], fg="#242964", font=(
            "Arial", 10)).pack(pady=(12, 6))
        tk.Button(
            self,
            text="Criar conta de professor",
            command=self.on_go_register,
            bg=self["bg"],
            fg="#6C5CE7",
            font=("Arial", 10, "bold"),
            relief="flat"
        ).pack()

    def _entry_with_placeholder(self, placeholder, is_password=False):
        e = tk.Entry(self, font=("Arial", 12), width=28, relief="flat", bd=4)
        e.insert(0, placeholder)
        if is_password:
          
            e.config(show="")
        e._placeholder = placeholder
        e._is_password = is_password
        e.bind("<FocusIn>", lambda ev: self._on_focus_in(e))
        e.bind("<FocusOut>", lambda ev: self._on_focus_out(e))
        return e

    def _on_focus_in(self, entry):
        if entry.get() == entry._placeholder:
            entry.delete(0, tk.END)
            if entry._is_password:
                entry.config(show="*")

    def _on_focus_out(self, entry):
        if entry.get() == "":
            entry.insert(0, entry._placeholder)
            if entry._is_password:
                entry.config(show="")

    def _attach_digit_limiter(self, entry: tk.Entry, max_len: int):
        # Allow only digits and limit length
        def validate(text_after):
            return len(text_after) <= max_len and re.fullmatch(r"\d*", text_after) is not None
        vcmd = (self.register(validate), "%P")
        entry.configure(validate="key", validatecommand=vcmd)

    def _handle_login(self):
        email = self.email_entry.get().strip()
        pw = self.pw_entry.get().strip()

        # If placeholders still present, treat as empty
        if email == self.email_entry._placeholder:
            email = ""
        if pw == self.pw_entry._placeholder:
            pw = ""

        errors = []
        if not is_valid_prof_email(email):
            dlist = ", ".join(f"@{d}" for d in PROFESSOR_DOMAINS)
            errors.append(
                f"E-mail deve ser institucional de professor ({dlist}).")
        if not is_valid_password(pw):
            errors.append("Senha deve ter exatamente 5 dígitos numéricos.")

        if errors:
            messagebox.showerror("Erro no login", "\n".join(errors))
            return

        user = self.users.get(email.lower())
        if not user or user.get("senha") != pw:
            messagebox.showerror("Credenciais inválidas",
                                 "E-mail ou senha incorretos.")
            return

        messagebox.showinfo(
            "Bem-vindo(a)!", f"Login concluído, Prof(a). {user.get('nome', 'Docente')} — Disciplina: {user.get('disciplina', '')}")


#Frame de Cadastro 
class RegisterFrame(tk.Frame):
    def __init__(self, master, users, on_done):
        super().__init__(master, bg=master["bg"])
        self.master = master
        self.users = users
        self.on_done = on_done

        tk.Label(self, text="Cadastro", font=("Arial", 24, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(40, 6))
        tk.Label(self, text="Preencha seus dados de professor", font=(
            "Arial", 10), bg=self["bg"], fg="#242964").pack(pady=(0, 14))

        # Campos
        self.nome = self._entry_with_placeholder("Nome completo")
        self.nome.pack(pady=6, ipady=6)
        self.email = self._entry_with_placeholder(
            "E-mail institucional (prof)")
        self.email.pack(pady=6, ipady=6)
        self.senha = self._entry_with_placeholder(
            "Senha (5 dígitos)", is_password=True)
        self._attach_digit_limiter(self.senha, max_len=5)
        self.senha.pack(pady=6, ipady=6)
        self.disciplina = self._entry_with_placeholder("Disciplina")
        self.disciplina.pack(pady=6, ipady=6)

        # Botões
        tk.Button(
            self,
            text="Validar & Salvar",
            command=self._handle_register,
            bg="#6C5CE7",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            width=24,
            padx=6,
            pady=6
        ).pack(pady=(18, 10))

        tk.Button(
            self,
            text="Voltar ao Login",
            command=self.on_done,
            bg=self["bg"],
            fg="#6C5CE7",
            font=("Arial", 10, "bold"),
            relief="flat"
        ).pack()

    def _entry_with_placeholder(self, placeholder, is_password=False):
        e = tk.Entry(self, font=("Arial", 12), width=28, relief="flat", bd=4)
        e.insert(0, placeholder)
        if is_password:
            e.config(show="")
        e._placeholder = placeholder
        e._is_password = is_password
        e.bind("<FocusIn>", lambda ev: self._on_focus_in(e))
        e.bind("<FocusOut>", lambda ev: self._on_focus_out(e))
        return e

    def _on_focus_in(self, entry):
        if entry.get() == entry._placeholder:
            entry.delete(0, tk.END)
            if entry._is_password:
                entry.config(show="*")

    def _on_focus_out(self, entry):
        if entry.get() == "":
            entry.insert(0, entry._placeholder)
            if entry._is_password:
                entry.config(show="")

    def _attach_digit_limiter(self, entry: tk.Entry, max_len: int):
        def validate(text_after):
            return len(text_after) <= max_len and re.fullmatch(r"\d*", text_after) is not None
        vcmd = (self.register(validate), "%P")
        entry.configure(validate="key", validatecommand=vcmd)

    def _handle_register(self):
        nome = self.nome.get().strip()
        email = self.email.get().strip()
        pw = self.senha.get().strip()
        disc = self.disciplina.get().strip()

        # Treat placeholders as empty
        if nome == self.nome._placeholder:
            nome = ""
        if email == self.email._placeholder:
            email = ""
        if pw == self.senha._placeholder:
            pw = ""
        if disc == self.disciplina._placeholder:
            disc = ""

        errors = []
        if not nome:
            errors.append("Informe o nome completo.")
        if not is_valid_prof_email(email):
            dlist = ", ".join(f"@{d}" for d in PROFESSOR_DOMAINS)
            errors.append(
                f"E-mail deve ser institucional de professor ({dlist}).")
        if not is_valid_password(pw):
            errors.append("Senha deve ter exatamente 5 dígitos numéricos.")
        if not disc:
            errors.append("Informe a disciplina.")

        if errors:
            messagebox.showerror("Corrija os campos", "\n".join(errors))
            return

        key = email.lower()
        if key in self.users:
            messagebox.showerror(
                "E-mail já cadastrado", "Este e-mail já existe. Faça login ou use outro e-mail.")
            return

        # salvar
        self.users[key] = {"nome": nome, "email": key,
                           "senha": pw, "disciplina": disc}
        try:
            save_users(self.users)
            messagebox.showinfo(
                "Sucesso", "Cadastro realizado! Você já pode fazer login.")
            self.on_done()
        except Exception as e:
            messagebox.showerror(
                "Erro ao salvar", f"Não foi possível salvar os dados.\n{e}")


# Execução
if __name__ == "__main__":
    app = App()
    app.mainloop()


