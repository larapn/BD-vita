import tkinter as tk
from tkinter import Toplevel, Listbox, Entry, Label, Button, messagebox
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
            cursor.execute("SELECT nome FROM pessoa")
            resultado = cursor.fetchall()
            lista_pessoas.delete(0, tk.END)
            for linha in resultado:
                lista_pessoas.insert(tk.END, linha[0])
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
                cursor.execute(query, (entry_cpf.get(), entry_nome.get(), entry_data_nascimento.get(), 
                                       entry_telefone.get(), entry_endereco.get(), entry_bairro.get(), 
                                       entry_estado.get()))
                con.commit()
                print("Pessoa adicionada com sucesso!")
            except mysql.connector.Error as err:
                print(f"Erro ao adicionar pessoa: {err}")
            finally:
                cursor.close()
                con.close()
        add_window.destroy()

    Button(add_window, text="Salvar", command=salvar_pessoa).pack()

def remover_pessoa():
    remove_window = Toplevel(root)
    remove_window.title("Remover Pessoa")

    Label(remove_window, text="CPF").pack()
    entry_cpf = Entry(remove_window)
    entry_cpf.pack()

    def confirmar_remocao():
        con = create_db_connection()
        if con is not None:
            cursor = con.cursor()
            try:
                query = "DELETE FROM pessoa WHERE cpf = %s"
                cursor.execute(query, (entry_cpf.get(),))
                con.commit()
                print("Pessoa removida com sucesso!")
            except mysql.connector.Error as err:
                print(f"Erro ao remover pessoa: {err}")
            finally:
                cursor.close()
                con.close()
        remove_window.destroy()

    Button(remove_window, text="Remover", command=confirmar_remocao).pack()

def pesquisar_por_idade():
    pesquisa_window = Toplevel(root)
    pesquisa_window.title("Pesquisar por Idade")

    Label(pesquisa_window, text="Idade").pack()
    entry_idade = Entry(pesquisa_window)
    entry_idade.pack()

    def pesquisar_por_idade():
        pesquisa_window = Toplevel(root)
        pesquisa_window.title("Pesquisar por Idade")

        Label(pesquisa_window, text="Idade").pack()
        entry_idade = Entry(pesquisa_window)
        entry_idade.pack()

    def buscar_por_idade():
        idade = entry_idade.get()
        try:
            idade = int(idade)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número válido para a idade.")
            return

        con = create_db_connection()
        if con is not None:
            cursor = con.cursor()
            try:
                # Calcula o ano de nascimento com base na idade inserida
                ano_nascimento = datetime.datetime.now().year - idade
                cursor.execute("SELECT nome FROM pessoa WHERE YEAR(data_nascimento) = %s", (ano_nascimento,))
                resultado = cursor.fetchall()
                lista_pessoas.delete(0, tk.END)
                for linha in resultado:
                    lista_pessoas.insert(tk.END, linha[0])
            except mysql.connector.Error as err:
                print(f"Erro ao buscar dados: {err}")
            finally:
                cursor.close()
                con.close()

    def ordenar_por_idade_crescente():
        con = create_db_connection()
        if con is not None:
            cursor = con.cursor()
            try:
                cursor.execute("SELECT nome FROM pessoa ORDER BY data_nascimento")
                resultado = cursor.fetchall()
                lista_pessoas.delete(0, tk.END)
                for linha in resultado:
                    lista_pessoas.insert(tk.END, linha[0])
            except mysql.connector.Error as err:
                print(f"Erro ao buscar dados: {err}")
            finally:
                cursor.close()
                con.close()

    def ordenar_por_idade_decrescente():
        con = create_db_connection()
        if con is not None:
            cursor = con.cursor()
            try:
                cursor.execute("SELECT nome FROM pessoa ORDER BY data_nascimento DESC")
                resultado = cursor.fetchall()
                lista_pessoas.delete(0, tk.END)
                for linha in resultado:
                    lista_pessoas.insert(tk.END, linha[0])
            except mysql.connector.Error as err:
                print(f"Erro ao buscar dados: {err}")
            finally:
                cursor.close()
                con.close()

    Button(pesquisa_window, text="Buscar por Idade", command=buscar_por_idade).pack()
    Button(pesquisa_window, text="Ordenar por Idade (Crescente)", command=ordenar_por_idade_crescente).pack()
    Button(pesquisa_window, text="Ordenar por Idade (Decrescente)", command=ordenar_por_idade_decrescente).pack()



root = tk.Tk()
root.title("Lista de Pessoas")

botao_pesquisar_idade = Button(root, text="Pesquisar por Idade", command=pesquisar_por_idade)
botao_pesquisar_idade.pack()

botao_mostrar = tk.Button(root, text="Visualizar Pessoas", command=mostrar_pessoas)
botao_mostrar.pack()

botao_adicionar = tk.Button(root, text="Adicionar Pessoa", command=adicionar_pessoa)
botao_adicionar.pack()

botao_remover = tk.Button(root, text="Remover Pessoa", command=remover_pessoa)
botao_remover.pack()

lista_pessoas = Listbox(root)
lista_pessoas.bind('<<ListboxSelect>>', on_pessoa_select)
lista_pessoas.pack()

root.mainloop()