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

O script busca os dados no caminho configurado na variável `BASE_DADOS`. Por padrão, ele espera a seguinte estrutura:

```text
C:/R_SMTR/dados/gtfs/2026/
├── sppo_2026-05-02Q.zip
└── brt_2026-05-02Q.zip
```

*Nota: Você pode ajustar o ano, mês e versão do estudo diretamente nas constantes no início do arquivo `extrair_terminais.py`.*

## ⚙️ Como Executar

Com o ambiente ativo, execute:

```bash
python extrair_terminais.py
```

Ou utilizando o `uv` diretamente:

```bash
uv run extrair_terminais.py
```

## 📊 Saída

O script gera o arquivo **`terminais_linhas_consolidado.csv`** na raiz do projeto, contendo as seguintes colunas:

- `route_short_name`: Número da linha.
- `terminal_ida`: Nome do terminal de origem (sentido 0).
- `lat_ida` / `lon_ida`: Coordenadas do terminal de ida.
- `terminal_volta`: Nome do terminal de origem (sentido 1).
- `lat_volta` / `lon_volta`: Coordenadas do terminal de volta.

---
Desenvolvido para auxiliar na gestão e análise de dados de transporte público do Rio de Janeiro.
