# portal_unip_completo.py
import re
import json
import os
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# Configurações
ALUNOS_FILE = "alunos.json"
PROFESSORES_FILE = "professores.json"
DISCIPLINAS_FILE = "disciplinas.json"
NOTAS_FILE = "notas.json"
FALTAS_FILE = "faltas.json"
REVISOES_FILE = "revisoes.json"
DIARIO_FILE = "diario.json"

ALUNO_DOMAIN = "unip.br"
PROFESSOR_DOMAINS = ["prof.unip.br", "docente.unip.br"]

# Utilidades


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def is_hashed(value: str) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", value))


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

# JSON helpers


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

# Interface incial


class PortalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portal UNIP - Sistema Unificado")
        self.geometry("480x700")
        self.minsize(420, 600)
        self.configure(bg="#DCDDE1")

        # Carregar dados já salvos
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
        self.users_alunos = load_json(ALUNOS_FILE)
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
        self.users_alunos = load_json(ALUNOS_FILE)
        self._clear()
        self.active_frame = PortalAlunoFrame(self, self.users_alunos, ra,
                                             on_logout=self.show_home)
        self.active_frame.pack(expand=True, fill="both")

    # PROFESSOR
    def show_login_prof(self):
        self.users_prof = load_json(PROFESSORES_FILE)
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
        self.users_prof = load_json(PROFESSORES_FILE)
        self.users_alunos = load_json(ALUNOS_FILE)
        self._clear()
        self.active_frame = PortalProfFrame(self, self.users_prof, email,
                                            alunos=self.users_alunos,
                                            on_logout=self.show_home)
        self.active_frame.pack(expand=True, fill="both")

# Tela Inicial


class HomeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=master["bg"])
        tk.Label(self, text="Portal UNIP", font=("Arial", 34, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(60, 10))
        tk.Label(self, text="Escolha seu tipo de acesso", font=("Arial", 12),
                 bg=self["bg"], fg="#242964").pack(pady=(0, 18))

        tk.Button(self, text="🎓 Sou Aluno", command=master.show_login_aluno,
                  bg="#6C5CE7", fg="white", font=("Arial", 13, "bold"),
                  relief="flat", width=22, height=2).pack(pady=12)

        tk.Button(self, text="🧑‍🏫 Sou Professor", command=master.show_login_prof,
                  bg="#0984E3", fg="white", font=("Arial", 13, "bold"),
                  relief="flat", width=22, height=2).pack(pady=6)

# Login / Cadastro Aluno


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
        if not user:
            messagebox.showerror("Erro", "RA não cadastrado.")
            return

        stored = user.get("senha", "")
        if is_hashed(stored):
            if hash_pw(pw) != stored:
                messagebox.showerror("Erro", "RA ou senha incorretos.")
                return
        else:
            if stored != pw:
                messagebox.showerror("Erro", "RA ou senha incorretos.")
                return
            self.users[ra]["senha"] = hash_pw(pw)
            save_json(ALUNOS_FILE, self.users)

        messagebox.showinfo("Bem-vindo", f"Olá, {user.get('nome')}!")
        self.on_login_success(ra)


class RegisterAlunoFrame(tk.Frame):
    def __init__(self, master, users, on_done):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.on_done = on_done

        tk.Label(self, text="Cadastro de Aluno", font=("Arial", 22, "bold"),
                 bg=self["bg"], fg="#242964").pack(pady=(30, 8))

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
                          "nascimento": nasc, "senha": hash_pw(senha)}
        save_json(ALUNOS_FILE, self.users)
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
        self.on_done()

# Portal do Aluno


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

        tk.Button(win, text="Solicitar Revisão", command=solicitar_revisao, bg="#6C5CE7",
                  fg="white", font=("Arial", 11, "bold"), relief="flat").pack(pady=10)

    def _faltas(self):
        faltas_data = load_json(FALTAS_FILE)
        faltas = faltas_data.get(self.ra, {"frequencia": "100%", "faltas": 0, "atestados": [
        ], "total_aulas": 0, "presencas": 0})

        win = self._popup_window("Faltas e Frequência", "520x460")
        tk.Label(win, text="Situação Atual", font=(
            "Arial", 14, "bold"), bg="#ECECEC").pack(pady=8)

        freq = faltas.get("frequencia", "0%")
        try:
            freq_val = int(freq.strip('%'))
        except Exception:
            freq_val = 0
        faltas_qtd = faltas.get("faltas", 0)
        cor_freq = "#27AE60" if freq_val >= 75 else "#E74C3C"
        cor_falta = "#E74C3C"

        tk.Label(win, text=f"Frequência: {freq}", fg=cor_freq, bg="#ECECEC", font=(
            "Arial", 12, "bold")).pack(pady=4)
        tk.Label(win, text=f"Faltas: {faltas_qtd}", fg=cor_falta, bg="#ECECEC", font=(
            "Arial", 12, "bold")).pack(pady=4)

        tk.Label(win, text="Enviar Atestado (PDF, JPG, PNG):",
                 bg="#ECECEC", font=("Arial", 12, "bold")).pack(pady=(20, 4))

        def enviar():
            caminho = filedialog.askopenfilename(title="Selecionar atestado", filetypes=[
                                                 ("Documentos e imagens", "*.pdf;*.jpg;*.jpeg;*.png")])
            if caminho:
                faltas.setdefault("atestados", []).append({
                    "arquivo": caminho,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                faltas_data[self.ra] = faltas
                save_json(FALTAS_FILE, faltas_data)
                messagebox.showinfo(
                    "Sucesso", "Atestado enviado ao professor.")
                listar_atestados()

        tk.Button(win, text="📎 Selecionar Arquivo", command=enviar, bg="#6C5CE7",
                  fg="white", font=("Arial", 11, "bold"), relief="flat").pack(pady=8)

        tk.Label(win, text="Atestados Enviados:", bg="#ECECEC",
                 font=("Arial", 12, "bold")).pack(pady=(16, 4))

        tree = ttk.Treeview(win, columns=("data", "arquivo"),
                            show="headings", height=5)
        tree.heading("data", text="Data do Envio")
        tree.heading("arquivo", text="Arquivo")
        tree.column("data", width=140)
        tree.column("arquivo", width=300)
        tree.pack(padx=12, pady=4, fill="x")

        def listar_atestados():
            for i in tree.get_children():
                tree.delete(i)
            for at in faltas.get("atestados", []):
                tree.insert("", "end", values=(
                    at["data"], os.path.basename(at["arquivo"])))

        listar_atestados()

    def _cadastro(self):
        user = self.users[self.ra]
        win = self._popup_window("Meu Cadastro")
        txt = (f"Nome: {user['nome']}\nE-mail: {user['email']}\nNascimento: {user.get('nascimento', '---')}\n\n"
               "Para alterar outros dados, contate a secretaria.")
        tk.Label(win, text=txt, bg="#ECECEC", justify="left",
                 font=("Arial", 12)).pack(padx=12, pady=12)

        def alterar_senha():
            dlg = tk.Toplevel(win)
            dlg.title("Alterar Senha")
            dlg.geometry("360x220")
            dlg.configure(bg="#ECECEC")

            tk.Label(dlg, text="Senha atual:", bg="#ECECEC").pack(
                anchor="w", padx=12, pady=(12, 2))
            cur = tk.Entry(dlg, show="*", width=28)
            cur.pack(padx=12)

            tk.Label(dlg, text="Nova senha (5 dígitos):", bg="#ECECEC").pack(
                anchor="w", padx=12, pady=(8, 2))
            novo = tk.Entry(dlg, show="*", width=28)
            novo.pack(padx=12)

            tk.Label(dlg, text="Confirmar nova senha:", bg="#ECECEC").pack(
                anchor="w", padx=12, pady=(8, 2))
            conf = tk.Entry(dlg, show="*", width=28)
            conf.pack(padx=12)

            def aplicar():
                cur_v = cur.get().strip()
                novo_v = novo.get().strip()
                conf_v = conf.get().strip()
                if not cur_v or not novo_v or not conf_v:
                    messagebox.showerror(
                        "Erro", "Preencha todos os campos.", parent=dlg)
                    return
                if not is_valid_password(novo_v):
                    messagebox.showerror(
                        "Erro", "Nova senha inválida (5 dígitos).", parent=dlg)
                    return
                if novo_v != conf_v:
                    messagebox.showerror(
                        "Erro", "Confirmação não confere.", parent=dlg)
                    return

                stored = self.users[self.ra].get("senha", "")
                if is_hashed(stored):
                    if hash_pw(cur_v) != stored:
                        messagebox.showerror(
                            "Erro", "Senha atual incorreta.", parent=dlg)
                        return
                else:
                    if cur_v != stored:
                        messagebox.showerror(
                            "Erro", "Senha atual incorreta.", parent=dlg)
                        return

                self.users[self.ra]["senha"] = hash_pw(novo_v)
                save_json(ALUNOS_FILE, self.users)
                messagebox.showinfo(
                    "Sucesso", "Senha alterada com sucesso.", parent=dlg)
                dlg.destroy()

            tk.Button(dlg, text="Aplicar", command=aplicar,
                      bg="#6C5CE7", fg="white", width=20).pack(pady=12)

        tk.Button(win, text="Alterar Senha", command=alterar_senha, bg="#6C5CE7",
                  fg="white", font=("Arial", 11, "bold"), relief="flat").pack(pady=8)

# Login / Cadastro Professor


class LoginProfFrame(tk.Frame):
    def __init__(self, master, users, on_login_success, on_register, on_back):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.on_login_success = on_login_success
        self.on_register = on_register
        self.on_back = on_back

        tk.Label(self, text="Login do Professor", font=(
            "Arial", 22, "bold"), bg=self["bg"], fg="#242964").pack(pady=(60, 8))
        tk.Label(self, text="Use seu e-mail institucional",
                 bg=self["bg"], fg="#242964").pack(pady=(0, 8))

        self.email_entry = self._entry_with_placeholder(
            "E-mail institucional (prof)")
        self.pw_entry = self._entry_with_placeholder(
            "Senha (5 dígitos)", is_password=True)
        self._attach_digit_limiter(self.pw_entry, 5)

        self.email_entry.pack(pady=8, ipady=6)
        self.pw_entry.pack(pady=8, ipady=6)

        tk.Button(self, text="Entrar", command=self._login, bg="#0984E3", fg="white", font=(
            "Arial", 11, "bold"), relief="flat", width=24).pack(pady=(16, 8))
        tk.Button(self, text="Criar conta de professor", command=self.on_register,
                  bg=self["bg"], fg="#0984E3", font=("Arial", 10, "bold"), relief="flat").pack(pady=4)
        tk.Button(self, text="Voltar", command=self.on_back, bg="#DCDDE1",
                  fg="#242964", font=("Arial", 10, "bold"), relief="flat").pack(pady=8)

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
        if not user:
            messagebox.showerror("Erro", "E-mail não cadastrado.")
            return

        stored = user.get("senha", "")
        if is_hashed(stored):
            if hash_pw(pw) != stored:
                messagebox.showerror("Erro", "E-mail ou senha incorretos.")
                return
        else:
            if stored != pw:
                messagebox.showerror("Erro", "E-mail ou senha incorretos.")
                return
            self.users[email]["senha"] = hash_pw(pw)
            save_json(PROFESSORES_FILE, self.users)

        messagebox.showinfo("Bem-vindo", f"Olá, Prof(a). {user.get('nome')}!")
        self.on_login_success(email)


class RegisterProfFrame(tk.Frame):
    def __init__(self, master, users, on_done):
        super().__init__(master, bg=master["bg"])
        self.users = users
        self.on_done = on_done

        tk.Label(self, text="Cadastro de Professor", font=(
            "Arial", 22, "bold"), bg=self["bg"], fg="#242964").pack(pady=(30, 8))
        tk.Label(self, text="Insira seus dados institucionais",
                 bg=self["bg"], fg="#242964").pack(pady=(0, 6))

        self.nome = self._entry("Nome completo")
        self.email = self._entry("E-mail institucional (prof)")
        self.senha = self._entry("Senha (5 dígitos)", is_password=True)
        self.disciplina = self._entry("Disciplina (ex: Programação I)")

        for w in (self.nome, self.email, self.senha, self.disciplina):
            w.pack(pady=6, ipady=6)

        self._attach_digit_limiter(self.senha, 5)

        tk.Button(self, text="Validar & Salvar", command=self._salvar, bg="#0984E3", fg="white", font=(
            "Arial", 11, "bold"), relief="flat", width=26).pack(pady=(12, 8))
        tk.Button(self, text="Voltar", command=self.on_done, bg="#DCDDE1",
                  fg="#242964", font=("Arial", 10, "bold"), relief="flat").pack(pady=2)

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
                             "senha": hash_pw(pw), "disciplina": disc}
        save_json(PROFESSORES_FILE, self.users)
        messagebox.showinfo("Sucesso", "Cadastro de professor realizado!")
        self.on_done()

# Portal do Professor


class PortalProfFrame(tk.Frame):
    def __init__(self, master, users_prof, email, alunos, on_logout):
        super().__init__(master, bg=master["bg"])
        self.users_prof = users_prof
        self.email = email
        self.alunos = alunos
        self.on_logout = on_logout

        prof = users_prof.get(email, {})
        nome = prof.get("nome", "Professor")
        disc = prof.get("disciplina", "—")

        tk.Label(self, text="Portal do Professor", font=(
            "Arial", 20, "bold"), bg=self["bg"], fg="#242964").pack(pady=12)
        tk.Label(self, text=f"Prof(a). {nome} — Disciplina: {disc}", font=(
            "Arial", 12), bg=self["bg"], fg="#242964").pack(pady=(0, 12))

        # Menu de ações do professor
        actions = [
            ("👤 Meu Cadastro", self._meu_cadastro),
            ("📝 Gerenciar Notas", self._gerenciar_notas),
            ("📅 Gerenciar Faltas & Chamada", self._gerenciar_faltas),
            ("📆 Alterar Cronograma / Diário", self._alterar_cronograma),
            ("📄 Ver Atestados Recebidos", self._ver_atestados)
        ]
        for txt, cmd in actions:
            tk.Button(self, text=txt, command=cmd, bg="#6C5CE7", fg="white", font=(
                "Arial", 11, "bold"), relief="flat", width=32).pack(pady=6)

        # Novo: botão que abre janela com alunos filtrados pela disciplina do professor
        tk.Button(self, text="👨‍🎓 Ver Alunos Cadastrados", command=self._ver_alunos, bg="#6C5",
                  fg="white", font=("Arial", 11, "bold"), relief="flat", width=32).pack(pady=6)

        # Treeview removido da tela principal para deixar mais limpa (substituído pelo botão acima)

        tk.Button(self, text="🚪 Sair", command=self.on_logout, bg="#DCDDE1", fg="#242964", font=(
            "Arial", 11, "bold"), relief="flat", width=18).pack(pady=10)

    # Área de meu cadastro (professor: alteração de senha, email e disciplina)
    def _meu_cadastro(self):
        prof = self.users_prof.get(self.email, {})
        win = tk.Toplevel(self)
        win.title("Meu Cadastro - Professor")
        win.geometry("480x320")
        win.configure(bg="#ECECEC")

        tk.Label(win, text="Editar Informações do Perfil", font=(
            "Arial", 14, "bold"), bg="#ECECEC").pack(pady=8)
        frm = tk.Frame(win, bg="#ECECEC")
        frm.pack(padx=12, pady=6, fill="x")

        tk.Label(frm, text="Nome:", bg="#ECECEC").grid(
            row=0, column=0, sticky="w")
        nome_e = tk.Entry(frm, width=36)
        nome_e.grid(row=0, column=1, pady=6)
        nome_e.insert(0, prof.get("nome", ""))

        tk.Label(frm, text="E-mail (institucional):",
                 bg="#ECECEC").grid(row=1, column=0, sticky="w")
        email_e = tk.Entry(frm, width=36)
        email_e.grid(row=1, column=1, pady=6)
        email_e.insert(0, prof.get("email", ""))

        tk.Label(frm, text="Disciplina:", bg="#ECECEC").grid(
            row=2, column=0, sticky="w")
        disc_e = tk.Entry(frm, width=36)
        disc_e.grid(row=2, column=1, pady=6)
        disc_e.insert(0, prof.get("disciplina", ""))

        def salvar_dados():
            novo_nome = nome_e.get().strip()
            novo_email = email_e.get().strip().lower()
            nova_disc = disc_e.get().strip()
            if not novo_nome or not novo_email or not nova_disc:
                messagebox.showerror(
                    "Erro", "Preencha todos os campos.", parent=win)
                return
            if not is_valid_prof_email(novo_email):
                dlist = ", ".join(f"@{d}" for d in PROFESSOR_DOMAINS)
                messagebox.showerror(
                    "Erro", f"E-mail deve ser institucional ({dlist}).", parent=win)
                return
            # mover registro se o email mudou (chave do dict)
            if novo_email != self.email:
                if novo_email in self.users_prof:
                    messagebox.showerror(
                        "Erro", "E-mail já cadastrado por outro usuário.", parent=win)
                    return
                # transferir dados
                self.users_prof[novo_email] = self.users_prof.pop(self.email)
                self.users_prof[novo_email]["nome"] = novo_nome
                self.users_prof[novo_email]["email"] = novo_email
                self.users_prof[novo_email]["disciplina"] = nova_disc
                save_json(PROFESSORES_FILE, self.users_prof)
                messagebox.showinfo(
                    "Sucesso", "Dados atualizados. Faça login novamente com o novo e-mail.", parent=win)
                win.destroy()
                self.on_logout()
            else:
                self.users_prof[self.email]["nome"] = novo_nome
                self.users_prof[self.email]["disciplina"] = nova_disc
                save_json(PROFESSORES_FILE, self.users_prof)
                messagebox.showinfo(
                    "Sucesso", "Dados atualizados.", parent=win)
                win.destroy()

        def alterar_senha_prof():
            dlg = tk.Toplevel(win)
            dlg.title("Alterar Senha - Professor")
            dlg.geometry("360x220")
            dlg.configure(bg="#ECECEC")

            tk.Label(dlg, text="Senha atual:", bg="#ECECEC").pack(
                anchor="w", padx=12, pady=(12, 2))
            cur = tk.Entry(dlg, show="*", width=28)
            cur.pack(padx=12)

            tk.Label(dlg, text="Nova senha (5 dígitos):", bg="#ECECEC").pack(
                anchor="w", padx=12, pady=(8, 2))
            novo = tk.Entry(dlg, show="*", width=28)
            novo.pack(padx=12)

            tk.Label(dlg, text="Confirmar nova senha:", bg="#ECECEC").pack(
                anchor="w", padx=12, pady=(8, 2))
            conf = tk.Entry(dlg, show="*", width=28)
            conf.pack(padx=12)

            def aplicar():
                cur_v = cur.get().strip()
                novo_v = novo.get().strip()
                conf_v = conf.get().strip()
                if not cur_v or not novo_v or not conf_v:
                    messagebox.showerror(
                        "Erro", "Preencha todos os campos.", parent=dlg)
                    return
                if not is_valid_password(novo_v):
                    messagebox.showerror(
                        "Erro", "Nova senha inválida (5 dígitos).", parent=dlg)
                    return
                if novo_v != conf_v:
                    messagebox.showerror(
                        "Erro", "Confirmação não confere.", parent=dlg)
                    return

                stored = self.users_prof[self.email].get("senha", "")
                if is_hashed(stored):
                    if hash_pw(cur_v) != stored:
                        messagebox.showerror(
                            "Erro", "Senha atual incorreta.", parent=dlg)
                        return
                else:
                    if cur_v != stored:
                        messagebox.showerror(
                            "Erro", "Senha atual incorreta.", parent=dlg)
                        return

                self.users_prof[self.email]["senha"] = hash_pw(novo_v)
                save_json(PROFESSORES_FILE, self.users_prof)
                messagebox.showinfo(
                    "Sucesso", "Senha alterada com sucesso.", parent=dlg)
                dlg.destroy()

            tk.Button(dlg, text="Aplicar", command=aplicar,
                      bg="#6C5CE7", fg="white", width=20).pack(pady=12)

        tk.Button(win, text="Salvar Dados", command=salvar_dados,
                  bg="#0984E3", fg="white", width=20).pack(pady=6)
        tk.Button(win, text="Alterar Senha", command=alterar_senha_prof,
                  bg="#6C5CE7", fg="white", width=20).pack(pady=6)

    #  Área de gerenciamento de atestados enviados pelo aluno
    def _ver_atestados(self):
        faltas_data = load_json(FALTAS_FILE)
        win = tk.Toplevel(self)
        win.title("Atestados Recebidos")
        win.geometry("720x420")
        win.configure(bg="#ECECEC")

        tk.Label(win, text="Atestados Recebidos de Alunos",
                 bg="#ECECEC", font=("Arial", 14, "bold")).pack(pady=8)

        tree = ttk.Treeview(win, columns=(
            "ra", "nome", "data", "arquivo"), show="headings", height=12)
        tree.heading("ra", text="RA")
        tree.heading("nome", text="Aluno")
        tree.heading("data", text="Data do Envio")
        tree.heading("arquivo", text="Arquivo")
        tree.column("ra", width=100, anchor="center")
        tree.column("nome", width=220)
        tree.column("data", width=160)
        tree.column("arquivo", width=220)
        tree.pack(padx=12, pady=6, fill="both", expand=True)

        for ra, dados in sorted(faltas_data.items()):
            aluno = self.alunos.get(ra, {"nome": "Desconhecido"})
            for at in dados.get("atestados", []):
                tree.insert("", "end", values=(ra, aluno.get("nome", "—"), at.get(
                    "data", ""), os.path.basename(at.get("arquivo", ""))))

        def on_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0], "values")
            ra_sel, nome_sel, data_sel, arquivo_sel = vals
            dados = faltas_data.get(ra_sel, {})
            caminho_full = None
            for at in dados.get("atestados", []):
                if os.path.basename(at.get("arquivo", "")) == arquivo_sel and at.get("data", "") == data_sel:
                    caminho_full = at.get("arquivo")
                    break
            if caminho_full and os.path.exists(caminho_full):
                try:
                    if os.name == "nt":
                        os.startfile(caminho_full)
                    elif os.name == "posix":
                        try:
                            os.system(f"open \"{caminho_full}\"")
                        except Exception:
                            os.system(f"xdg-open \"{caminho_full}\"")
                    else:
                        messagebox.showinfo(
                            "Arquivo", f"Caminho: {caminho_full}")
                except Exception as e:
                    messagebox.showinfo(
                        "Arquivo", f"Caminho: {caminho_full}\n(Erro ao abrir: {e})")
            else:
                messagebox.showinfo(
                    "Arquivo", f"Arquivo não encontrado localmente.\nNome: {arquivo_sel}\nAluno: {nome_sel}\nData: {data_sel}")

        tree.bind("<Double-1>", on_double_click)
        tk.Button(win, text="Fechar", command=win.destroy, bg="#DCDDE1", fg="#242964", font=(
            "Arial", 11, "bold"), relief="flat", width=18).pack(pady=10)

    #  Ver Alunos cadastrados na disciplina
    def _ver_alunos(self):
        alunos_all = load_json(ALUNOS_FILE)
        # key = RA, value = list of dicts with 'nome'
        disciplinas_por_ra = load_json(DISCIPLINAS_FILE)
        prof = self.users_prof.get(self.email, {})
        minha_disc = prof.get("disciplina", "").strip()

        win = tk.Toplevel(self)
        win.title("Alunos Cadastrados (Minha Disciplina)")
        win.geometry("720x420")
        win.configure(bg="#ECECEC")

        tk.Label(win, text=f"Alunos vinculados à disciplina: {minha_disc}", bg="#ECECEC", font=(
            "Arial", 14, "bold")).pack(pady=8)

        tree = ttk.Treeview(win, columns=(
            "ra", "nome", "email", "disciplinas"), show="headings", height=15)
        tree.heading("ra", text="RA")
        tree.heading("nome", text="Nome")
        tree.heading("email", text="E-mail")
        tree.heading("disciplinas", text="Disciplinas")
        tree.column("ra", width=100, anchor="center")
        tree.column("nome", width=220)
        tree.column("email", width=220)
        tree.column("disciplinas", width=240)
        tree.pack(padx=10, pady=6, fill="both", expand=True)

        # Filtrar alunos que tenham esta disciplina no DISCIPLINAS_FILE
        for ra, dados in sorted(alunos_all.items()):
            disciplinas_do_aluno = disciplinas_por_ra.get(ra, [])
            # disciplinas_do_aluno pode ser lista de dicts com 'nome'
            nomes = []
            tem = False
            for d in disciplinas_do_aluno:
                nome_d = d.get("nome") if isinstance(d, dict) else str(d)
                if nome_d:
                    nomes.append(nome_d)
                    if nome_d == minha_disc:
                        tem = True
            if tem:
                tree.insert("", "end", values=(ra, dados.get(
                    "nome", "-"), dados.get("email", "-"), ", ".join(nomes)))

        tk.Button(win, text="Fechar", command=win.destroy, bg="#DCDDE1", fg="#242964", font=(
            "Arial", 11, "bold"), relief="flat", width=18).pack(pady=10)

    # Gerenciamento de Notas
    def _gerenciar_notas(self):
        notas_data = load_json(NOTAS_FILE)
        win = tk.Toplevel(self)
        win.title("Gerenciamento de Notas")
        win.geometry("760x520")
        win.configure(bg="#ECECEC")

        tk.Label(win, text="Gerenciar Notas dos Alunos", font=(
            "Arial", 14, "bold"), bg="#ECECEC").pack(pady=8)

        prof = self.users_prof.get(self.email, {})
        default_disc = prof.get("disciplina", "")
        tk.Label(win, text="Disciplina:", bg="#ECECEC").pack(
            anchor="w", padx=12)
        disc_cb = ttk.Combobox(win, values=[default_disc], state="readonly")
        disc_cb.set(default_disc)
        disc_cb.pack(padx=12, pady=4, anchor="w")

        cols = ("RA", "Nome", "P1", "P2")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("RA", width=100, anchor="center")
        tree.column("Nome", width=260)
        tree.column("P1", width=80, anchor="center")
        tree.column("P2", width=80, anchor="center")
        tree.pack(padx=12, pady=8, fill="both", expand=True)

        def carregar_lista():
            for i in tree.get_children():
                tree.delete(i)
            alunos_all = load_json(ALUNOS_FILE)
            for ra, aluno in sorted(alunos_all.items()):
                notas_aluno = notas_data.get(ra, {})
                disc = disc_cb.get()
                vals = notas_aluno.get(disc, {})
                p1 = vals.get("P1", "-")
                p2 = vals.get("P2", "-")
                tree.insert("", "end", values=(
                    ra, aluno.get("nome", "-"), p1, p2))

        carregar_lista()

        frm = tk.Frame(win, bg="#ECECEC")
        frm.pack(padx=12, pady=6, anchor="w")
        tk.Label(frm, text="RA do Aluno:", bg="#ECECEC").grid(
            row=0, column=0, sticky="w")
        ra_e = tk.Entry(frm, width=18)
        ra_e.grid(row=0, column=1, padx=6)
        tk.Label(frm, text="P1:", bg="#ECECEC").grid(
            row=0, column=2, sticky="w")
        p1_e = tk.Entry(frm, width=8)
        p1_e.grid(row=0, column=3, padx=6)
        tk.Label(frm, text="P2:", bg="#ECECEC").grid(
            row=0, column=4, sticky="w")
        p2_e = tk.Entry(frm, width=8)
        p2_e.grid(row=0, column=5, padx=6)

        def postar_notas():
            ra_v = ra_e.get().strip().upper()
            p1_v = p1_e.get().strip()
            p2_v = p2_e.get().strip()
            disc = disc_cb.get()
            if not ra_v or (not p1_v and not p2_v):
                messagebox.showerror(
                    "Erro", "Informe RA e ao menos uma nota.", parent=win)
                return
            alunos_all = load_json(ALUNOS_FILE)
            if ra_v not in alunos_all:
                messagebox.showerror("Erro", "RA não encontrado.", parent=win)
                return
            notas_data.setdefault(ra_v, {})
            notas_data[ra_v].setdefault(disc, {})
            if p1_v:
                try:
                    notas_data[ra_v][disc]["P1"] = float(p1_v)
                except:
                    messagebox.showerror(
                        "Erro", "P1 deve ser número.", parent=win)
                    return
            if p2_v:
                try:
                    notas_data[ra_v][disc]["P2"] = float(p2_v)
                except:
                    messagebox.showerror(
                        "Erro", "P2 deve ser número.", parent=win)
                    return
            save_json(NOTAS_FILE, notas_data)
            messagebox.showinfo("Sucesso", "Nota(s) postada(s).", parent=win)
            carregar_lista()

        def editar_selecionado():
            sel = tree.selection()
            if not sel:
                messagebox.showerror(
                    "Erro", "Selecione um aluno na lista.", parent=win)
                return
            vals = tree.item(sel[0], "values")
            ra_e.delete(0, tk.END)
            ra_e.insert(0, vals[0])
            p1_e.delete(0, tk.END)
            p1_e.insert(0, vals[2])
            p2_e.delete(0, tk.END)
            p2_e.insert(0, vals[3])

        tk.Button(frm, text="Postar / Atualizar Notas", command=postar_notas,
                  bg="#0984E3", fg="white").grid(row=0, column=6, padx=8)
        tk.Button(frm, text="Editar Selecionado", command=editar_selecionado,
                  bg="#6C5CE7", fg="white").grid(row=0, column=7, padx=4)

        def ver_revisoes():
            revisoes = load_json(REVISOES_FILE)
            win2 = tk.Toplevel(win)
            win2.title("Solicitações de Revisão")
            win2.geometry("520x360")
            win2.configure(bg="#ECECEC")
            tree2 = ttk.Treeview(win2, columns=(
                "ra", "disc", "prova", "data"), show="headings", height=12)
            for h, w in [("ra", 100), ("disc", 200), ("prova", 80), ("data", 180)]:
                tree2.heading(h, text=h.upper())
                tree2.column(h, width=w)
            tree2.pack(padx=12, pady=8, fill="both", expand=True)
            for ra, itens in revisoes.items():
                for it in itens:
                    tree2.insert("", "end", values=(ra, it.get(
                        "disciplina", ""), it.get("prova", ""), it.get("data", "")))
            tk.Button(win2, text="Fechar", command=win2.destroy).pack(pady=8)
        tk.Button(win, text="Visualizar Solicitações de Revisão",
                  command=ver_revisoes, bg="#DCDDE1").pack(pady=6)

    # Gerenciamento de faltas e frequência
    def _gerenciar_faltas(self):
        faltas_data = load_json(FALTAS_FILE)
        win = tk.Toplevel(self)
        win.title("Gerenciamento de Faltas e Chamada")
        win.geometry("820x520")
        win.configure(bg="#ECECEC")
        tk.Label(win, text="Gerenciar Faltas e Registrar Aula (Chamada)",
                 font=("Arial", 14, "bold"), bg="#ECECEC").pack(pady=8)

        cols = ("RA", "Nome", "Faltas", "Presenças",
                "Total Aulas", "Frequência")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("RA", width=100)
        tree.column("Nome", width=260)
        tree.column("Faltas", width=80, anchor="center")
        tree.column("Presenças", width=90, anchor="center")
        tree.column("Total Aulas", width=100, anchor="center")
        tree.column("Frequência", width=100, anchor="center")
        tree.pack(padx=12, pady=8, fill="both", expand=True)

        def atualizar_tree():
            for i in tree.get_children():
                tree.delete(i)
            alunos_all = load_json(ALUNOS_FILE)
            for ra, aluno in sorted(alunos_all.items()):
                reg = faltas_data.get(ra, {})
                faltas = reg.get("faltas", 0)
                pres = reg.get("presencas", 0)
                total = reg.get("total_aulas", 0)
                freq = f"{int((pres/total*100) if total > 0 else 100)}%"
                tree.insert("", "end", values=(ra, aluno.get(
                    "nome", "-"), faltas, pres, total, freq))
        atualizar_tree()

        frm = tk.Frame(win, bg="#ECECEC")
        frm.pack(padx=12, pady=6, anchor="w")
        tk.Label(frm, text="RA:", bg="#ECECEC").grid(
            row=0, column=0, sticky="w")
        ra_e = tk.Entry(frm, width=16)
        ra_e.grid(row=0, column=1, padx=6)
        tk.Label(frm, text="Alterar faltas (número):",
                 bg="#ECECEC").grid(row=0, column=2, sticky="w")
        faltas_e = tk.Entry(frm, width=8)
        faltas_e.grid(row=0, column=3, padx=6)

        def aplicar_faltas():
            ra_v = ra_e.get().strip().upper()
            try:
                novo = int(faltas_e.get().strip())
            except:
                messagebox.showerror(
                    "Erro", "Digite um número inteiro em faltas.", parent=win)
                return
            alunos_all = load_json(ALUNOS_FILE)
            if ra_v not in alunos_all:
                messagebox.showerror("Erro", "RA não encontrado.", parent=win)
                return
            reg = faltas_data.setdefault(
                ra_v, {"faltas": 0, "presencas": 0, "total_aulas": 0, "frequencia": "100%", "atestados": []})
            reg["faltas"] = novo
            total = reg.get("total_aulas", 0)
            pres = max(0, total - reg["faltas"])
            reg["presencas"] = pres
            reg["frequencia"] = f"{int((pres/total*100) if total > 0 else 100)}%"
            faltas_data[ra_v] = reg
            save_json(FALTAS_FILE, faltas_data)
            messagebox.showinfo("Sucesso", "Faltas atualizadas.", parent=win)
            atualizar_tree()

        tk.Button(frm, text="Aplicar Faltas", command=aplicar_faltas,
                  bg="#6C5CE7", fg="white").grid(row=0, column=4, padx=8)

        # Registrar aula (chamada)
        sep = ttk.Separator(win, orient="horizontal")
        sep.pack(fill="x", pady=6)
        tk.Label(win, text="Registrar Aula (Chamada)", bg="#ECECEC",
                 font=("Arial", 12, "bold")).pack(pady=6)
        cham_frm = tk.Frame(win, bg="#ECECEC")
        cham_frm.pack(padx=12, pady=6, fill="x")
        tk.Label(cham_frm, text="Data (DD/MM/AAAA):",
                 bg="#ECECEC").grid(row=0, column=0, sticky="w")
        data_e = tk.Entry(cham_frm, width=14)
        data_e.grid(row=0, column=1, padx=6)
        data_e.insert(0, datetime.now().strftime("%d/%m/%Y"))
        tk.Label(cham_frm, text="Conteúdo da aula:",
                 bg="#ECECEC").grid(row=0, column=2, sticky="w")
        conteudo_e = tk.Entry(cham_frm, width=36)
        conteudo_e.grid(row=0, column=3, padx=6)

        box_win = tk.Frame(win, bg="#ECECEC")
        box_win.pack(padx=12, pady=6, fill="both", expand=False)
        canvas = tk.Canvas(box_win, height=140, bg="#ECECEC")
        sb = tk.Scrollbar(box_win, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#ECECEC")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        checks = {}
        alunos_all = load_json(ALUNOS_FILE)
        for i, (ra, aluno) in enumerate(sorted(alunos_all.items())):
            var = tk.IntVar(value=1)
            cb = tk.Checkbutton(
                inner, text=f"{ra} — {aluno.get('nome', '')}", variable=var, bg="#ECECEC", anchor="w")
            cb.pack(anchor="w")
            checks[ra] = var

        def registrar_aula():
            data_v = data_e.get().strip()
            conteudo_v = conteudo_e.get().strip()
            try:
                datetime.strptime(data_v, "%d/%m/%Y")
            except Exception:
                messagebox.showerror(
                    "Erro", "Data inválida. Use DD/MM/AAAA.", parent=win)
                return
            diario = load_json(DIARIO_FILE)
            disc = self.users_prof.get(self.email, {}).get("disciplina", "—")
            diario.setdefault(disc, []).append({
                "data": data_v,
                "conteudo": conteudo_v,
                "registro": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            faltas_data_local = load_json(FALTAS_FILE)
            for ra, var in checks.items():
                reg = faltas_data_local.setdefault(
                    ra, {"faltas": 0, "presencas": 0, "total_aulas": 0, "frequencia": "100%", "atestados": []})
                reg["total_aulas"] = reg.get("total_aulas", 0) + 1
                if var.get() == 1:
                    reg["presencas"] = reg.get("presencas", 0) + 1
                else:
                    reg["faltas"] = reg.get("faltas", 0) + 1
                total = reg["total_aulas"]
                pres = reg["presencas"]
                reg["frequencia"] = f"{int((pres/total*100) if total > 0 else 100)}%"
                faltas_data_local[ra] = reg
            save_json(DIARIO_FILE, diario)
            save_json(FALTAS_FILE, faltas_data_local)
            messagebox.showinfo(
                "Sucesso", "Aula registrada e chamadas atualizadas.", parent=win)
            atualizar_tree()

        tk.Button(win, text="Registrar Aula e Atualizar Chamada",
                  command=registrar_aula, bg="#0984E3", fg="white").pack(pady=8)

    # Cronograma / Diário Eletrônico
    def _alterar_cronograma(self):
        disciplinas = load_json(DISCIPLINAS_FILE)
        win = tk.Toplevel(self)
        win.title("Cronograma e Diário Eletrônico")
        win.geometry("760x520")
        win.configure(bg="#ECECEC")
        tk.Label(win, text="Cronograma / Diário Eletrônico",
                 font=("Arial", 14, "bold"), bg="#ECECEC").pack(pady=8)

        prof = self.users_prof.get(self.email, {})
        disc = prof.get("disciplina", "")

        tk.Label(win, text=f"Cronograma da disciplina: {disc}", bg="#ECECEC").pack(
            anchor="w", padx=12)
        tree = ttk.Treeview(win, columns=(
            "dia", "horario", "info"), show="headings", height=8)
        tree.heading("dia", text="Dia")
        tree.heading("horario", text="Horário")
        tree.heading("info", text="Info")
        tree.column("dia", width=120)
        tree.column("horario", width=140)
        tree.column("info", width=420)
        tree.pack(padx=12, pady=8, fill="x")

        def carregar_cron():
            for i in tree.get_children():
                tree.delete(i)
            for item in disciplinas.get(self.email, []):
                tree.insert("", "end", values=(item.get("dia", ""),
                            item.get("horario", ""), item.get("nome", "")))
        carregar_cron()

        frm = tk.Frame(win, bg="#ECECEC")
        frm.pack(padx=12, pady=6, fill="x")
        tk.Label(frm, text="Nome da Aula/Atividade:",
                 bg="#ECECEC").grid(row=0, column=0, sticky="w")
        nome_e = tk.Entry(frm, width=30)
        nome_e.grid(row=0, column=1, padx=6)
        tk.Label(frm, text="Dia:", bg="#ECECEC").grid(
            row=0, column=2, sticky="w")
        dia_e = tk.Entry(frm, width=12)
        dia_e.grid(row=0, column=3, padx=6)
        tk.Label(frm, text="Horário:", bg="#ECECEC").grid(
            row=0, column=4, sticky="w")
        hor_e = tk.Entry(frm, width=12)
        hor_e.grid(row=0, column=5, padx=6)

        def adicionar_aula():
            nome_v = nome_e.get().strip()
            dia_v = dia_e.get().strip()
            hor_v = hor_e.get().strip()
            if not nome_v or not dia_v or not hor_v:
                messagebox.showerror(
                    "Erro", "Preencha todos os campos.", parent=win)
                return
            disciplinas.setdefault(self.email, []).append(
                {"nome": nome_v, "dia": dia_v, "horario": hor_v})
            save_json(DISCIPLINAS_FILE, disciplinas)
            carregar_cron()
            messagebox.showinfo(
                "Sucesso", "Aula adicionada ao cronograma.", parent=win)

        tk.Button(frm, text="Adicionar Aula Semanal", command=adicionar_aula,
                  bg="#6C5CE7", fg="white").grid(row=0, column=6, padx=8)

        sep = ttk.Separator(win, orient="horizontal")
        sep.pack(fill="x", pady=6)
        cont_fr = tk.Frame(win, bg="#ECECEC")
        cont_fr.pack(padx=12, pady=6, fill="x")
        tk.Label(cont_fr, text="Registrar Prova/Avaliação (data DD/MM/AAAA):",
                 bg="#ECECEC").grid(row=0, column=0, sticky="w")
        data_e = tk.Entry(cont_fr, width=14)
        data_e.grid(row=0, column=1, padx=6)
        data_e.insert(0, datetime.now().strftime("%d/%m/%Y"))
        tk.Label(cont_fr, text="Descrição:", bg="#ECECEC").grid(
            row=0, column=2, sticky="w")
        desc_e = tk.Entry(cont_fr, width=36)
        desc_e.grid(row=0, column=3, padx=6)

        def registrar_prova():
            d = data_e.get().strip()
            desc = desc_e.get().strip()
            try:
                datetime.strptime(d, "%d/%m/%Y")
            except:
                messagebox.showerror("Erro", "Data inválida.", parent=win)
                return
            diario = load_json(DIARIO_FILE)
            diario.setdefault(disc, []).append(
                {"data": d, "conteudo": f"[Avaliação] {desc}", "registro": datetime.now().strftime("%d/%m/%Y %H:%M")})
            save_json(DIARIO_FILE, diario)
            messagebox.showinfo(
                "Sucesso", "Prova/avaliação registrada no diário.", parent=win)

        tk.Button(cont_fr, text="Registrar Prova/Avaliação", command=registrar_prova,
                  bg="#0984E3", fg="white").grid(row=0, column=4, padx=8)

        sep2 = ttk.Separator(win, orient="horizontal")
        sep2.pack(fill="x", pady=6)
        tk.Label(win, text="Diário Eletrônico (visualizar):",
                 bg="#ECECEC").pack(anchor="w", padx=12)
        diario_tree = ttk.Treeview(win, columns=(
            "data", "conteudo", "registro"), show="headings", height=8)
        diario_tree.heading("data", text="Data")
        diario_tree.heading("conteudo", text="Conteúdo")
        diario_tree.heading("registro", text="Registro")
        diario_tree.column("data", width=120)
        diario_tree.column("conteudo", width=420)
        diario_tree.column("registro", width=180)
        diario_tree.pack(padx=12, pady=8, fill="both", expand=True)

        def carregar_diario():
            for i in diario_tree.get_children():
                diario_tree.delete(i)
            diario = load_json(DIARIO_FILE)
            for item in diario.get(disc, []):
                diario_tree.insert("", "end", values=(
                    item.get("data", ""), item.get("conteudo", ""), item.get("registro", "")))
        carregar_diario()
        tk.Button(win, text="Atualizar Diário", command=carregar_diario,
                  bg="#6C5CE7", fg="white").pack(pady=6)


# Execução
if __name__ == "__main__":
    # cria arquivos vazios básicos se não existirem (opcional)
    for fn in (ALUNOS_FILE, PROFESSORES_FILE, DISCIPLINAS_FILE, NOTAS_FILE, FALTAS_FILE, REVISOES_FILE, DIARIO_FILE):
        if not os.path.exists(fn):
            save_json(fn, {})

    app = PortalApp()
    app.mainloop()
