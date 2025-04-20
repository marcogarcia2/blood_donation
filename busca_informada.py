import heapq
from math import radians, sin, cos, sqrt, atan2
import networkx as nx

def haversine(n1, n2, grafo):
    """Calcula a distância Haversine entre dois nós com coordenadas (x, y)."""
    R = 6371000  # Raio da Terra em metros
    lat1, lon1 = radians(grafo.nodes[n1]['y']), radians(grafo.nodes[n1]['x'])
    lat2, lon2 = radians(grafo.nodes[n2]['y']), radians(grafo.nodes[n2]['x'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def a_estrela(grafo, origem, destinos):
    """
    A* com heurística Haversine para múltiplos destinos.
    
    Retorna o caminho até o destino mais próximo.
    """
    destinos = set(destinos)
    fila = []
    heapq.heappush(fila, (0 + min(haversine(origem, d, grafo) for d in destinos), 0, origem, [origem]))

    custo_ate_agora = {origem: 0}

    while fila:
        f, g, atual, caminho = heapq.heappop(fila)

        if atual in destinos:
            return caminho

        for vizinho in grafo.neighbors(atual):
            # Calcular custo da aresta
            if grafo.is_multigraph():
                arestas = grafo[atual][vizinho]
                custo = min(attr.get('weight', 1) for attr in arestas.values())
            else:
                custo = grafo[atual][vizinho].get('weight', 1)

            novo_g = g + custo

            if vizinho not in custo_ate_agora or novo_g < custo_ate_agora[vizinho]:
                custo_ate_agora[vizinho] = novo_g
                h = min(haversine(vizinho, d, grafo) for d in destinos)
                f_novo = novo_g + h
                heapq.heappush(fila, (f_novo, novo_g, vizinho, caminho + [vizinho]))

    raise ValueError("Nenhum caminho encontrado para os destinos fornecidos.")