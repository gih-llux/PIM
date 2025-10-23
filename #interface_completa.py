# interface inicial
# portal_unip_completo.py
import re
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# ---------------- Configurações / Arquivos ----------------
ALUNOS_FILE = "alunos.json"
PROFESSORES_FILE = "professores.json"
DISCIPLINAS_FILE = "disciplinas.json"
NOTAS_FILE = "notas.json"
FALTAS_FILE = "faltas.json"
REVISOES_FILE = "revisoes.json"

ALUNO_DOMAIN = "unip.br"
PROFESSOR_DOMAINS = ["prof.unip.br", "docente.unip.br"]

# ---------------- Validações ----------------


def is_valid_password(pw: str) -> bool:
    return bool(re.fullmatch(r"\d{5}", pw))


def is_valid_ra(ra: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9]{7}", ra))


def is_valid_student_email(email: str) -> bool:
    return bool(re.fullmatch(rf"[A-Za-z0-9._%+-]+@{re.escape(ALUNO_DOMAIN)}", email))


def is_valid_prof_email(email: str) -> bool:
    domains = "|".join(re.escape(d) for d in PROFESSOR_DOMAINS)
    pattern = rf"^[A-Za-z0-9._%+-]+@(?:{domains})$"
    return bool(re.fullmatch(pattern, email))


def is_valid_birthdate(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# ---------------- JSON helpers ----------------


def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------- Aplicativo Principal ----------------


class PortalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portal UNIP - Sistema Unificado")
        self.geometry("480x700")
        self.minsize(420, 600)
        self.configure(bg="#DCDDE1")

        # Carregar "bancos"
        self.users_alunos = load_json(ALUNOS_FILE)
        self.users_prof = load_json(PROFESSORES_FILE)

        self.active_frame = None
        self.show_home()

    def _clear(self):
        if self.active_frame:
            self.active_frame.destroy()
            self.active_frame = None

    # Home / navegação
    def show_home(self):
        self._clear()
        self.active_frame = HomeFrame(self)
        self.active_frame.pack(expand=True, fill="both")

    # ALUNO
    def show_login_aluno(self):
        self._clear()
        self.active_frame = LoginAlunoFrame(self,
                                            self.users_alunos,
                                            on_login_success=self.show_portal_aluno,
                                            on_register=self.show_register_aluno,
                                            on_back=self.show_home)
        self.active_frame.pack(expand=True, fill="both")

    def show_register_aluno(self):
        self._clear()
        self.active_frame = RegisterAlunoFrame(self,
                                               self.users_alunos,
                                               on_done=self.show_login_aluno)
        self.active_frame.pack(expand=True, fill="both")

    def show_portal_aluno(self, ra):
        # recarrega users (caso tenham sido alterados)
        self.users_alunos = load_json(ALUNOS_FILE)
        self._clear()
        self.active_frame = PortalAlunoFrame(self, self.users_alunos, ra,
                                             on_logout=self.show_home)
        self.active_frame.pack(expand=True, fill="both")

    # PROFESSOR
    def show_login_prof(self):
        self._clear()
        self.active_frame = LoginProfFrame(self,
                                           self.users_prof,
                                           on_login_success=self.show_portal_prof,
                                           on_register=self.show_register_prof,
                                           on_back=self.show_home)
        self.active_frame.pack(expand=True, fill="both")

    def show_register_prof(self):
        self._clear()
        self.active_frame = RegisterProfFrame(self,
                                              self.users_prof,
                                              on_done=self.show_login_prof)
        self.active_frame.pack(expand=True, fill="both")

    def show_portal_prof(self, email):
        # recarrega bancos
        self.users_prof = load_json(PROFESSORES_FILE)
        self.users_alunos = load_json(ALUNOS_FILE)
        self._clear()
        self.active_frame = PortalProfFrame(self, self.users_prof, email,
                                            alunos=self.users_alunos,
                                            on_logout=self.show_home)
        self.active_frame.pack(expand=True, fill="both")

# ---------------- Tela Inicial ----------------


class HomeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=master["bg"])
        tk.Label(self, text="Portal UNIP", font=("Arial", 34, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(60, 10))
        tk.Label(self, text="Escolha seu tipo de acesso", font=("Arial", 12),
                 bg=self["bg"], fg="#242964").pack(pady=(0, 18))

        # Botões
        tk.Button(self, text="🎓 Sou Aluno", command=master.show_login_aluno,
                  bg="#6C5CE7", fg="white", font=("Arial", 13, "bold"),
                  relief="flat", width=22, height=2).pack(pady=12)

        tk.Button(self, text="🧑‍🏫 Sou Professor", command=master.show_login_prof,
                  bg="#0984E3", fg="white", font=("Arial", 13, "bold"),
                  relief="flat", width=22, height=2).pack(pady=6)

# ---------------- Login / Cadastro Aluno ----------------


class LoginAlunoFrame(tk.Frame):
    def __init__(self, master, users, on_login_success, on_register, on_back):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.on_login_success = on_login_success
        self.on_register = on_register
        self.on_back = on_back

        tk.Label(self, text="Login do Aluno", font=("Arial", 24, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(50, 8))

        self.ra_entry = self._entry_with_placeholder("RA (7 caracteres)")
        self.pw_entry = self._entry_with_placeholder(
            "Senha (5 dígitos)", is_password=True)
        self._attach_digit_limiter(self.pw_entry, 5)

        self.ra_entry.pack(pady=8, ipady=6)
        self.pw_entry.pack(pady=8, ipady=6)

        tk.Button(self, text="Entrar", command=self._login,
                  bg="#6C5CE7", fg="white", font=("Arial", 11, "bold"),
                  relief="flat", width=24).pack(pady=(18, 8))

        tk.Button(self, text="Criar Cadastro", command=self.on_register,
                  bg="#DCDDE1", fg="#6C5CE7", font=("Arial", 10, "bold"),
                  relief="flat").pack(pady=4)

        tk.Button(self, text="Voltar", command=self.on_back,
                  bg="#DCDDE1", fg="#242964", font=("Arial", 10, "bold"),
                  relief="flat").pack(pady=8)

    def _entry_with_placeholder(self, placeholder, is_password=False):
        e = tk.Entry(self, font=("Arial", 12), width=30, relief="flat", bd=4)
        e.insert(0, placeholder)
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
        entry.configure(validate="key", validatecommand=(
            self.register(validate), "%P"))

    def _login(self):
        ra = self.ra_entry.get().strip().upper()
        pw = self.pw_entry.get().strip()

        if ra in ("", self.ra_entry._placeholder) or pw in ("", self.pw_entry._placeholder):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if not is_valid_ra(ra):
            messagebox.showerror("Erro", "RA inválido.")
            return
        if not is_valid_password(pw):
            messagebox.showerror("Erro", "Senha inválida (5 dígitos).")
            return

        user = self.users.get(ra)
        if not user or user.get("senha") != pw:
            messagebox.showerror("Erro", "RA ou senha incorretos.")
            return

        messagebox.showinfo("Bem-vindo", f"Olá, {user.get('nome')}!")
        self.on_login_success(ra)


class RegisterAlunoFrame(tk.Frame):
    def __init__(self, master, users, on_done):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.on_done = on_done

        tk.Label(self, text="Cadastro de Aluno", font=("Arial", 22, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(30, 8))

        # campos
        self.nome = self._entry("Nome completo")
        self.email = self._entry(f"E-mail institucional (@{ALUNO_DOMAIN})")
        self.nasc = self._entry("Data de nascimento (DD/MM/AAAA)")
        self.ra = self._entry("RA (7 caracteres)")
        self.senha = self._entry("Senha (5 dígitos)", is_password=True)
        self._attach_digit_limiter(self.senha, 5)

        for w in (self.nome, self.email, self.nasc, self.ra, self.senha):
            w.pack(pady=6, ipady=6)

        tk.Button(self, text="Salvar", command=self._salvar,
                  bg="#6C5CE7", fg="white", font=("Arial", 11, "bold"),
                  relief="flat", width=26).pack(pady=(16, 8))

        tk.Button(self, text="Voltar", command=self.on_done,
                  bg="#DCDDE1", fg="#242964", font=("Arial", 10, "bold"),
                  relief="flat").pack()

    def _entry(self, placeholder, is_password=False):
        e = tk.Entry(self, font=("Arial", 12), width=30, relief="flat", bd=4)
        e.insert(0, placeholder)
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
        entry.configure(validate="key", validatecommand=(
            self.register(validate), "%P"))

    def _salvar(self):
        nome = self.nome.get().strip()
        email = self.email.get().strip().lower()
        nasc = self.nasc.get().strip()
        ra = self.ra.get().strip().upper()
        senha = self.senha.get().strip()

        if not nome or not email or not nasc or not ra or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        if not is_valid_student_email(email):
            messagebox.showerror("Erro", f"E-mail deve ser @{ALUNO_DOMAIN}.")
            return
        if not is_valid_birthdate(nasc):
            messagebox.showerror(
                "Erro", "Data de nascimento inválida. Use DD/MM/AAAA.")
            return
        if not is_valid_ra(ra):
            messagebox.showerror("Erro", "RA inválido (7 caracteres).")
            return
        if not is_valid_password(senha):
            messagebox.showerror("Erro", "Senha inválida (5 dígitos).")
            return
        if ra in self.users:
            messagebox.showerror("Erro", "RA já cadastrado.")
            return

        self.users[ra] = {"nome": nome, "email": email,
                          "nascimento": nasc, "senha": senha}
        save_json(ALUNOS_FILE, self.users)
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
        self.on_done()

# ---------------- Portal do Aluno ----------------


class PortalAlunoFrame(tk.Frame):
    def __init__(self, master, users, ra, on_logout):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.ra = ra
        self.on_logout = on_logout

        tk.Label(self, text="Portal do Aluno - UNIP", font=("Arial", 20, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=16)
        tk.Label(self, text=f"Bem-vindo(a), {users[ra]['nome']}", font=("Arial", 12),
                 bg=self["bg"], fg="#242964").pack(pady=(0, 10))

        buttons = [
            ("📚 Disciplinas", self._disciplinas),
            ("🧮 Notas e Revisão", self._notas),
            ("📅 Faltas e Frequência", self._faltas),
            ("👤 Meu Cadastro", self._cadastro),
            ("🚪 Sair", self.on_logout)
        ]
        for txt, cmd in buttons:
            tk.Button(self, text=txt, command=cmd, width=28, pady=8,
                      bg="#6C5CE7" if txt != "🚪 Sair" else "#DCDDE1",
                      fg="white" if txt != "🚪 Sair" else "#242964",
                      font=("Arial", 11, "bold"), relief="flat").pack(pady=6)

    def _popup_window(self, title, size="480x420"):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry(size)
        win.configure(bg="#ECECEC")
        return win

    def _disciplinas(self):
        disciplinas = load_json(DISCIPLINAS_FILE).get(self.ra, [
            {"nome": "Programação I", "dia": "Segunda", "horario": "19h-21h"},
            {"nome": "Banco de Dados", "dia": "Terça", "horario": "19h-21h"}
        ])
        win = self._popup_window("Disciplinas e Cronograma")
        tk.Label(win, text="Disciplinas do semestre", font=(
            "Arial", 14, "bold"), bg="#ECECEC").pack(pady=8)
        for d in disciplinas:
            tk.Label(win, text=f"{d['nome']} — {d['dia']} ({d['horario']})", bg="#ECECEC", font=(
                "Arial", 11)).pack(anchor="w", padx=12, pady=4)

    def _notas(self):
        notas = load_json(NOTAS_FILE).get(self.ra, {
            "Programação I": {"P1": 8.5, "P2": 7.0},
            "Banco de Dados": {"P1": 7.5, "P2": 8.0}
        })
        win = self._popup_window("Notas e Solicitação de Revisão", "560x480")
        tk.Label(win, text="Notas do Semestre", font=(
            "Arial", 14, "bold"), bg="#ECECEC").pack(pady=8)

        # Treeview com colunas Disciplina, P1, P2
        tree = ttk.Treeview(win, columns=(
            "disc", "p1", "p2"), show="headings", height=8)
        tree.heading("disc", text="Disciplina")
        tree.heading("p1", text="P1")
        tree.heading("p2", text="P2")
        tree.column("disc", width=320)
        tree.column("p1", width=80, anchor="center")
        tree.column("p2", width=80, anchor="center")
        for disc, vals in notas.items():
            p1 = vals.get("P1", "-")
            p2 = vals.get("P2", "-")
            tree.insert("", "end", values=(disc, p1, p2))
        tree.pack(padx=12, pady=8, fill="x")

        # Solicitação de revisão
        tk.Label(win, text="Solicitar Revisão de Nota", bg="#ECECEC",
                 font=("Arial", 12, "bold")).pack(pady=(8, 4))
        materias = list(notas.keys())
        cb_mat = ttk.Combobox(win, values=materias, state="readonly", width=40)
        cb_mat.pack(pady=4)
        cb_prova = ttk.Combobox(
            win, values=["P1", "P2"], state="readonly", width=12)
        cb_prova.pack(pady=4)

        def solicitar_revisao():
            materia = cb_mat.get()
            prova = cb_prova.get()
            if not materia or not prova:
                messagebox.showerror("Erro", "Selecione disciplina e prova.")
                return
            revisoes = load_json(REVISOES_FILE)
            revisoes.setdefault(self.ra, []).append({
                "disciplina": materia,
                "prova": prova,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            save_json(REVISOES_FILE, revisoes)
            messagebox.showinfo("Solicitação enviada",
                                f"Revisão solicitada para {materia} - {prova}.")

        tk.Button(win, text="Solicitar Revisão", command=solicitar_revisao,
                  bg="#6C5CE7", fg="white", font=("Arial", 11, "bold"), relief="flat").pack(pady=10)

    def _faltas(self):
        faltas = load_json(FALTAS_FILE).get(
            self.ra, {"frequencia": "92%", "faltas": 3})
        win = self._popup_window("Faltas e Frequência")
        tk.Label(win, text=f"Frequência atual: {faltas['frequencia']}\nFaltas acumuladas: {faltas['faltas']}",
                 bg="#ECECEC", font=("Arial", 12)).pack(pady=12)
        tk.Label(win, text="Enviar atestado (PDF ou imagem):",
                 bg="#ECECEC", font=("Arial", 11, "bold")).pack(pady=4)

        def enviar():
            arq = filedialog.askopenfilename(title="Selecionar atestado")
            if arq:
                messagebox.showinfo("Atestado enviado",
                                    "Atestado enviado com sucesso!")
        tk.Button(win, text="Selecionar Arquivo", command=enviar,
                  bg="#6C5CE7", fg="white", font=("Arial", 11, "bold"), relief="flat").pack(pady=8)

    def _cadastro(self):
        user = self.users[self.ra]
        win = self._popup_window("Meu Cadastro")
        txt = (f"Nome: {user['nome']}\nE-mail: {user['email']}\nNascimento: {user.get('nascimento', '---')}\n\n"
               "Para alterar dados, contate a secretaria.")
        tk.Label(win, text=txt, bg="#ECECEC", justify="left",
                 font=("Arial", 12)).pack(padx=12, pady=12)

# ---------------- Login / Cadastro Professor ----------------


class LoginProfFrame(tk.Frame):
    def __init__(self, master, users, on_login_success, on_register, on_back):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.on_login_success = on_login_success
        self.on_register = on_register
        self.on_back = on_back

        tk.Label(self, text="Login do Professor", font=("Arial", 22, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(60, 8))
        tk.Label(self, text="Use seu e-mail institucional",
                 bg=self["bg"], fg="#242964").pack(pady=(0, 8))

        self.email_entry = self._entry_with_placeholder(
            "E-mail institucional (prof)")
        self.pw_entry = self._entry_with_placeholder(
            "Senha (5 dígitos)", is_password=True)
        self._attach_digit_limiter(self.pw_entry, 5)

        self.email_entry.pack(pady=8, ipady=6)
        self.pw_entry.pack(pady=8, ipady=6)

        tk.Button(self, text="Entrar", command=self._login,
                  bg="#0984E3", fg="white", font=("Arial", 11, "bold"),
                  relief="flat", width=24).pack(pady=(16, 8))

        tk.Button(self, text="Criar conta de professor", command=self.on_register,
                  bg=self["bg"], fg="#0984E3", font=("Arial", 10, "bold"),
                  relief="flat").pack(pady=4)

        tk.Button(self, text="Voltar", command=self.on_back,
                  bg="#DCDDE1", fg="#242964", font=("Arial", 10, "bold"),
                  relief="flat").pack(pady=8)

    def _entry_with_placeholder(self, placeholder, is_password=False):
        e = tk.Entry(self, font=("Arial", 12), width=32, relief="flat", bd=4)
        e.insert(0, placeholder)
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
        entry.configure(validate="key", validatecommand=(
            self.register(validate), "%P"))

    def _login(self):
        email = self.email_entry.get().strip().lower()
        pw = self.pw_entry.get().strip()
        if email in ("", self.email_entry._placeholder) or pw in ("", self.pw_entry._placeholder):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        if not is_valid_prof_email(email):
            dlist = ", ".join(f"@{d}" for d in PROFESSOR_DOMAINS)
            messagebox.showerror(
                "Erro", f"E-mail deve ser institucional ({dlist}).")
            return
        if not is_valid_password(pw):
            messagebox.showerror("Erro", "Senha inválida (5 dígitos).")
            return
        user = self.users.get(email)
        if not user or user.get("senha") != pw:
            messagebox.showerror("Erro", "E-mail ou senha incorretos.")
            return
        messagebox.showinfo("Bem-vindo", f"Olá, Prof(a). {user.get('nome')}!")
        self.on_login_success(email)


class RegisterProfFrame(tk.Frame):
    def __init__(self, master, users, on_done):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.on_done = on_done

        tk.Label(self, text="Cadastro de Professor", font=("Arial", 22, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(30, 8))
        tk.Label(self, text="Insira seus dados institucionais",
                 bg=self["bg"], fg="#242964").pack(pady=(0, 6))

        self.nome = self._entry("Nome completo")
        self.email = self._entry("E-mail institucional (prof)")
        self.senha = self._entry("Senha (5 dígitos)", is_password=True)
        self.disciplina = self._entry("Disciplina (ex: Programação I)")

        for w in (self.nome, self.email, self.senha, self.disciplina):
            w.pack(pady=6, ipady=6)

        self._attach_digit_limiter(self.senha, 5)

        tk.Button(self, text="Validar & Salvar", command=self._salvar,
                  bg="#0984E3", fg="white", font=("Arial", 11, "bold"),
                  relief="flat", width=26).pack(pady=(12, 8))

        tk.Button(self, text="Voltar", command=self.on_done,
                  bg="#DCDDE1", fg="#242964", font=("Arial", 10, "bold"),
                  relief="flat").pack()

    def _entry(self, placeholder, is_password=False):
        e = tk.Entry(self, font=("Arial", 12), width=32, relief="flat", bd=4)
        e.insert(0, placeholder)
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
        entry.configure(validate="key", validatecommand=(
            self.register(validate), "%P"))

    def _salvar(self):
        nome = self.nome.get().strip()
        email = self.email.get().strip().lower()
        pw = self.senha.get().strip()
        disc = self.disciplina.get().strip()

        if not nome or not email or not pw or not disc:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        if not is_valid_prof_email(email):
            dlist = ", ".join(f"@{d}" for d in PROFESSOR_DOMAINS)
            messagebox.showerror(
                "Erro", f"E-mail deve ser institucional ({dlist}).")
            return
        if not is_valid_password(pw):
            messagebox.showerror("Erro", "Senha inválida (5 dígitos).")
            return
        if email in self.users:
            messagebox.showerror("Erro", "E-mail já cadastrado.")
            return

        self.users[email] = {"nome": nome, "email": email,
                             "senha": pw, "disciplina": disc}
        save_json(PROFESSORES_FILE, self.users)
        messagebox.showinfo("Sucesso", "Cadastro de professor realizado!")
        self.on_done()

# ---------------- Portal do Professor ----------------


class PortalProfFrame(tk.Frame):
    def __init__(self, master, users_prof, email, alunos, on_logout):
        super().__init__(master, bg=master["bg"])
        self.users_prof = users_prof
        self.email = email
        self.alunos = alunos  # todos os alunos do JSON
        self.on_logout = on_logout

        prof = users_prof.get(email, {})
        nome = prof.get("nome", "Professor")
        disc = prof.get("disciplina", "—")

        tk.Label(self, text="Portal do Professor", font=("Arial", 20, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=12)
        tk.Label(self, text=f"Prof(a). {nome} — Disciplina: {disc}", font=("Arial", 12),
                 bg=self["bg"], fg="#242964").pack(pady=(0, 12))

        tk.Label(self, text="Alunos cadastrados (todos no sistema)", font=("Arial", 12, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(6, 6))

        # Treeview com alunos
        cols = ("RA", "Nome", "E-mail")
        tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("RA", width=100, anchor="center")
        tree.column("Nome", width=220)
        tree.column("E-mail", width=260)
        tree.pack(padx=12, pady=6, fill="both", expand=True)

        # popular
        for ra, info in sorted(self.alunos.items()):
            tree.insert("", "end", values=(ra, info.get(
                "nome", "-"), info.get("email", "-")))

        tk.Button(self, text="🚪 Sair", command=self.on_logout,
                  bg="#DCDDE1", fg="#242964", font=("Arial", 11, "bold"),
                  relief="flat", width=18).pack(pady=10)


# ---------------- Execução ----------------
if __name__ == "__main__":
    app = PortalApp()
    app.mainloop()
