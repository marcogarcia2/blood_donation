"""
Implementação do algoritmo BFS (Breadth-First Search) para busca não informada.

Este módulo contém a implementação do algoritmo de busca em largura (BFS)
para encontrar o caminho mais curto entre um nó de origem e um conjunto
de nós de destino em um grafo.
"""

# Vamos implementar uma Busca Em Largura:
# Ela irá receber:
# - o grafo
# - um nó de origem (usuário)
# - uma lista de nós de destino

# - Retornará o primeiro caminho mais curto (que será o mais curto tbm)

# busca_nao_informada.py
from collections import deque

# Deque é só uma fila dupla da biblioteca padrão de Python chamada collections, usada aqui, pois o BFS funciona a partir de uma estrutura baseada em FIFO (First In First Out).

def bfs(grafo, origem, destinos):
    """
    Implementação do algoritmo de busca em largura (BFS) para encontrar
    o caminho mais curto entre um nó de origem e um conjunto de destinos.
    
    O BFS explora todos os nós vizinhos do nó atual antes de avançar para
    os nós do próximo nível, garantindo que o primeiro caminho encontrado
    seja o mais curto em termos de número de arestas.
    
    Args:
        grafo: Grafo do NetworkX
        origem: ID do nó inicial (localização do usuário)
        destinos: Lista de IDs dos nós objetivos (hemocentros válidos)
        
    Returns:
        list: Caminho da origem até o destino mais próximo encontrado, ou
              None se não houver caminho
    """
    # Conjunto para armazenar nós já visitados, evitando ciclos
    visitado = set()
    
    # Fila FIFO (First In First Out) para gerenciar a ordem de exploração
    # Cada elemento da fila é uma tupla (nó_atual, caminho_até_nó)
    fila = deque([(origem, [origem])])

    while fila:
        # Remove o primeiro elemento da fila (FIFO)
        atual, caminho = fila.popleft()
        
        # Se o nó já foi visitado, pula para o próximo
        if atual in visitado:
            continue
            
        # Marca o nó atual como visitado
        visitado.add(atual)

        # Se encontramos um destino, retorna o caminho
        if atual in destinos:
            return caminho

        # Explora todos os vizinhos do nó atual
        for vizinho in grafo.neighbors(atual):
            if vizinho not in visitado:
                # Adiciona o vizinho na fila com o caminho atualizado
                fila.append((vizinho, caminho + [vizinho]))

    # Se a fila ficou vazia e não encontramos um destino
    return None
