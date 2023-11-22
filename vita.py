import tkinter as tk
from tkinter import Toplevel, Listbox, Entry, Label, Button, messagebox,ttk, Frame
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
            # Consulta para buscar nomes e tipos das pessoas
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
                pedir_tipo_pessoa(cpf)  # Chama a função para pedir o tipo da pessoa
            except mysql.connector.Error as err:
                print(f"Erro ao adicionar pessoa: {err}")
            finally:
                cursor.close()
                con.close()
            add_window.destroy()
        pedir_tipo_pessoa(entry_cpf.get())

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

        Label(funcionario_window, text="CRM:").pack()
        crm_entry = Entry(funcionario_window)
        crm_entry.pack()

        Label(funcionario_window, text="Especialidade:").pack()
        especialidade_entry = Entry(funcionario_window)
        especialidade_entry.pack()

        Label(funcionario_window, text="COREN:").pack()
        coren_entry = Entry(funcionario_window)
        coren_entry.pack()

        Label(funcionario_window, text="Setor:").pack()
        setor_entry = Entry(funcionario_window)
        setor_entry.pack()

        def salvar_funcionario():
            if cargo_var.get() == "Médico":
                crm = crm_entry.get()
                especialidade = especialidade_entry.get()
                # Salvar informações de médico no banco de dados
            elif cargo_var.get() == "Enfermeiro":
                coren = coren_entry.get()
                setor = setor_entry.get()
                # Salvar informações de enfermeiro no banco de dados
            mostrar_pessoas()
        funcionario_window.destroy()
        parent_window.destroy()


        Button(funcionario_window, text="Salvar Funcionário", command=salvar_funcionario).pack()

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
        # Salvar informações do paciente no banco de dados
        mostrar_pessoas()
        paciente_window.destroy()
        parent_window.destroy()

    Button(paciente_window, text="Salvar Paciente", command=salvar_paciente).pack()
    parent_window.destroy()

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
                # Primeiro, remova registros relacionados de tabelas que usam o id_funcionario
                cursor.execute("DELETE FROM medico WHERE id_funcionario IN (SELECT id_funcionario FROM funcionario WHERE cpf = %s)", (cpf,))
                cursor.execute("DELETE FROM enfermeiro WHERE id_funcionario IN (SELECT id_funcionario FROM funcionario WHERE cpf = %s)", (cpf,))
                # Agora remova registros da tabela funcionario e paciente
                cursor.execute("DELETE FROM funcionario WHERE cpf = %s", (cpf,))
                cursor.execute("DELETE FROM paciente WHERE cpf = %s", (cpf,))
                # Por fim, remova o registro na tabela pessoa
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
    if not widget.curselection():  # Verifica se há um item selecionado
        return
    index = int(widget.curselection()[0])
    nome_pessoa = widget.get(index).split(" - ")[0]  # Pega apenas o nome
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
    filtro_window = Toplevel(root)
    filtro_window.title("Filtrar por")

    Button(filtro_window, text="Pacientes", command=lambda: filtrar("paciente")).pack()
    Button(filtro_window, text="Médicos", command=lambda: filtrar("medico")).pack()
    Button(filtro_window, text="Enfermeiros", command=lambda: filtrar("enfermeiro")).pack()



def filtrar(tipo):
    con = create_db_connection()
    if con is not None:
        cursor = con.cursor()
        try:
            if tipo == "paciente":
                # Consulta para pacientes
                cursor.execute("SELECT pessoa.nome, paciente.tipo_sanguineo, paciente.orgao_transplante FROM pessoa INNER JOIN paciente ON pessoa.cpf = paciente.cpf")
            elif tipo == "medico":
                # Consulta para médicos
                cursor.execute("SELECT pessoa.nome, medico.crm, medico.especialidade FROM pessoa INNER JOIN funcionario ON pessoa.cpf = funcionario.cpf INNER JOIN medico ON funcionario.id_funcionario = medico.id_funcionario")
            elif tipo == "enfermeiro":
                # Consulta para enfermeiros
                cursor.execute("SELECT pessoa.nome, enfermeiro.coren FROM pessoa INNER JOIN funcionario ON pessoa.cpf = funcionario.cpf INNER JOIN enfermeiro ON funcionario.id_funcionario = enfermeiro.id_funcionario")

            resultado = cursor.fetchall()
            lista_pessoas.delete(0, tk.END)
            for linha in resultado:
                if tipo in ["medico", "paciente", "enfermeiro"]:
                    # Formatação de acordo com o tipo selecionado
                    info_adicional = ', '.join([f"{item}" for item in linha[1:]])
                    lista_pessoas.insert(tk.END, f"{linha[0]} - {info_adicional}")
                else:
                    lista_pessoas.insert(tk.END, linha[0])
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

# Adicionando botões ao frame dos botões
botao_filtrar_por = Button(button_frame, text="Filtrar por", command=filtrar_por_tipo)
botao_filtrar_por.pack(side=tk.LEFT, padx=10)

botao_mostrar = Button(button_frame, text="Visualizar Pessoas", command=mostrar_pessoas)
botao_mostrar.pack(side=tk.LEFT, padx=10)

botao_adicionar = Button(button_frame, text="Adicionar Pessoa", command=adicionar_pessoa)
botao_adicionar.pack(side=tk.LEFT, padx=10)

botao_remover = Button(button_frame, text="Remover Pessoa", command=remover_pessoa)
botao_remover.pack(side=tk.LEFT, padx=10)

# Frame para a Listbox e área de detalhes
list_detail_frame = Frame(main_frame)
list_detail_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Listbox no lado esquerdo
lista_pessoas = Listbox(list_detail_frame)
lista_pessoas.bind('<<ListboxSelect>>', on_pessoa_select)
lista_pessoas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Área de detalhes no lado direito (se necessário)
detail_area = Frame(list_detail_frame)
detail_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# ... [resto do seu código] ...

root.mainloop()