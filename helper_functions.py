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
        rota = nx.shortest_path(self.graph, origem, destino, weight=weight)
        return rota
    
    # Calcula a distância da rota com método padrão da biblioteca networkx
    def calcular_distancia(self, origem, destino, weight="length"):
        distancia = nx.shortest_path_length(self.graph, origem, destino, weight=weight)
        return distancia

    # Plota a rota encontrada com o networkx
    def plotar_rota(self, rota):
        ox.plot_graph_route(self.graph, rota, route_linewidth=4, node_size=0, bgcolor="white")


    def plotar_rota_com_zoom(self, rota, margem=0.005):
        """
        Plota a rota com zoom automático baseado nos nós da rota.
        margem: margem geográfica (em graus) ao redor da rota
        """
        import matplotlib.pyplot as plt

        # Pega os pontos da rota como GeoDataFrame
        rota_coords = [(self.graph.nodes[n]['x'], self.graph.nodes[n]['y']) for n in rota]
        xs, ys = zip(*rota_coords)

        # Calcula limites com margem
        xlim = (min(xs) - margem, max(xs) + margem)
        ylim = (min(ys) - margem, max(ys) + margem)

        # Plota usando o osmnx com limites ajustados
        fig, ax = ox.plot_graph_route(
            self.graph, rota,
            route_linewidth=4, node_size=0, bgcolor="white", ax=None,
            show=False, close=False
        )
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        plt.tight_layout()
        plt.title("Rota com Zoom Automático")
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
    

# Função que plota os hemocentros, o usuário e as ruas com zoom (sem o mapa por trás)
def plotar_com_zoom(gdf_user, gdf_hcs, gdf_edges, valid=False, map=True):
    
    # Juntando os pontos que queremos enquadrar
    gdf_zoom = pd.concat([gdf_user, gdf_hcs])

    # Parâmetros de margem e tamanho mínimo
    margin_percent = 0.1
    min_width = 0.1
    min_height = 0.1

    # Calculando limites brutos
    x_min, x_max = gdf_zoom.geometry.x.min(), gdf_zoom.geometry.x.max()
    y_min, y_max = gdf_zoom.geometry.y.min(), gdf_zoom.geometry.y.max()

    # Dimensões reais
    real_width = x_max - x_min
    real_height = y_max - y_min

    # Margem absoluta
    x_margin = real_width * margin_percent
    y_margin = real_height * margin_percent

    # Tamanhos finais respeitando mínimo
    final_width = max(real_width, min_width)
    final_height = max(real_height, min_height)

    # Centro da área
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2

    # Limites ajustados com margem
    x_min_plot = x_center - final_width / 2 - x_margin
    x_max_plot = x_center + final_width / 2 + x_margin
    y_min_plot = y_center - final_height / 2 - y_margin
    y_max_plot = y_center + final_height / 2 + y_margin

    # Verificando se os hemocentros são validos
    title, hc_label = "", ""
    if (valid):
        hc_label = "Hemocentro Válido"
        title = "Usuário e Hemocentros Válidos (com Zoom)"
    else:
        hc_label = "Hemocentro"
        title = "Usuário e Hemocentros (com Zoom)"

    # Plotando o mapa
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_edges.plot(ax=ax, linewidth=0.2, edgecolor="blue", label='Ruas')
    gdf_hcs.plot(ax=ax, color="red", markersize=50, zorder=3, label=hc_label)
    gdf_user.plot(ax=ax, color="#00AA00", markersize=50, zorder=3, label='Localização do Usuário')
    

    # Aplicando limites
    ax.set_xlim(x_min_plot, x_max_plot)
    ax.set_ylim(y_min_plot, y_max_plot)

    if (map):
        import contextily as ctx
        ctx.add_basemap(ax, crs=gdf_edges.crs, source=ctx.providers.OpenStreetMap.Mapnik)

    # Estética final
    ax.set_axis_off()
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    plt.savefig("images/hcs_validos_zoom.png", dpi=300)
    plt.show()
