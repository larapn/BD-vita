import tkinter as tk
from tkinter import Toplevel, Listbox, Entry, Label, Button, messagebox, ttk, Frame
from PIL import Image, ImageTk
import mysql.connector



def create_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Lara33253240",
            database="vita"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao banco de dados: {err}")
        return None

def mostrar_pessoas():
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            cursor.execute("""
                SELECT p.nome, 
                       CASE 
                         WHEN pa.cpf IS NOT NULL THEN 'Paciente'
                         WHEN m.id_funcionario IS NOT NULL THEN 'Médico'
                         WHEN e.id_funcionario IS NOT NULL THEN 'Enfermeiro'
                         ELSE 'Desconhecido'
                       END as tipo
                FROM pessoa p
                LEFT JOIN paciente pa ON p.cpf = pa.cpf
                LEFT JOIN funcionario f ON p.cpf = f.cpf
                LEFT JOIN medico m ON f.id_funcionario = m.id_funcionario
                LEFT JOIN enfermeiro e ON f.id_funcionario = e.id_funcionario
            """)
            resultado = cursor.fetchall()
            lista_pessoas.delete(0, tk.END)
            for linha in resultado:
                lista_pessoas.insert(tk.END, f"{linha[0]} - {linha[1]}")
        except mysql.connector.Error as err:
            print(f"Erro ao buscar dados: {err}")
        finally:
            cursor.close()
            con.close()

def on_pessoa_select(event):
    widget = event.widget
    index = int(widget.curselection()[0])
    nome_pessoa = widget.get(index)
    mostrar_detalhes_pessoa(nome_pessoa)

def mostrar_detalhes_pessoa(nome_pessoa):
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            cursor.execute("SELECT * FROM pessoa WHERE nome = %s", (nome_pessoa,))
            pessoa = cursor.fetchone()
            if pessoa:
                detalhes_window = Toplevel(root)
                detalhes_window.title(f"Detalhes de {nome_pessoa}")

               
                for col, val in zip(["CPF", "Nome", "Data Nascimento", "Telefone", "Endereço", "Bairro", "Estado"], pessoa):
                    Label(detalhes_window, text=f"{col}: {val}").pack()

                
                Button(detalhes_window, text="Alterar Dados", command=lambda: alterar_dados_pessoa(pessoa)).pack()
        except mysql.connector.Error as err:
            print(f"Erro ao buscar dados: {err}")
        finally:
            cursor.close()
            con.close()

def alterar_dados_pessoa(pessoa):
    cpf_original = pessoa[0]  
    alterar_window = Toplevel(root)
    alterar_window.title("Alterar Dados da Pessoa")

    
    labels = ["CPF", "Nome", "Data Nascimento", "Telefone", "Endereço", "Bairro", "Estado"]
    entries = {}
    for i, label in enumerate(labels):
        Label(alterar_window, text=label).pack()
        entry = Entry(alterar_window)
        entry.insert(0, pessoa[i])  
        entry.pack()
        entries[label] = entry

    def salvar_alteracoes():
        dados_atualizados = {label: entries[label].get() for label in labels}
        con = create_db_connection()
        if con is not None:
            cursor = con.cursor()
            try:
                query = """UPDATE pessoa SET cpf = %s, nome = %s, data_nascimento = %s, telefone = %s, 
                           endereco = %s, bairro = %s, estado = %s WHERE cpf = %s"""
                cursor.execute(query, (dados_atualizados["CPF"], dados_atualizados["Nome"], dados_atualizados["Data Nascimento"], 
                                       dados_atualizados["Telefone"], dados_atualizados["Endereço"], 
                                       dados_atualizados["Bairro"], dados_atualizados["Estado"], cpf_original))
                con.commit()
                print("Dados atualizados com sucesso!")
            except mysql.connector.Error as err:
                print(f"Erro ao atualizar dados: {err}")
            finally:
                cursor.close()
                con.close()
        alterar_window.destroy()

    
    Button(alterar_window, text="Salvar Alterações", command=salvar_alteracoes).pack()

def adicionar_pessoa():
    add_window = Toplevel(root)
    add_window.title("Adicionar Pessoa")

    
    Label(add_window, text="CPF").pack()
    entry_cpf = Entry(add_window)
    entry_cpf.pack()

    Label(add_window, text="Nome").pack()
    entry_nome = Entry(add_window)
    entry_nome.pack()

    Label(add_window, text="Data de Nascimento").pack()
    entry_data_nascimento = Entry(add_window)
    entry_data_nascimento.pack()

    Label(add_window, text="Telefone").pack()
    entry_telefone = Entry(add_window)
    entry_telefone.pack()

    Label(add_window, text="Endereço").pack()
    entry_endereco = Entry(add_window)
    entry_endereco.pack()

    Label(add_window, text="Bairro").pack()
    entry_bairro = Entry(add_window)
    entry_bairro.pack()

    Label(add_window, text="Estado").pack()
    entry_estado = Entry(add_window)
    entry_estado.pack()

    def salvar_pessoa():
        con = create_db_connection()
        if con is not None:
            cursor = con.cursor()
            try:
                query = """INSERT INTO pessoa (cpf, nome, data_nascimento, telefone, endereco, bairro, estado) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cpf = entry_cpf.get()
                cursor.execute(query, (cpf, entry_nome.get(), entry_data_nascimento.get(), 
                                    entry_telefone.get(), entry_endereco.get(), entry_bairro.get(), 
                                    entry_estado.get()))
                con.commit()
                print("Pessoa adicionada com sucesso!")
                pedir_tipo_pessoa(cpf)  
            except mysql.connector.Error as err:
                print(f"Erro ao adicionar pessoa: {err}")
            finally:
                cursor.close()
                con.close()
            add_window.destroy()

    Button(add_window, text="Salvar", command=salvar_pessoa).pack()

    def pedir_tipo_pessoa(cpf):
        tipo_window = Toplevel(root)
        tipo_window.title("Selecionar Tipo")

        Label(tipo_window, text="Selecione o Tipo:").pack()
        Button(tipo_window, text="Funcionário", command=lambda: adicionar_tipo_funcionario(cpf, tipo_window)).pack()
        Button(tipo_window, text="Paciente", command=lambda: adicionar_tipo_paciente(cpf, tipo_window)).pack()

    def adicionar_tipo_funcionario(cpf, parent_window):
        funcionario_window = Toplevel(root)
        funcionario_window.title("Adicionar Funcionário")

        cargo_var = tk.StringVar()
        Label(funcionario_window, text="Cargo:").pack()
        cargo_menu = ttk.Combobox(funcionario_window, textvariable=cargo_var, values=["Médico", "Enfermeiro"])
        cargo_menu.pack()
        
        medico_frame = Frame(funcionario_window)
        enfermeiro_frame = Frame(funcionario_window)

        Label(medico_frame, text="CRM:").pack()
        crm_entry = Entry(medico_frame)
        crm_entry.pack()
        Label(medico_frame, text="Especialidade:").pack()
        especialidade_entry = Entry(medico_frame)
        especialidade_entry.pack()

        Label(enfermeiro_frame, text="COREN:").pack()
        coren_entry = Entry(enfermeiro_frame)
        coren_entry.pack()
        Label(enfermeiro_frame, text="Setor:").pack()
        setor_entry = Entry(enfermeiro_frame)
        setor_entry.pack()

        def mostrar_campos_por_cargo(event):
            if cargo_var.get() == "Médico":
                enfermeiro_frame.pack_forget()
                medico_frame.pack()
            elif cargo_var.get() == "Enfermeiro":
                medico_frame.pack_forget()
                enfermeiro_frame.pack()

        cargo_menu.bind('<<ComboboxSelected>>', mostrar_campos_por_cargo)


        def salvar_funcionario():
            cargo = cargo_var.get()
            crm = crm_entry.get()
            especialidade = especialidade_entry.get()
            coren = coren_entry.get()
            setor = setor_entry.get()
            salvar_funcionario_bd(cpf, cargo, crm, especialidade, coren, setor)
            funcionario_window.destroy()
            parent_window.destroy()


        Button(funcionario_window, text="Salvar Funcionário", command=salvar_funcionario).pack()

def salvar_funcionario_bd(cpf, cargo, crm, especialidade, coren, setor):
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            cursor.execute("INSERT INTO funcionario (cpf) VALUES (%s)", (cpf,))
            id_funcionario = cursor.lastrowid

            if cargo == "Médico":
                cursor.execute("INSERT INTO medico (crm, especialidade, id_funcionario) VALUES (%s, %s, %s)", (crm, especialidade, id_funcionario))
            elif cargo == "Enfermeiro":
                cursor.execute("INSERT INTO enfermeiro (coren, setor, id_funcionario) VALUES (%s, %s, %s)", (coren, setor, id_funcionario))

            con.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao salvar funcionário: {err}")
            con.rollback()
        finally:
            cursor.close()
            con.close()

def adicionar_tipo_paciente(cpf, parent_window):
    paciente_window = Toplevel(root)
    paciente_window.title("Adicionar Paciente")

    Label(paciente_window, text="Tipo Sanguíneo:").pack()
    tipo_sanguineo_entry = Entry(paciente_window)
    tipo_sanguineo_entry.pack()

    Label(paciente_window, text="Órgão para Transplante:").pack()
    orgao_transplante_entry = Entry(paciente_window)
    orgao_transplante_entry.pack()

    def salvar_paciente():
        tipo_sanguineo = tipo_sanguineo_entry.get()
        orgao_transplante = orgao_transplante_entry.get()
        salvar_paciente_bd(cpf, tipo_sanguineo, orgao_transplante)
        paciente_window.destroy()
        parent_window.destroy()

    Button(paciente_window, text="Salvar Paciente", command=salvar_paciente).pack()
    
def salvar_paciente_bd(cpf, tipo_sanguineo, orgao_transplante):
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            cursor.execute("INSERT INTO paciente (cpf, tipo_sanguineo, orgao_transplante) VALUES (%s, %s, %s)", (cpf, tipo_sanguineo, orgao_transplante))
            con.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao salvar paciente: {err}")
            con.rollback()
        finally:
            cursor.close()
            con.close()
    
def remover_pessoa():
    remove_window = Toplevel(root)
    remove_window.title("Remover Pessoa")

    Label(remove_window, text="CPF").pack()
    entry_cpf = Entry(remove_window)
    entry_cpf.pack()

    def confirmar_remocao():
        cpf = entry_cpf.get()
        con = create_db_connection()
        if con is not None:
            cursor = con.cursor()
            try:
                cursor.execute("DELETE FROM medico WHERE id_funcionario IN (SELECT id_funcionario FROM funcionario WHERE cpf = %s)", (cpf,))
                cursor.execute("DELETE FROM enfermeiro WHERE id_funcionario IN (SELECT id_funcionario FROM funcionario WHERE cpf = %s)", (cpf,))
                cursor.execute("DELETE FROM funcionario WHERE cpf = %s", (cpf,))
                cursor.execute("DELETE FROM paciente WHERE cpf = %s", (cpf,))
                cursor.execute("DELETE FROM pessoa WHERE cpf = %s", (cpf,))

                con.commit()
                messagebox.showinfo("Sucesso", "Pessoa removida com sucesso!")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao remover pessoa: {err}")
                con.rollback()
            finally:
                cursor.close()
                con.close()
        remove_window.destroy()

    Button(remove_window, text="Remover", command=confirmar_remocao).pack()

def on_pessoa_select(event):
    widget = event.widget
    if not widget.curselection():  
        return
    index = int(widget.curselection()[0])
    nome_pessoa = widget.get(index).split(" - ")[0]  
    mostrar_detalhes_pessoa(nome_pessoa)

def mostrar_detalhes_pessoa(nome_pessoa):
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            cursor.execute("SELECT * FROM pessoa WHERE nome = %s", (nome_pessoa,))
            pessoa = cursor.fetchone()
            if pessoa:
                detalhes_window = Toplevel(root)
                detalhes_window.title(f"Detalhes de {nome_pessoa}")

                for col, val in zip(["CPF", "Nome", "Data Nascimento", "Telefone", "Endereço", "Bairro", "Estado"], pessoa):
                    Label(detalhes_window, text=f"{col}: {val}").pack()
        except mysql.connector.Error as err:
            print(f"Erro ao buscar dados: {err}")
        finally:
            cursor.close()
            con.close()

def filtrar_por_tipo():
    global filtro_var
    filtro_var = {"medico": tk.BooleanVar(), "enfermeiro": tk.BooleanVar(), "paciente": tk.BooleanVar()}

    filtro_window = Toplevel(root)
    filtro_window.title("Filtrar por")

    tk.Checkbutton(filtro_window, text="Médicos", variable=filtro_var["medico"]).pack()
    tk.Checkbutton(filtro_window, text="Enfermeiros", variable=filtro_var["enfermeiro"]).pack()
    tk.Checkbutton(filtro_window, text="Pacientes", variable=filtro_var["paciente"]).pack()

    Button(filtro_window, text="Aplicar Filtro", command=aplicar_filtro).pack()

def aplicar_filtro():
    tipos_selecionados = [tipo for tipo, var in filtro_var.items() if var.get()]
    filtrar(tipos_selecionados)



def filtrar(tipos):
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            lista_pessoas.delete(0, tk.END)  

            for tipo in tipos:
                count_query = ""
                if tipo == "paciente":
                    count_query = "SELECT COUNT(*) FROM paciente"
                    tipo_nome = "Paciente"
                elif tipo == "medico":
                    count_query = "SELECT COUNT(*) FROM medico"
                    tipo_nome = "Médico"
                elif tipo == "enfermeiro":
                    count_query = "SELECT COUNT(*) FROM enfermeiro"
                    tipo_nome = "Enfermeiro"

                if count_query:
                    cursor.execute(count_query)
                    count_result = cursor.fetchone()
                    lista_pessoas.insert(tk.END, f"{count_result[0]} pessoas cadastradas como {tipo_nome}")

                query = f"""
                    SELECT p.nome, 
                           CASE 
                             WHEN pa.cpf IS NOT NULL THEN 'Paciente'
                             WHEN m.id_funcionario IS NOT NULL THEN 'Médico'
                             WHEN e.id_funcionario IS NOT NULL THEN 'Enfermeiro'
                             ELSE 'Desconhecido'
                           END as tipo
                    FROM pessoa p
                    LEFT JOIN paciente pa ON p.cpf = pa.cpf
                    LEFT JOIN funcionario f ON p.cpf = f.cpf
                    LEFT JOIN medico m ON f.id_funcionario = m.id_funcionario
                    LEFT JOIN enfermeiro e ON f.id_funcionario = e.id_funcionario
                """
                cursor.execute(query)
                resultado = cursor.fetchall()
                for linha in resultado:
                    lista_pessoas.insert(tk.END, f"{linha[0]} - {linha[1]}")
                    
        except mysql.connector.Error as err:
            print(f"Erro ao buscar dados: {err}")
        finally:
            cursor.close()
            con.close()

criterio_pesquisa = "Nome"

def atualizar_criterio_pesquisa(novo_criterio):
    global criterio_pesquisa
    criterio_pesquisa = novo_criterio
    botao_pesquisa.config(text=novo_criterio)

def abrir_janela_pesquisa():
    janela_pesquisa = Toplevel(root)
    janela_pesquisa.title("Opções de Pesquisa")

    def atualizar_botao_pesquisa(texto):
        botao_pesquisa.config(text=texto)
        janela_pesquisa.destroy()

    Button(janela_pesquisa, text="Nome", command=lambda: atualizar_criterio_pesquisa("Nome")).pack(fill=tk.X)
    Button(janela_pesquisa, text="Ano de Nascimento", command=lambda: atualizar_criterio_pesquisa("Ano de Nascimento")).pack(fill=tk.X)
    Button(janela_pesquisa, text="Bairro", command=lambda: atualizar_criterio_pesquisa("Bairro")).pack(fill=tk.X)
    Button(janela_pesquisa, text="Cancelar", command=lambda: atualizar_criterio_pesquisa("Pesquisar por")).pack(fill=tk.X)

def enviar_acao():
    texto_pesquisa = campo_entrada.get()
    realizar_pesquisa(criterio_pesquisa, texto_pesquisa)

def realizar_pesquisa(criterio, texto):
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            query = ""
            if criterio == "Nome":
                coluna_pesquisa = "p.nome"
            elif criterio == "Ano de Nascimento":
                coluna_pesquisa = "YEAR(p.data_nascimento)"
            elif criterio == "Bairro":
                coluna_pesquisa = "p.bairro"
            else:
                coluna_pesquisa = "p.nome"

            query = f"""
                SELECT p.nome, 
                       CASE 
                         WHEN pa.cpf IS NOT NULL THEN 'Paciente'
                         WHEN m.id_funcionario IS NOT NULL THEN 'Médico'
                         WHEN e.id_funcionario IS NOT NULL THEN 'Enfermeiro'
                         ELSE 'Desconhecido'
                       END as tipo
                FROM pessoa p
                LEFT JOIN paciente pa ON p.cpf = pa.cpf
                LEFT JOIN funcionario f ON p.cpf = f.cpf
                LEFT JOIN medico m ON f.id_funcionario = m.id_funcionario
                LEFT JOIN enfermeiro e ON f.id_funcionario = e.id_funcionario
                WHERE {coluna_pesquisa} LIKE %s
            """

            cursor.execute(query, ('%' + texto + '%',) if criterio != "Ano de Nascimento" else (texto,))
            resultado = cursor.fetchall()
            lista_pessoas.delete(0, tk.END)
            if resultado:
                for linha in resultado:
                    lista_pessoas.insert(tk.END, f"{linha[0]} - {linha[1]}")
            else:
                lista_pessoas.insert(tk.END, "Nenhuma pessoa encontrada")
        except mysql.connector.Error as err:
            print(f"Erro ao buscar dados: {err}")
        finally:
            cursor.close()
            con.close()





root = tk.Tk()
root.title("Lista de Pessoas")
root.state('zoomed')

main_frame = Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

button_frame = Frame(main_frame)
button_frame.pack(side=tk.TOP, fill=tk.X)


botao_filtrar_por = Button(button_frame, text="Filtrar por", command=filtrar_por_tipo,bg="#DE6262", fg="white", highlightbackground="#DE6262", 
                           borderwidth=0, highlightthickness=0, padx=10, pady=5)
botao_filtrar_por.pack(side=tk.LEFT, padx=10)

botao_mostrar = Button(button_frame, text="Visualizar Pessoas", command=mostrar_pessoas,bg="#DE6262", fg="white", highlightbackground="#DE6262", 
                           borderwidth=0, highlightthickness=0, padx=10, pady=5)
botao_mostrar.pack(side=tk.LEFT, padx=10)

botao_adicionar = Button(button_frame, text="Adicionar Pessoa", command=adicionar_pessoa,bg="#DE6262", fg="white", highlightbackground="#DE6262", 
                           borderwidth=0, highlightthickness=0, padx=10, pady=5)
botao_adicionar.pack(side=tk.LEFT, padx=10)

botao_remover = Button(button_frame, text="Remover Pessoa", command=remover_pessoa,bg="#DE6262", fg="white", highlightbackground="#DE6262", 
                           borderwidth=0, highlightthickness=0, padx=10, pady=5)
botao_remover.pack(side=tk.LEFT, padx=10)

botao_pesquisa = Button(button_frame, text="Pesquisar por", command=abrir_janela_pesquisa, bg="#DE6262", fg="white", highlightbackground="#DE6262", 
                        borderwidth=0, highlightthickness=0, padx=10, pady=5)
botao_pesquisa.pack(side=tk.LEFT, padx=10)

campo_entrada = Entry(button_frame)
campo_entrada.pack(side=tk.LEFT, padx=10)

botao_enviar = Button(button_frame, text="Enviar", command=enviar_acao, bg="#DE6262", fg="white", highlightbackground="#DE6262", 
                      borderwidth=0, highlightthickness=0, padx=2, pady=2)
botao_enviar.pack(side=tk.LEFT, padx=10)


list_detail_frame = Frame(main_frame)
list_detail_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

lista_pessoas = Listbox(list_detail_frame, font=("Helvetica", 12),
                        highlightbackground='#DE6262', highlightcolor='#DE6262',
                        highlightthickness=2, bd=0, selectbackground='#DE6262')
lista_pessoas.bind('<<ListboxSelect>>', on_pessoa_select)
lista_pessoas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

detail_area = Frame(list_detail_frame)
detail_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

image_path = 'Alerta Saúde.png'  
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)
image_label = Label(main_frame, image=photo)
image_label.pack(side=tk.RIGHT, padx=10, pady=10)

root.mainloop()