# Extração de Terminais GTFS

Este projeto automatiza a extração e consolidação dos terminais de origem (ida e volta) das linhas de ônibus (SPPO e BRT) a partir de arquivos GTFS.

## 🚀 Funcionalidades

- Processamento de arquivos ZIP de GTFS (SPPO e BRT).
- Identificação automática da primeira parada de cada viagem (`stop_sequence` mínima).
- Tratamento de duplicidades geográficas (seleciona o ponto mais frequente para cada linha/sentido).
- Consolidação horizontal: gera um único arquivo CSV com os terminais de ida e volta na mesma linha.
- Suporte a codificação UTF-8 com BOM para compatibilidade direta com o Excel.

## 📋 Pré-requisitos

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (recomendado para gerenciamento de pacotes)

## 🛠️ Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd extrair_terminais_gtfs
   ```

2. **Crie o ambiente virtual e instale as dependências:**
   ```bash
   uv venv
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

## 📂 Estrutura de Dados Esperada

O script busca os dados no caminho configurado na variável `BASE_DADOS` e `ANO_GTFS`. Por padrão, ele espera o arquivo consolidado:

```text
C:/R_SMTR/dados/gtfs/2026/gtfs_rio-de-janeiro_pub.zip
```

*Nota: Você pode ajustar o ano diretamente na constante `ANO_GTFS` no início dos arquivos Python.*

## ⚙️ Como Executar

Com o ambiente ativo, execute:

```bash
- `python extrair_terminais.py`: Extrai apenas os terminais (origens).
- `python extrair_todos_pontos.py`: Extrai todos os pontos de parada.

Ou utilizando o `uv` diretamente:

```bash
uv run extrair_terminais.py
uv run extrair_todos_pontos.py
```

## 📊 Saída

### 1. Terminais (`terminais_linhas_consolidado.csv`)
- `route_short_name`: Número da linha.
- `modal`: Tipo de transporte (SPPO, BRT, etc.).
- `terminal_ida`: Nome do terminal de origem (sentido 0).
- `lat_ida` / `lon_ida`: Coordenadas do terminal de ida.
- `terminal_volta`: Nome do terminal de origem (sentido 1).
- `lat_volta` / `lon_volta`: Coordenadas do terminal de volta.

### 2. Todos os Pontos (`todos_pontos_por_linha_consolidado.csv`)
- `route_short_name`: Número da linha.
- `modal`: Tipo de transporte (SPPO, BRT, etc.).
- `direction_id`: Sentido (0 ou 1).
- `stop_lat` / `stop_lon`: Coordenadas geográficas.
- `stop_name`: Nome do ponto de parada.
- `stop_id`: Identificador da parada.

---
Desenvolvido para auxiliar na gestão e análise de dados de transporte público do Rio de Janeiro.
