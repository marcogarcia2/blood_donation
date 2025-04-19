import osmnx as ox
import networkx as nx
import random

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
        rota = nx.shortest_path(self.grafo, origem, destino, weight=weight)
        return rota

    # Plota a rota encontrada com o networkx
    def plotar_rota(self, rota):
        ox.plot_graph_route(self.grafo, rota, route_linewidth=4, node_size=0, bgcolor="white")



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
            tipo: random.choices([0, random.randint(1, 50)], weights=[0.5, 0.5])[0]
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