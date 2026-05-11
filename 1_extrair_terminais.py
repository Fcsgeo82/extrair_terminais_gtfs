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

def extrair_terminais():
    """Processa o GTFS e retorna os terminais."""
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

    if routes.empty or trips.empty or stop_times.empty or stops.empty:
        print("❌ Erro: Arquivos GTFS essenciais estão vazios ou ausentes.")
        return pd.DataFrame()

    # 2. Identificar a primeira parada de cada viagem (stop_sequence mínima)
    stop_times['stop_sequence'] = pd.to_numeric(stop_times['stop_sequence'])
    # Encontrar o índice da primeira parada por trip_id
    idx_primeira_parada = stop_times.groupby('trip_id')['stop_sequence'].idxmin()
    origens = stop_times.loc[idx_primeira_parada, ['trip_id', 'stop_id']]

    # 3. Associar com rotas e sentidos
    origens = pd.merge(origens, trips[['trip_id', 'route_id', 'direction_id']], on='trip_id')
    
    # 4. Cruzar com informações geográficas
    origens = pd.merge(origens, stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id')
    
    # 5. TRATAMENTO DE DUPLICIDADES
    # Primeiro, consolidamos por coordenadas (XY) para o caso de stop_ids diferentes no mesmo local
    contagem = origens.groupby(['route_id', 'direction_id', 'stop_lat', 'stop_lon']).agg({
        'stop_name': 'first',
        'trip_id': 'count'
    }).reset_index()
    contagem = contagem.rename(columns={'trip_id': 'frequencia'})
    
    # Agora selecionamos a localização (XY) mais frequente para cada (route_id, direction_id)
    terminais_unicos = contagem.sort_values(['route_id', 'direction_id', 'frequencia'], ascending=[True, True, False])
    terminais_unicos = terminais_unicos.groupby(['route_id', 'direction_id']).first().reset_index()

    # 6. Cruzar com routes para obter o número da linha e modal
    terminais_unicos = pd.merge(terminais_unicos, routes[['route_id', 'route_short_name', 'route_type']], on='route_id')

    # Mapeamento de modais
    mapa_modais = {
        '700': 'SPPO',
        '702': 'BRT',
        '200': 'METRÔ',
        '900': 'VLT',
        '3': 'ÔNIBUS'
    }
    terminais_unicos['modal'] = terminais_unicos['route_type'].map(mapa_modais).fillna('OUTROS')

    return terminais_unicos

def main():
    print("🚀 Iniciando extração de terminais GTFS...")
    
    df_terminais = extrair_terminais()
    
    if df_terminais.empty:
        print("❌ Nenhum dado processado.")
        return

    # Separar Ida (0) e Volta (1)
    df_ida = df_terminais[df_terminais['direction_id'] == '0'].copy()
    df_volta = df_terminais[df_terminais['direction_id'] == '1'].copy()

    # Renomear colunas para o merge horizontal
    df_ida = df_ida.rename(columns={
        'stop_name': 'terminal_ida',
        'stop_lat': 'lat_ida',
        'stop_lon': 'lon_ida'
    })
    
    df_volta = df_volta.rename(columns={
        'stop_name': 'terminal_volta',
        'stop_lat': 'lat_volta',
        'stop_lon': 'lon_volta'
    })

    # Pivotar: Mesclar Ida e Volta na mesma linha por route_short_name (número da linha)
    resultado = pd.merge(
        df_ida[['route_short_name', 'modal', 'terminal_ida', 'lat_ida', 'lon_ida']],
        df_volta[['route_short_name', 'terminal_volta', 'lat_volta', 'lon_volta']],
        on='route_short_name',
        how='outer'
    )

    # Ordenar por número de linha
    resultado = resultado.sort_values('route_short_name')

    # Salvar resultado
    output_path = Path("terminais_linhas_consolidado.csv")
    resultado.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Sucesso! Arquivo gerado: {output_path.absolute()}")
    print(f"📊 Total de linhas processadas: {len(resultado)}")

if __name__ == "__main__":
    main()
