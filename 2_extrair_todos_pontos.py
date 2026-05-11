import pandas as pd
import zipfile
import io
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
BASE_DADOS = Path("C:/R_SMTR/dados")
ANO_GTFS = '2026'

# Nome do arquivo GTFS público consolidado
ARQUIVO_GTFS = "gtfs_rio-de-janeiro_pub.zip"

def carregar_gtfs_csv(zip_path, filename):
    """Lê um arquivo CSV de dentro do arquivo ZIP do GTFS."""
    with zipfile.ZipFile(zip_path, 'r') as z:
        if filename in z.namelist():
            with z.open(filename) as f:
                return pd.read_csv(f, dtype=str)
    return pd.DataFrame()

def extrair_todos_pontos():
    """Processa o GTFS e retorna todos os pontos de parada por linha/sentido em ordem sequencial."""
    zip_path = BASE_DADOS / f"gtfs/{ANO_GTFS}/{ARQUIVO_GTFS}"
    
    if not zip_path.exists():
        print(f"⚠️ Arquivo não encontrado: {zip_path}")
        return pd.DataFrame()

    print(f"📦 Processando {ARQUIVO_GTFS}...")
    
    # 1. Carregar arquivos necessários
    routes = carregar_gtfs_csv(zip_path, 'routes.txt')
    trips = carregar_gtfs_csv(zip_path, 'trips.txt')
    stop_times = carregar_gtfs_csv(zip_path, 'stop_times.txt')
    stops = carregar_gtfs_csv(zip_path, 'stops.txt')

    if stop_times.empty or trips.empty or stops.empty or routes.empty:
        print(f"❌ Arquivos essenciais ausentes no ZIP {ARQUIVO_GTFS}")
        return pd.DataFrame()

    # Converter stop_sequence para numérico para ordenação correta
    stop_times['stop_sequence'] = pd.to_numeric(stop_times['stop_sequence'])

    # 2. Associar stop_times com trips (para obter route_id e direction_id)
    df = pd.merge(
        stop_times[['trip_id', 'stop_id', 'stop_sequence']], 
        trips[['trip_id', 'route_id', 'direction_id']], 
        on='trip_id'
    )
    
    # 3. Associar com stops (para obter coordenadas e nomes)
    df = pd.merge(
        df, 
        stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], 
        on='stop_id'
    )
    
    # 4. Associar com routes (para obter o número da linha e modal)
    df = pd.merge(
        df, 
        routes[['route_id', 'route_short_name', 'route_type']], 
        on='route_id'
    )

    # 5. REMOÇÃO DE DUPLICIDADES E ORDENAÇÃO
    # Calculamos a sequência média para cada ponto único dentro da linha/sentido
    df_deduplicado = df.groupby(['route_short_name', 'direction_id', 'stop_lat', 'stop_lon']).agg({
        'stop_name': 'first',
        'stop_id': 'first',
        'route_type': 'first', # Mantemos o tipo da rota para o modal
        'stop_sequence': 'mean' 
    }).reset_index()

    # Mapeamento de modais
    mapa_modais = {
        '700': 'SPPO',
        '702': 'BRT',
        '200': 'METRÔ',
        '900': 'VLT',
        '3': 'ÔNIBUS'
    }
    df_deduplicado['modal'] = df_deduplicado['route_type'].map(mapa_modais).fillna('OUTROS')

    # 6. Ordenar por Linha, Sentido e Sequência
    df_deduplicado = df_deduplicado.sort_values(['route_short_name', 'direction_id', 'stop_sequence'])

    print(f"✨ Pontos únicos identificados e ordenados: {len(df_deduplicado)}")
    
    return df_deduplicado

def main():
    print("🚀 Iniciando extração de todos os pontos de parada GTFS...")
    
    df_final = extrair_todos_pontos()
    
    if df_final.empty:
        print("❌ Nenhum dado processado.")
        return

    # Salvar resultado
    output_path = Path("todos_pontos_por_linha_consolidado.csv")
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Sucesso! Arquivo gerado: {output_path.absolute()}")
    print(f"📊 Total de pontos únicos (Linha/Sentido/XY): {len(df_final)}")

if __name__ == "__main__":
    main()
