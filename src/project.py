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
from utils.helper_functions import plotar_com_zoom
from PIL import Image, ImageTk

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
        self.root.geometry("1100x1000")
        
        # Variáveis de estado
        self.grafo = None
        self.banco_hemocentros = None
        self.origem = None
        self.tipo_sanguineo = tk.StringVar()
        self.tipo_sanguineo.trace_add("write", self.filtrar_hemocentros)
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
            text="Compartilhar Localização", 
            command=self.origem_usuario
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
        ttk.Radiobutton(
            control_frame, 
            text="Ideal", 
            variable=self.algoritmo, 
            value="Ideal"
        ).grid(row=0, column=7, padx=5, pady=5)
        
        # Botão para executar busca
        ttk.Button(
            control_frame, 
            text="Encontrar Rota", 
            command=self.encontrar_rota
        ).grid(row=0, column=8, padx=5, pady=5)
        
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
    

    def mostrar_imagem(self, pathname: str):
        try:
            # Remove imagem/canvas anterior, se existir
            if hasattr(self, 'frame_imagem') and self.frame_imagem.winfo_exists():
                self.frame_imagem.destroy()
            if hasattr(self, 'canvas_imagem') and self.canvas_imagem.winfo_exists():
                self.canvas_imagem.destroy()
            if hasattr(self, 'scrollbar_y') and self.scrollbar_y.winfo_exists():
                self.scrollbar_y.destroy()
            if hasattr(self, 'scrollbar_x') and self.scrollbar_x.winfo_exists():
                self.scrollbar_x.destroy()

            # Carrega a imagem
            imagem = Image.open("../images/app_images/" + pathname)
            max_size = (1100, 1100)
            imagem.thumbnail(max_size)  # Redimensiona mantendo proporção
            self.tk_image = ImageTk.PhotoImage(imagem)

            # Canvas com scroll
            self.canvas_imagem = tk.Canvas(self.root, width=1000, height=700)
            self.scrollbar_y = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas_imagem.yview)
            self.scrollbar_x = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas_imagem.xview)
            self.canvas_imagem.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

            # Posicionamento
            self.canvas_imagem.grid(row=2, column=0, sticky="nsew", columnspan=2)
            self.scrollbar_y.grid(row=2, column=2, sticky="ns")
            self.scrollbar_x.grid(row=3, column=0, sticky="ew", columnspan=2)

            # Frame onde a imagem será colocada
            self.frame_imagem = tk.Frame(self.canvas_imagem)
            self.label_imagem = tk.Label(self.frame_imagem, image=self.tk_image)
            self.label_imagem.pack()

            # Adiciona o frame ao canvas
            self.canvas_imagem.create_window((0, 0), window=self.frame_imagem, anchor="nw")

            # Atualiza limites de scroll
            self.frame_imagem.update_idletasks()
            self.canvas_imagem.config(scrollregion=self.canvas_imagem.bbox("all"))

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar grafo: {str(e)}")


    def carregar_grafo(self):
        """
        Carrega o grafo a partir do arquivo e inicializa o banco de hemocentros.
        """
        try:
            self.grafo = Graph("../data/sao_carlos.graphml")
            # Criar banco de hemocentros com 5 hemocentros aleatórios
            hemocentros = self.grafo.get_random_nodes(5)
            self.banco_hemocentros = BancoDeHemocentros(hemocentros, self.grafo.graph)
            self.gdf_hcs = self.grafo.get_gdf_nodes(hemocentros)
            plotar_com_zoom(gdf_user=None, gdf_hcs=self.gdf_hcs, gdf_edges=self.grafo.edges_gdf, name="mapa_com_hemocentros.png", app=True)

            # Mostrando o grafo
            self.mostrar_imagem("mapa_com_hemocentros.png")
            messagebox.showinfo("Sucesso", "Grafo carregado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar grafo: {str(e)}")
    
    def origem_usuario(self):
        """
        Seleciona um nó aleatório do grafo como origem.
        """
        if self.grafo is None:
            messagebox.showerror("Erro", "Carregue o grafo primeiro!")
            return
        
        # self.origem = self.grafo.get_random_nodes(1)[0]
        self.origem = 5156294301
        self.origem_label.config(text=f"Origem: Nó {self.origem}")

        try:
            self.gdf_user = self.grafo.get_gdf_nodes([self.origem])
            plotar_com_zoom(gdf_user=self.gdf_user, gdf_hcs=self.gdf_hcs, gdf_edges=self.grafo.edges_gdf, map=False, name="mapa_hcs_usuario.png", app=True)

            self.mostrar_imagem("mapa_hcs_usuario.png")
            messagebox.showinfo("Sucesso", "Localização do usuário adquirida!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao localizar o usuário: {str(e)}")


    # Escolhido o tipo sanguíneo, mostra somente os hemocentros válidos
    def filtrar_hemocentros(self, *args):
        """
        """
        if self.grafo is None:
            messagebox.showerror("Erro", "Carregue o grafo primeiro!")
            return
    
        if self.origem is None:
            messagebox.showerror("Erro", "Compartilhe sua localização primeiro!")
            return
        
        hcs_validos = self.banco_hemocentros.hemocentros_validos(self.tipo_sanguineo.get())
        self.gdf_hcs_validos = self.grafo.get_gdf_nodes(hcs_validos)

        try:
            plotar_com_zoom(gdf_user=self.gdf_user, gdf_hcs=self.gdf_hcs_validos, gdf_edges=self.grafo.edges_gdf, map=False, valid=True, name="hemocentros_validos.png", app=True)
            self.mostrar_imagem("hemocentros_validos.png")

            if len(hcs_validos) < 5 and len(hcs_validos) > 1:
                messagebox.showinfo("Sucesso", f"De 5 hemocentros, apenas {len(hcs_validos)} possuem doadores compatíveis.")
            elif len(hcs_validos) == 1:
                messagebox.showinfo("Sucesso", f"De 5 hemocentros, apenas {len(hcs_validos)} possui doadores compatíveis.")
            elif len(hcs_validos) == 0:
                messagebox.showinfo("Sucesso", f"Nenhum dos hemocentros possui doadores compatíveis.")
            else:
                messagebox.showinfo("Sucesso", f"Todos os hemocentros possuem doadores compatíveis.")
    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar hemocentros: {str(e)}")

    def somar_distancia_rota(self, rota):
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
            messagebox.showerror("Erro", "Compartilhe sua origem primeiro!")
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
        algoritmo = self.algoritmo.get()
        if algoritmo == "A*":
            rota = a_estrela(self.grafo.graph, self.origem, hemocentros_validos)
        elif algoritmo == "BFS":
            rota = bfs(self.grafo.graph, self.origem, hemocentros_validos)
        elif algoritmo == "Ideal":
            distancias = {
                destino: self.grafo.calcular_distancia(self.origem, destino)
                for destino in hemocentros_validos
            }
            destino_mais_proximo = min(distancias.items(), key=lambda x: x[1])[0]
            rota = self.grafo.calcular_rota(self.origem, destino_mais_proximo)
        else:
            messagebox.showerror("Erro", "Algoritmo inválido!")
            return
        
        if rota is None:
            messagebox.showerror("Erro", "Não foi possível encontrar uma rota!")
            return
        
        # Atualizar informações
        self.destino_label.config(text=f"Destino: Nó {rota[-1]}")
        distancia = self.somar_distancia_rota(rota)
        self.distancia_label.config(text=f"Distância: {distancia:.2f} metros")
        self.nos_label.config(text=f"Nós percorridos: {len(rota)}")
        
        # Plotar rota
        self.grafo.plotar_rota(rota, name="rota_app.png", app=True)
        self.mostrar_imagem("rota_app.png")

if __name__ == "__main__":
    root = tk.Tk()
    app = BloodDonationApp(root)
    root.mainloop()
