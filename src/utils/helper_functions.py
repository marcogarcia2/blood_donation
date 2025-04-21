import osmnx as ox
import networkx as nx
import random
import pandas as pd
import matplotlib.pyplot as plt

# Classe que representa o grafo da cidade escolhida
class Graph:

    # Inicia e mantém na memória o grafo em OSMNX e GDF
    def __init__(self, graphml_file):

        # Esse formato usamos para cálculos
        self.graph = ox.load_graphml(graphml_file)

        # Esse formato usamos para plotar no mapa
        self.nodes_gdf, self.edges_gdf = ox.graph_to_gdfs(self.graph)
    

    # Retorna n nós aleatórios do grafo em uma lista
    def get_random_nodes(self, n=1):
        return random.sample(list(self.graph.nodes), n)


    # Retorna os IDs dos nós em formato GDF
    def get_gdf_nodes(self, ids):
        return self.nodes_gdf.loc[ids]


    # Calcula rota com método padrão da biblioteca networkx
    def calcular_rota(self, origem, destino, weight="length"):
        return nx.shortest_path(self.graph, origem, destino, weight=weight)
        
    
    # Calcula a distância da rota com método padrão da biblioteca networkx
    def calcular_distancia(self, origem, destino, weight="length"):
        return nx.shortest_path_length(self.graph, origem, destino, weight=weight)

    # Função customizada: Plotar a rota com cores chamativas
    def plotar_rota(self, rota, name=None, app=False):
        '''
        Plota uma rota qualquer em azul, com o nó de origem em verde e o nó de destino em vermelho,
        sobre o grafo todo em cinza. 

        Args:
            rota: lista de nós que compõe a rota
            name: nome do arquivo caso queria salvar a imagem (opcional)
            app: indica se foi chamada pelo aplicativo ou não (opcional)
        '''

        # Definindo o primeiro e o último nó
        origem = rota[0]
        destino = rota[-1]

        fig, ax = ox.plot_graph(
            self.graph,
            show=False,
            close=False,
            bgcolor='white',
            node_size=0,
            edge_color='gray',
            edge_linewidth=0.5
        )

        # Coordenadas da rota
        x = [self.graph.nodes[n]['x'] for n in rota]
        y = [self.graph.nodes[n]['y'] for n in rota]

        # Desenha a rota real respeitando a geometria das arestas
        for u, v in zip(rota[:-1], rota[1:]):
            edge_data = self.graph.get_edge_data(u, v)
            if self.graph.is_multigraph():
                edge_data = edge_data[0]  # pega a primeira aresta se for multigraph

            if 'geometry' in edge_data:
                xs, ys = edge_data['geometry'].xy
            else:
                xs = [self.graph.nodes[u]['x'], self.graph.nodes[v]['x']]
                ys = [self.graph.nodes[u]['y'], self.graph.nodes[v]['y']]

            if u == rota[0]: ax.plot(xs, ys, color='blue', linewidth=3, alpha=0.7, label='Rota') # Label somente uma vez
            else: ax.plot(xs, ys, color='blue', linewidth=3, alpha=0.7)

        # Destacar origem
        ax.scatter(self.graph.nodes[origem]['x'], self.graph.nodes[origem]['y'], c='#00AA00', s=150, label='Origem', zorder=5)

        # Destacar destino
        ax.scatter(self.graph.nodes[destino]['x'], self.graph.nodes[destino]['y'], c='red', s=60, label='Destino', zorder=5)

        # Zoom: calcular limites com margem
        margin = 0.005

        x_min, x_max = min(x), max(x)
        y_min, y_max = min(y), max(y)

        width = x_max - x_min
        height = y_max - y_min

        # Força proporção quadrada com base na maior dimensão
        lado = max(width, height)

        # Centro da rota
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2

        # Aplica limites com proporção quadrada e margem extra
        ax.set_xlim(x_center - lado / 2 - margin, x_center + lado / 2 + margin)
        ax.set_ylim(y_center - lado / 2 - margin, y_center + lado / 2 + margin)

        plt.legend()
        plt.tight_layout()
        
        # Caso tenha nome, significa que quer salvar a imagem
        if name is not None: 
            if app: 
                plt.savefig("../images/app_images/" + name, dpi=300)
            else:
                plt.savefig("../images/" + name, dpi=300)

        # Se for exibido pelo aplicativo, não abra uma janela
        if app:
            plt.close(fig) 
        else:
            plt.show()   



# Classe que representa todos os hemocentros da cidade escolhida
class BancoDeHemocentros:

    def __init__(self, h_list, grafo):

        self.TIPOS_SANGUINEOS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

        # Atributo principal, vai guardar todo o estoque dos hemocentros
        self.hemocentros = {}
        
        # Para cada hemocentro:
        for node_id in h_list:
            self.hemocentros[node_id] = {
                
                # Salvando suas coordenadas
                'coords': (grafo.nodes[node_id]['x'], grafo.nodes[node_id]['y']),
                
                # Gerando um número aleatório de bolsas de sangue de cada tipo
                'estoque': self.__generate_random_stock()
            }

    
    # Gerando um número aleatório de bolsas de sangue de cada tipo
    def __generate_random_stock(self):
        return {
            tipo: random.choices([0, random.randint(1, 50)], weights=[0.6, 0.4])[0]
            for tipo in self.TIPOS_SANGUINEOS
        }


    # Retorna o estoque de bolsas de sangue de um determinado hemocentro
    def consultar_estoque(self, h_id):
        return self.hemocentros.get(h_id, {}).get('estoque', None)


    # Função que retorna os tipos doadores para um determinado tipo
    def __doadores(self, tipo: str) -> list:
        compatibilidade = {
            'O-': ['O-'],
            'O+': ['O-', 'O+'],
            'A-': ['O-', 'A-'],
            'A+': ['O-', 'O+', 'A-', 'A+'],
            'B-': ['O-', 'B-'],
            'B+': ['O-', 'O+', 'B-', 'B+'],
            'AB-': ['O-', 'A-', 'B-', 'AB-'],
            'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
        }
        return compatibilidade.get(tipo.upper(), [])
        
    
    # Função que retorna os hemocentros que possuem sangue disponível para ser doado, dado o tipo sanguíneo do usuário
    def hemocentros_validos(self, tipo: str) -> list:
        
        hcs_validos = []
        doadores = self.__doadores(tipo)

        for hc in self.hemocentros:
            blood_stock = self.consultar_estoque(hc)            
            for doador in doadores:
                if blood_stock[doador] > 0:
                    hcs_validos.append(hc)
                    break
        
        return hcs_validos
    

# Função que plota os hemocentros, o usuário e as ruas com zoom
def plotar_com_zoom(gdf_user, gdf_hcs, gdf_edges, valid=False, map=True, name=None, app=False):
    '''
    Essa função plota a posição do usuário e as posições dos hemocentros em relação ao grafo todo.
    O Plot é realizado com zoom, ignorando partes não importantes do grafo (pois este geralmente é muito grande.)

    Args: 
        gdf_user: posição do usuário em GDF (verde)
        gdf_hcs: posição dos hemocentros em GDF (vermelho)
        gdf_edges: todo o grafo em GDF (azul, representa as ruas)
        valid: booleano que indica se os hemocentros em questão são os válidos ou gerais (opcional)
        map: booleano responsável por colocar o mapa por debaixo do plot (opcional)
        name: nome do arquivo caso queira salvar a imagem (opcional)
        app: indica se foi chamada pelo aplicativo (opcional)
    '''

    # Juntando os pontos que queremos enquadrar
    gdfs = [gdf for gdf in [gdf_user, gdf_hcs] if gdf is not None]
    if gdfs:
        gdf_zoom = pd.concat(gdfs)

        # Parâmetros de margem e tamanho mínimo
        margin = 0.1

        # Calculando limites brutos
        x_min, x_max = gdf_zoom.geometry.x.min(), gdf_zoom.geometry.x.max()
        y_min, y_max = gdf_zoom.geometry.y.min(), gdf_zoom.geometry.y.max()

        # Dimensões reais
        real_width = x_max - x_min
        real_height = y_max - y_min

        # Margem absoluta
        x_margin = real_width * margin
        y_margin = real_height * margin

        # Tamanhos finais respeitando proporção quadrada
        lado = max(real_width, real_height)

        # Centro da área
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2

        # Limites ajustados com margem e proporção quadrada
        x_min_plot = x_center - lado / 2 - x_margin
        x_max_plot = x_center + lado / 2 + x_margin
        y_min_plot = y_center - lado / 2 - y_margin
        y_max_plot = y_center + lado / 2 + y_margin

    ## Daqui pra cima, a única coisa que foi feita foi o cálculo para dar zoom. 
    ## Não se preocupe tanto com o código acima.

    # Verificando se os hemocentros são validos ou não, isso mudará o título e a legenda
    title, hc_label = "", ""
    if valid:
        hc_label = "Hemocentro Válido"
        title = "Usuário e Hemocentros Válidos (com Zoom)"
    else:
        hc_label = "Hemocentro"
        title = "Usuário e Hemocentros (com Zoom)"


    green = 'chartreuse' if map else '#00AA00'
    
    # Plotando os dados de fato no mapa, caso tenham sido passados por argumento
    fig, ax = plt.subplots(figsize=(10, 10))
    if gdf_edges is not None: gdf_edges.plot(ax=ax, linewidth=0.2, edgecolor="blue", label='Ruas')
    if gdf_hcs is not None: gdf_hcs.plot(ax=ax, color="red", markersize=50, zorder=3, label=hc_label)
    if gdf_user is not None: gdf_user.plot(ax=ax, color=green, markersize=150, zorder=3, label='Localização do Usuário')
    
    if gdfs:
        # Aplicando limites
        ax.set_xlim(x_min_plot, x_max_plot)
        ax.set_ylim(y_min_plot, y_max_plot)

    if map:
        import contextily as ctx
        ctx.add_basemap(ax, crs=gdf_edges.crs, source=ctx.providers.OpenStreetMap.Mapnik)

    # Estética final
    ax.set_axis_off()
    plt.legend()
    if not app: plt.title(title)
    plt.tight_layout()

    # Caso tenha nome, significa que quer salvar a imagem
    if name is not None: 
        if app: 
            plt.savefig("../images/app_images/" + name, dpi=300)
        else:
            plt.savefig("../images/" + name, dpi=300)

    # Se for exibido pelo aplicativo, não abra uma janela
    if app:
        plt.close(fig) 
    else:
        plt.show()  

