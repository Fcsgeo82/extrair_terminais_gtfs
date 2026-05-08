import pandas as pd
import zipfile
import io
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
BASE_DADOS = Path("C:/R_SMTR/dados")
ANO_GTFS = '2026'
MES_GTFS = '05'
ESTUDO_GTFS = '02'

# O script processará tanto SPPO quanto BRT para consolidar no final
MODAIS = ['sppo', 'brt']

def carregar_gtfs_csv(zip_path, filename):
    """Lê um arquivo CSV de dentro do arquivo ZIP do GTFS."""
    with zipfile.ZipFile(zip_path, 'r') as z:
        if filename in z.namelist():
            with z.open(filename) as f:
                return pd.read_csv(f, dtype=str)
    return pd.DataFrame()

def extrair_terminais_modal(modal):
    """Processa um modal específico e retorna os terminais."""
    zip_name = f"{modal}_{ANO_GTFS}-{MES_GTFS}-{ESTUDO_GTFS}Q.zip"
    zip_path = BASE_DADOS / f"gtfs/{ANO_GTFS}/{zip_name}"
    
    if not zip_path.exists():
        print(f"⚠️ Arquivo não encontrado: {zip_path}")
        return pd.DataFrame()

    print(f"📦 Processando {modal.upper()}...")
    
    # 1. Carregar arquivos necessários
    routes = carregar_gtfs_csv(zip_path, 'routes.txt')
    trips = carregar_gtfs_csv(zip_path, 'trips.txt')
    stop_times = carregar_gtfs_csv(zip_path, 'stop_times.txt')
    stops = carregar_gtfs_csv(zip_path, 'stops.txt')

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
    # Agrupamos por Linha, Sentido e Coordenadas
    contagem = origens.groupby(['route_id', 'direction_id', 'stop_lat', 'stop_lon']).agg({
        'stop_name': 'first', # Pega o primeiro nome encontrado para essa coordenada
        'trip_id': 'count'    # Conta frequencia de viagens
    }).reset_index()
    contagem = contagem.rename(columns={'trip_id': 'frequencia'})
    
    # Agora selecionamos a localização (XY) mais frequente para cada (route_id, direction_id)
    terminais_unicos = contagem.sort_values(['route_id', 'direction_id', 'frequencia'], ascending=[True, True, False])
    terminais_unicos = terminais_unicos.groupby(['route_id', 'direction_id']).first().reset_index()

    # 6. Cruzar com routes para obter o número da linha
    terminais_unicos = pd.merge(terminais_unicos, routes[['route_id', 'route_short_name']], on='route_id')

    return terminais_unicos

def main():
    print("🚀 Iniciando extração de terminais GTFS...")
    
    lista_terminais = []
    for m in MODAIS:
        df_modal = extrair_terminais_modal(m)
        if not df_modal.empty:
            lista_terminais.append(df_modal)
    
    if not lista_terminais:
        print("❌ Nenhum dado processado.")
        return

    df_final = pd.concat(lista_terminais, ignore_index=True)

    # Separar Ida (0) e Volta (1)
    df_ida = df_final[df_final['direction_id'] == '0'].copy()
    df_volta = df_final[df_final['direction_id'] == '1'].copy()

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
    # Usamos route_short_name pois route_id pode variar entre modais mas o número da linha é o que importa
    resultado = pd.merge(
        df_ida[['route_short_name', 'terminal_ida', 'lat_ida', 'lon_ida']],
        df_volta[['route_short_name', 'terminal_volta', 'lat_volta', 'lon_volta']],
        on='route_short_name',
        how='outer'
    )

    # Ordenar por número de linha
    resultado = resultado.sort_values('route_short_name')

    # Salvar resultado
    output_dir = Path("C:/R_SMTR/resultados")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "terminais_linhas_consolidado.csv"
    
    resultado.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Sucesso! Arquivo gerado: {output_path.absolute()}")
    print(f"📊 Total de linhas processadas: {len(resultado)}")

if __name__ == "__main__":
    main()
