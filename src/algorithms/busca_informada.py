"""
Implementação do algoritmo A* para busca informada.

Este módulo contém a implementação do algoritmo A* com heurística Haversine
para encontrar o caminho mais eficiente entre um nó de origem e um conjunto
de nós de destino em um grafo.
"""

import heapq
from math import radians, sin, cos, sqrt, atan2

def haversine(n1, n2, grafo):
    """
    Calcula a distância Haversine entre dois nós com coordenadas geográficas.
    
    A distância Haversine é uma fórmula que calcula a distância entre dois pontos
    na superfície de uma esfera (Terra) dadas suas coordenadas de latitude e longitude.
    
    Args:
        n1: ID do primeiro nó
        n2: ID do segundo nó
        grafo: Grafo contendo as coordenadas dos nós
        
    Returns:
        float: Distância em metros entre os nós
    """
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
    Implementação do algoritmo A* com heurística Haversine para múltiplos destinos.
    
    O algoritmo A* é uma busca informada que utiliza uma função heurística
    para estimar o custo do caminho mais curto entre o nó atual e o destino.
    Neste caso, a heurística é a distância Haversine.
    
    Args:
        grafo: Grafo do NetworkX
        origem: ID do nó inicial
        destinos: Conjunto de IDs dos nós objetivos
        
    Returns:
        list: Caminho da origem até o destino mais próximo encontrado
        
    Raises:
        ValueError: Se nenhum caminho for encontrado para os destinos fornecidos
    """
    destinos = set(destinos)
    fila = []
    heapq.heappush(
        fila, 
        (0 + min(haversine(origem, d, grafo) for d in destinos), 0, origem, [origem])
    )

    custo_ate_agora = {origem: 0}

    while fila:
        f, g, atual, caminho = heapq.heappop(fila)

        if atual in destinos:
            return caminho

        for vizinho in grafo.neighbors(atual):
            # Calcular custo da aresta
            if grafo.is_multigraph():
                arestas = grafo[atual][vizinho]  # Pega as múltiplas arestas entre os nós
                custo = min(attr.get('length', 0) for attr in arestas.values())
            else:
                custo = grafo[atual][vizinho].get('length', 0)

            novo_g = g + custo

            if vizinho not in custo_ate_agora or novo_g < custo_ate_agora[vizinho]:
                custo_ate_agora[vizinho] = novo_g
                h = min(haversine(vizinho, d, grafo) for d in destinos)
                f_novo = novo_g + h
                heapq.heappush(fila, (f_novo, novo_g, vizinho, caminho + [vizinho]))

    raise ValueError("Nenhum caminho encontrado para os destinos fornecidos.")