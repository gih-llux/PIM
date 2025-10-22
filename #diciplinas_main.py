# diciplinas_main.py
import tkinter as tk
from tkinter import ttk, messagebox
import json, os, re

# CONFIGURAÇÕES
PROFESSOR_DOMAINS = ["prof.unip.br", "docente.unip.br"]
USERS_FILE = "professores.json"

# Validação para o professor ter acesso a sua área
def is_valid_password(pw: str) -> bool:
    return bool(re.fullmatch(r"\d{5}", pw))  # senha de 5 digitos


def is_valid_prof_email(email: str) -> bool:
    domains = "|".join(re.escape(d) for d in PROFESSOR_DOMAINS)
    pattern = rf"^[A-Za-z0-9._%+-]+@(?:{domains})$"
    return bool(re.fullmatch(pattern, email))


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


# Tela de funções
class CadastroWindow(tk.Toplevel):
    def __init__(self, user):
        super().__init__()
        self.title("Meu Cadastro")
        self.geometry("400x300")
        self.user = user

        ttk.Label(self, text="Alterar dados cadastrais", font=("Arial", 13, "bold")).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(pady=10)

        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="w")
        nome_entry = ttk.Entry(frame)
        nome_entry.insert(0, user["nome"])
        nome_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Disciplina:").grid(row=1, column=0, sticky="w")
        disc_entry = ttk.Entry(frame)
        disc_entry.insert(0, user["disciplina"])
        disc_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Nova senha (5 dígitos):").grid(row=2, column=0, sticky="w")
        senha_entry = ttk.Entry(frame, show="*")
        senha_entry.grid(row=2, column=1, pady=5)

        def salvar():
            nome = nome_entry.get().strip()
            disc = disc_entry.get().strip()
            senha = senha_entry.get().strip()

            users = load_users()
            email = self.user["email"]
            if email in users:
                users[email]["nome"] = nome
                users[email]["disciplina"] = disc
                if senha:
                    if not is_valid_password(senha):
                        messagebox.showerror("Erro", "A nova senha deve conter 5 dígitos.")
                        return
                    users[email]["senha"] = senha
                save_users(users)
                messagebox.showinfo("Sucesso", "Dados atualizados com sucesso!")

        ttk.Button(self, text="Salvar alterações", command=salvar).pack(pady=10)


class NotasWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Gerenciamento de Notas")
        self.geometry("400x300")

        ttk.Label(self, text="Gerenciamento de Notas", font=("Arial", 13, "bold")).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(pady=10)

        ttk.Label(frame, text="Aluno:").grid(row=0, column=0)
        aluno_entry = ttk.Entry(frame)
        aluno_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Nota:").grid(row=1, column=0)
        nota_entry = ttk.Entry(frame)
        nota_entry.grid(row=1, column=1, pady=5)

        def postar_nota():
            aluno = aluno_entry.get().strip()
            nota = nota_entry.get().strip()
            if not aluno or not nota:
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return
            try:
                nota = float(nota)
            except ValueError:
                messagebox.showerror("Erro", "A nota deve ser numérica.")
                return

            notas_file = "notas.json"
            notas = {}
            if os.path.exists(notas_file):
                with open(notas_file, "r", encoding="utf-8") as f:
                    notas = json.load(f)

            notas[aluno] = nota
            with open(notas_file, "w", encoding="utf-8") as f:
                json.dump(notas, f, indent=2)
            messagebox.showinfo("Sucesso", f"Nota de {aluno} registrada: {nota}")

        ttk.Button(self, text="Salvar Nota", command=postar_nota).pack(pady=10)


class FaltasWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Gerenciamento de Faltas")
        self.geometry("400x300")

        ttk.Label(self, text="Gerenciamento de Faltas", font=("Arial", 13, "bold")).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(pady=10)

        ttk.Label(frame, text="Aluno:").grid(row=0, column=0)
        aluno_entry = ttk.Entry(frame)
        aluno_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Faltas:").grid(row=1, column=0)
        faltas_entry = ttk.Entry(frame)
        faltas_entry.grid(row=1, column=1, pady=5)

        def salvar_faltas():
            aluno = aluno_entry.get().strip()
            faltas = faltas_entry.get().strip()
            if not aluno or not faltas.isdigit():
                messagebox.showerror("Erro", "Informe um aluno e um número válido de faltas.")
                return

            faltas_file = "faltas.json"
            faltas_data = {}
            if os.path.exists(faltas_file):
                with open(faltas_file, "r", encoding="utf-8") as f:
                    faltas_data = json.load(f)

            faltas_data[aluno] = int(faltas)
            with open(faltas_file, "w", encoding="utf-8") as f:
                json.dump(faltas_data, f, indent=2)
            messagebox.showinfo("Sucesso", "Faltas registradas!")

        ttk.Button(self, text="Salvar Faltas", command=salvar_faltas).pack(pady=10)


class CronogramaWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Cronograma")
        self.geometry("500x400")

        ttk.Label(self, text="Alteração de Cronograma", font=("Arial", 13, "bold")).pack(pady=10)
        texto = tk.Text(self, width=60, height=15)
        texto.pack(pady=5)

        cronograma_file = "cronograma.json"
        if os.path.exists(cronograma_file):
            with open(cronograma_file, "r", encoding="utf-8") as f:
                texto.insert("1.0", f.read())

        def salvar():
            conteudo = texto.get("1.0", "end").strip()
            with open(cronograma_file, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Sucesso", "Cronograma atualizado!")

        ttk.Button(self, text="Salvar", command=salvar).pack(pady=10)


# Menu principal
class SistemaProfessor(tk.Toplevel):
    def __init__(self, user_info):
        super().__init__()
        self.title("Área do Professor")
        self.geometry("600x500")
        self.configure(bg="#ffffff")

        ttk.Label(self, text=f"Bem-vindo(a), Prof. {user_info['nome']}",
                  font=("Arial", 16, "bold"), background="#ffffff", foreground="#006b3f").pack(pady=30)

        btn_style = {"font": ("Arial", 12), "bg": "#00b37e", "fg": "white", "activebackground": "#009e6b",
                     "relief": "flat", "width": 25, "height": 2}

        tk.Button(self, text="Meu Cadastro", command=lambda: CadastroWindow(user_info), **btn_style).pack(pady=8)
        tk.Button(self, text="Gerenciamento de Notas", command=NotasWindow, **btn_style).pack(pady=8)
        tk.Button(self, text="Gerenciamento de Faltas", command=FaltasWindow, **btn_style).pack(pady=8)
        tk.Button(self, text="Alteração de Cronograma", command=CronogramaWindow, **btn_style).pack(pady=8)
        tk.Button(self, text="Sair", command=self.destroy, **btn_style).pack(pady=25)


#Tela de login e cadastro
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Sistema de Professores")
        self.geometry("450x400")
        self.configure(bg="#ffffff")

        self.users = load_users()
        self._build_login()

    def _build_login(self):
        frame = tk.Frame(self, bg="#ffffff")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Login do Professor", font=("Arial", 16, "bold"),
                 fg="#006b3f", bg="#ffffff").pack(pady=10)

        tk.Label(frame, text="E-mail:", bg="#ffffff").pack(anchor="w")
        self.email_entry = ttk.Entry(frame, width=35)
        self.email_entry.pack(pady=5)

        tk.Label(frame, text="Senha (5 dígitos):", bg="#ffffff").pack(anchor="w")
        self.pw_entry = ttk.Entry(frame, show="*", width=35)
        self.pw_entry.pack(pady=5)

        ttk.Button(frame, text="Entrar", command=self._handle_login).pack(pady=10)
        ttk.Button(frame, text="Cadastrar", command=self._open_register).pack(pady=5)

    def _handle_login(self):
        email = self.email_entry.get().strip().lower()
        senha = self.pw_entry.get().strip()

        user = self.users.get(email)
        if not user or user["senha"] != senha:
            messagebox.showerror("Erro", "E-mail ou senha incorretos.")
            return

        self.destroy()
        SistemaProfessor(user).mainloop()

    def _open_register(self):
        reg = tk.Toplevel(self)
        reg.title("Cadastro de Professor")
        reg.geometry("400x400")
        reg.configure(bg="#ffffff")

        frame = tk.Frame(reg, bg="#ffffff")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Cadastro de Professor", font=("Arial", 14, "bold"),
                 fg="#006b3f", bg="#ffffff").pack(pady=10)

        tk.Label(frame, text="Nome:", bg="#ffffff").pack(anchor="w")
        nome_entry = ttk.Entry(frame, width=35)
        nome_entry.pack(pady=5)

        tk.Label(frame, text="Disciplina:", bg="#ffffff").pack(anchor="w")
        disc_entry = ttk.Entry(frame, width=35)
        disc_entry.pack(pady=5)

        tk.Label(frame, text="E-mail:", bg="#ffffff").pack(anchor="w")
        email_entry = ttk.Entry(frame, width=35)
        email_entry.pack(pady=5)

        tk.Label(frame, text="Senha (5 dígitos):", bg="#ffffff").pack(anchor="w")
        pw_entry = ttk.Entry(frame, show="*", width=35)
        pw_entry.pack(pady=5)

        def registrar():
            nome = nome_entry.get().strip()
            disc = disc_entry.get().strip()
            email = email_entry.get().strip().lower()
            senha = pw_entry.get().strip()

            if not nome or not disc or not email or not senha:
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return
            if not is_valid_prof_email(email):
                messagebox.showerror("Erro", "E-mail inválido para professor UNIP.")
                return
            if not is_valid_password(senha):
                messagebox.showerror("Erro", "A senha deve conter exatamente 5 dígitos.")
                return

            users = load_users()
            if email in users:
                messagebox.showerror("Erro", "E-mail já cadastrado.")
                return

            users[email] = {"nome": nome, "disciplina": disc, "email": email, "senha": senha}
            save_users(users)
            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
            reg.destroy()

        ttk.Button(frame, text="Cadastrar", command=registrar).pack(pady=10)


# EXECUÇÃO
if __name__ == "__main__":
    App().mainloop()

