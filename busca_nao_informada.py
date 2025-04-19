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
    Realiza busca em largura (BFS) a partir de um nó origem até o primeiro destino encontrado.
    
    Parâmetros:
    - grafo: grafo do NetworkX
    - origem: ID do nó inicial (localização do usuário)
    - destinos: lista de IDs dos nós objetivos (hemocentros válidos já filtrados)

    Retorno:
    - lista com o caminho da origem até o destino mais próximo encontrado, ou None se não houver caminho
    """

    visitado = set() # É um conjunto que guarda nós explorados, pra evitar caminhos repetidos ou loops infinitos inócuos
    fila = deque([(origem, [origem])]) # A nossa fila é inicializada com o nó de origem e o caminho até agora, que é basicamente só onde estamos mesmo

    while fila: # Quando a fila estiver vazia, não há mais nós a visitar

        # Veja que faz sentido a linha a seguir, pois cada elemetno da lista é uma tupla, portando um popleft cospe os 2 elementos da fila, que são um nó e uma listinha de nós (que é o caminho)
        atual, caminho = fila.popleft() # Retira o nó da cabeça da fila, mantendo o FIFO
        
        # Esse nó da cabeça é o que será explorado neste passo, enquanto o caminho é exatamente
        if atual in visitado: # Se o nó já foi visitado, não faz sentido explorá-lo novamente, então pulamos ele
            continue # Volta pro início do loop, sem fazer nada abaixo dessa linha

        visitado.add(atual) # Adicionamos o nó atual à lista de visitados, pois ele foi explorado

        if atual in destinos: # Se o nó atual é um dos nossos objetivos, retornamos o caminho que trouxe até ele!
            return caminho

        # O método neighbors() retorna todos os nós adjacentes ao nó atual

        # Usamos isso para adicionar esses vizinhos na nossa listona de exploração, verificando se eles já não foram adicionados, com o 'not in'
        for vizinho in grafo.neighbors(atual):
            if vizinho not in visitado:
                fila.append((vizinho, caminho + [vizinho]))
                # Adicionamos o vizinho na cauda da fila, juntamente com o caminho até ele, que é o caminho atual + o vizinho

    return None
