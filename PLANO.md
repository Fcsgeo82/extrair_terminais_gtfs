# PLANO: Extração de Terminais GTFS

Este projeto visa extrair os pontos iniciais (terminais) de cada linha de ônibus a partir de arquivos GTFS, garantindo dados limpos e sem duplicidades.

## 📋 Objetivos
Gerar um arquivo `terminais_linhas.csv` contendo as coordenadas e nomes dos terminais de IDA e VOLTA para cada linha.

## 🛠️ Arquitetura da Solução
Utilizaremos Python e Pandas para processar os arquivos core do GTFS (`routes.txt`, `trips.txt`, `stop_times.txt`, `stops.txt`).

## 🔄 Fluxo de Processamento

### 1. Ingestão de Dados
*   Leitura dos arquivos diretamente do ZIP do GTFS.
*   Seleção das colunas essenciais para otimizar o uso de memória.

### 2. Identificação de Origens
*   Em `stop_times.txt`, identificar o registro com a menor `stop_sequence` para cada `trip_id`.
*   Cruzar com `trips.txt` para associar cada origem a uma `route_id` e `direction_id`.

### 3. Tratamento de Duplicidades (CRÍTICO)
Para evitar múltiplas entradas para a mesma linha e sentido, aplicaremos a seguinte lógica:
*   **Agrupamento Geográfico**: Agrupar por `route_id`, `direction_id`, `stop_lat` e `stop_lon`.
*   **Filtro de Coordenadas**: Se houver múltiplos pontos com o mesmo XY para a mesma linha/sentido, eles serão consolidados em um único registro.
*   **Seleção de Itinerário Principal**: Caso uma linha apresente origens diferentes (ex: variantes da linha), selecionaremos a origem vinculada ao maior número de viagens (`trip_id`) ou ao itinerário com maior número de paradas.
*   **Unicidade**: O dataset final garantirá a relação **1 Linha : 1 Origem Ida : 1 Origem Volta**.

### 4. Associação e Pivotagem
*   Unir com `stops.txt` para obter o nome amigável do terminal.
*   Transformar o dataset de formato "longo" (uma linha por sentido) para formato "largo" (uma linha por `route_id` com colunas de Ida e Volta).

### 5. Saída
*   Exportação para `terminais_linhas.csv`.

---
**Agentes Responsáveis:** Developer & Architect (ECC)
**Data de Criação:** 2026-05-08
