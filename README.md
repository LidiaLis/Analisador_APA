# Autora: Lídia Lisboa - 25/08/25

# Analisador Dinâmico de Código Python
Este projeto é uma aplicação desktop interativa desenvolvida com Tkinter para a máteira de APA, que permite ao usuário colar e analisar dinamicamente trechos de código Python. 
O objetivo principal é estimar a complexidade algorítmica de funções Python com base em medições empíricas de tempo de execução, 
oferecendo uma abordagem prática e visual para entender o desempenho de algoritmos.

# Funcionalidades
-Interface gráfica intuitiva para inserção e análise de código;
-Execução dinâmica de funções definidas pelo usuário;
-Geração automática de argumentos com base na assinatura da função;
-Medição de tempo de execução para diferentes tamanhos de entrada;
-Estimativa da complexidade algorítmica (ex: O(n), O(n log n), O(2ⁿ), etc.);
-Exibição dos resultados em uma tabela interativa;
-Detecção de técnicas utilizadas: recursão, iteração, programação dinâmica;
-Cálculo do erro percentual médio (MAPE) para ajuste de modelo.

# Estrutura do Projeto
bash
├── main.py               # Código principal com interface e lógica de análise
├── MODELS                # Dicionário com modelos de complexidade teórica
├── fit_complexity()      # Ajuste dos dados empíricos aos modelos teóricos
├── generate_args()       # Geração automática de argumentos para funções
├── App (classe Tk)       # Interface gráfica e controle de execução
└── README.md             # Documentação do projeto
# Como Funciona
O usuário insere um trecho de código Python no campo de texto.
O programa executa o código e identifica funções definidas, por meio majoritariamente do return.
Para cada função, ele gera entradas de teste com base na assinatura da função.
Se o código tiver uma recursão pesada, ele se restringe e realiza o teste com valores menores.
Mede o tempo de execução para diferentes valores de entrada, repetindo múltiplas vezes para reduzir ruído.
Ajusta os tempos observados aos modelos teóricos de complexidade usando regressão linear.
Exibe os resultados em uma tabela com tempo, tamanho, saída e complexidade estimada.
Detecta técnicas utilizadas no código (recursão, iteração, etc.) e exibe junto à complexidade.

# Modelos de Complexidade Considerados
-O(1);
-O(log n);
-O(n);
-O(n log n);
-O(n²);
-O(n³);
-O(2ⁿ)

A função fit_complexity() compara os tempos medidos com cada modelo e escolhe aquele com menor erro percentual médio (MAPE), exibindo também o coeficiente de ajuste a. 
O MAPE e a são os fatores mais importantes para a análise e redução do ruido, fazendo com que o código escolha entre os valores de testes, aqueles resultados que seriam 
o melhor caso para estas entradas de teste.

#  Interface Gráfica
A interface foi construída com Tkinter, utilizando:
-ScrolledText para entrada de código;
-Treeview para exibição dos resultados;
-Button para iniciar a análise;
-Label para mostrar a complexidade ajustada e técnica detectada;
-Cores suaves(Azul e Branca) e fontes modernas foram escolhidas para tornar a experiência agradável e acessível ao usuário.

# Requisitos
Python 3.7+;
Bibliotecas padrão de Python: tkinter, math, time, inspect, random, re, statistics.

# Como Executar
bash->
cd C:\Users\Lidia\Desktop\Apresentação-APA
python gui.py

# Melhorias Futuras
-Suporte a múltiplas funções simultaneamente;
-Exportação dos resultados em CSV ou PDF;
-Detecção automática de profundidade recursiva;
-Suporte a entrada personalizada para testes;
-Visualização gráfica dos tempos de execução;
-Análise de qualquer tipo de algoritmo.

(Atualmente se restringe um pouco, pois não apresenta o resultado sem return, mas por meio do MAPE já analisa vários tipos de codigos, com maior facilidae se tiver def e return)
