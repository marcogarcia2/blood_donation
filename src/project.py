"""
Sistema de Doação de Sangue - Interface Gráfica

Este módulo implementa uma interface gráfica para um sistema de roteamento
entre doadores de sangue e hemocentros, utilizando algoritmos de busca informada
e não informada para encontrar o caminho mais eficiente.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.helper_functions import Graph, BancoDeHemocentros
from algorithms.busca_informada import a_estrela
from algorithms.busca_nao_informada import bfs

class BloodDonationApp:
    """
    Classe principal da aplicação que implementa a interface gráfica
    para o sistema de doação de sangue.
    """
    
    def __init__(self, root):
        """
        Inicializa a aplicação com a janela principal.
        
        Args:
            root: A janela principal do Tkinter
        """
        self.root = root
        self.root.title("Sistema de Doação de Sangue")
        self.root.geometry("800x600")
        
        # Variáveis de estado
        self.grafo = None
        self.banco_hemocentros = None
        self.origem = None
        self.tipo_sanguineo = tk.StringVar()
        self.algoritmo = tk.StringVar(value="A*")
        
        # Criar interface
        self.create_widgets()
        
    def create_widgets(self):
        """
        Cria e organiza todos os widgets da interface gráfica.
        """
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de controle
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="5")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Botão para carregar grafo
        ttk.Button(
            control_frame, 
            text="Carregar Grafo", 
            command=self.carregar_grafo
        ).grid(row=0, column=0, padx=5, pady=5)
        
        # Botão para selecionar origem aleatória
        ttk.Button(
            control_frame, 
            text="Origem Aleatória", 
            command=self.origem_aleatoria
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Combobox para tipo sanguíneo
        ttk.Label(control_frame, text="Tipo Sanguíneo:").grid(
            row=0, column=2, padx=5, pady=5
        )
        tipos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        ttk.Combobox(
            control_frame, 
            textvariable=self.tipo_sanguineo, 
            values=tipos, 
            state="readonly"
        ).grid(row=0, column=3, padx=5, pady=5)
        
        # Radio buttons para algoritmo
        ttk.Label(control_frame, text="Algoritmo:").grid(
            row=0, column=4, padx=5, pady=5
        )
        ttk.Radiobutton(
            control_frame, 
            text="A*", 
            variable=self.algoritmo, 
            value="A*"
        ).grid(row=0, column=5, padx=5, pady=5)
        ttk.Radiobutton(
            control_frame, 
            text="BFS", 
            variable=self.algoritmo, 
            value="BFS"
        ).grid(row=0, column=6, padx=5, pady=5)
        
        # Botão para executar busca
        ttk.Button(
            control_frame, 
            text="Encontrar Rota", 
            command=self.encontrar_rota
        ).grid(row=0, column=7, padx=5, pady=5)
        
        # Frame para informações
        self.info_frame = ttk.LabelFrame(main_frame, text="Informações", padding="5")
        self.info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Labels para informações
        self.origem_label = ttk.Label(self.info_frame, text="Origem: Não definida")
        self.origem_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.destino_label = ttk.Label(self.info_frame, text="Destino: Não definido")
        self.destino_label.grid(row=0, column=1, padx=5, pady=5)
        
        self.distancia_label = ttk.Label(self.info_frame, text="Distância: Não calculada")
        self.distancia_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.nos_label = ttk.Label(self.info_frame, text="Nós percorridos: Não calculado")
        self.nos_label.grid(row=0, column=3, padx=5, pady=5)
        
    def carregar_grafo(self):
        """
        Carrega o grafo a partir do arquivo e inicializa o banco de hemocentros.
        """
        try:
            self.grafo = Graph("../data/sao_carlos.graphml")
            # Criar banco de hemocentros com 5 hemocentros aleatórios
            hemocentros = self.grafo.get_random_nodes(5)
            self.banco_hemocentros = BancoDeHemocentros(hemocentros, self.grafo.graph)
            messagebox.showinfo("Sucesso", "Grafo carregado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar grafo: {str(e)}")
    
    def origem_aleatoria(self):
        """
        Seleciona um nó aleatório do grafo como origem.
        """
        if self.grafo is None:
            messagebox.showerror("Erro", "Carregue o grafo primeiro!")
            return
        
        self.origem = self.grafo.get_random_nodes(1)[0]
        self.origem_label.config(text=f"Origem: Nó {self.origem}")
    
    def calcular_distancia_rota(self, rota):
        """
        Calcula a distância total de uma rota no grafo.
        
        Args:
            rota: Lista de nós que formam a rota
            
        Returns:
            float: Distância total da rota em metros
        """
        distancia = 0
        for i in range(len(rota) - 1):
            u, v = rota[i], rota[i + 1]
            
            # Verifica se a aresta existe no grafo
            if self.grafo.graph.has_edge(u, v):
                edge_data = self.grafo.graph[u][v]  # Pega os dados da aresta
                # Acessa o comprimento da aresta
                length = edge_data[0].get('length', 0)  # Caso não tenha 'length', assume 0
                distancia += length
            else:
                print(f"Aresta entre {u} e {v} não encontrada no grafo.")
        return distancia
    
    def encontrar_rota(self):
        """
        Encontra a rota mais eficiente entre a origem e o hemocentro mais próximo
        que possui o tipo sanguíneo desejado.
        """
        if self.grafo is None:
            messagebox.showerror("Erro", "Carregue o grafo primeiro!")
            return
        
        if self.origem is None:
            messagebox.showerror("Erro", "Selecione uma origem primeiro!")
            return
        
        tipo = self.tipo_sanguineo.get()
        if not tipo:
            messagebox.showerror("Erro", "Selecione um tipo sanguíneo!")
            return
        
        # Obter hemocentros válidos
        hemocentros_validos = self.banco_hemocentros.hemocentros_validos(tipo)
        if not hemocentros_validos:
            messagebox.showerror("Erro", "Não há hemocentros com estoque disponível para este tipo sanguíneo!")
            return
        
        # Executar algoritmo selecionado
        if self.algoritmo.get() == "A*":
            rota = a_estrela(self.grafo.graph, self.origem, hemocentros_validos)
        else:
            rota = bfs(self.grafo.graph, self.origem, hemocentros_validos)
        
        if rota is None:
            messagebox.showerror("Erro", "Não foi possível encontrar uma rota!")
            return
        
        # Atualizar informações
        self.destino_label.config(text=f"Destino: Nó {rota[-1]}")
        distancia = self.calcular_distancia_rota(rota)
        self.distancia_label.config(text=f"Distância: {distancia:.2f} metros")
        self.nos_label.config(text=f"Nós percorridos: {len(rota)}")
        
        # Plotar rota
        self.grafo.plotar_rota_com_zoom(rota)

if __name__ == "__main__":
    root = tk.Tk()
    app = BloodDonationApp(root)
    root.mainloop()
