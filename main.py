import pandas as pd
import requests
import json
import csv
import time
from tqdm import tqdm

# Abrir a API e ver todas os dados possiveis dela, assim posso puxar cada uma
def list_all_endpoints():
    base_url = "https://pokeapi.co/api/v2/"
    response = requests.get(base_url)

    if response.status_code == 200:
        endpoints = response.json()
        print("Endpoints principais disponíveis:")
        for endpoint, url in endpoints.items():
            print(f"- {endpoint:20} → {url}")
    else:
        print("Erro ao acessar a API")

list_all_endpoints()

# Configurações
BASE_URL = "https://pokeapi.co/api/v2/"
DELAY = 0.1

#fazer as tabelas
SELECTED_ENDPOINTS = {
    'pokemon': {
        'fields': ['id', 'name', 'height', 'weight', 'base_experience',
                  'types', 'abilities', 'stats_hp', 'stats_attack',
                  'stats_defense', 'stats_special_attack',
                  'stats_special_defense', 'stats_speed'],
        'processor': lambda d: {
            'id': d['id'],
            'name': d['name'],
            'height': d['height'],
            'weight': d['weight'],
            'base_experience': d['base_experience'],
            'types': ', '.join([t['type']['name'] for t in d['types']]),
            'abilities': ', '.join([a['ability']['name'] for a in d['abilities']]),
            'stats_hp': next(s['base_stat'] for s in d['stats'] if s['stat']['name'] == 'hp'),
            'stats_attack': next(s['base_stat'] for s in d['stats'] if s['stat']['name'] == 'attack'),
            'stats_defense': next(s['base_stat'] for s in d['stats'] if s['stat']['name'] == 'defense'),
            'stats_special_attack': next(s['base_stat'] for s in d['stats'] if s['stat']['name'] == 'special-attack'),
            'stats_special_defense': next(s['base_stat'] for s in d['stats'] if s['stat']['name'] == 'special-defense'),
            'stats_speed': next(s['base_stat'] for s in d['stats'] if s['stat']['name'] == 'speed')
        }
    },
    'region': {
        'fields': ['id', 'name', 'locations', 'main_generation', 'pokedexes'],
        'processor': lambda d: {
            'id': d['id'],
            'name': d['name'],
            'locations': ', '.join([loc['name'] for loc in d['locations']]),
            'main_generation': d['main_generation']['name'] if d['main_generation'] else '',
            'pokedexes': ', '.join([p['name'] for p in d['pokedexes']])
        }
    },
    'ability': {
        'fields': ['id', 'name', 'generation', 'effect', 'short_effect', 'pokemon'],
        'processor': lambda d: {
            'id': d['id'],
            'name': d['name'],
            'generation': d['generation']['name'],
            'effect': next((e['effect'] for e in d['effect_entries'] if e['language']['name'] == 'en'), ''),
            'short_effect': next((e['short_effect'] for e in d['effect_entries'] if e['language']['name'] == 'en'), ''),
            'pokemon': ', '.join([p['pokemon']['name'] for p in d['pokemon']])
        }
    },
    'type': {
        'fields': ['id', 'name', 'damage_relations', 'generation', 'move_damage_class', 'pokemon'],
        'processor': lambda d: {
            'id': d['id'],
            'name': d['name'],
            'damage_relations': str({k: [x['name'] for x in v] for k, v in d['damage_relations'].items()}),
            'generation': d['generation']['name'],
            'move_damage_class': d['move_damage_class']['name'] if d['move_damage_class'] else '',
            'pokemon': ', '.join([p['pokemon']['name'] for p in d['pokemon']])
        }
    },
    'pokedex': {
        'fields': ['id', 'name', 'region', 'description', 'pokemon_entries'],
        'processor': lambda d: {
            'id': d['id'],
            'name': d['name'],
            'region': d['region']['name'] if d['region'] else '',
            'description': next((e['description'] for e in d['descriptions'] if e['language']['name'] == 'en'), ''),
            'pokemon_entries': str([p['pokemon_species']['name'] for p in d['pokemon_entries']])
        }
    },
    'nature': {
        'fields': ['id', 'name', 'decreased_stat', 'increased_stat', 'hates_flavor', 'likes_flavor'],
        'processor': lambda d: {
            'id': d['id'],
            'name': d['name'],
            'decreased_stat': d['decreased_stat']['name'] if d['decreased_stat'] else '',
            'increased_stat': d['increased_stat']['name'] if d['increased_stat'] else '',
            'hates_flavor': d['hates_flavor']['name'] if d['hates_flavor'] else '',
            'likes_flavor': d['likes_flavor']['name'] if d['likes_flavor'] else ''
        }
    },
    'stat': {
        'fields': ['id', 'name', 'is_battle_only', 'affecting_moves', 'affecting_natures', 'characteristics'],
        'processor': lambda d: {
            'id': d['id'],
            'name': d['name'],
            'is_battle_only': d['is_battle_only'],
            'affecting_moves': str({k: [x['name'] for x in v] for k, v in d['affecting_moves'].items()}),
            'affecting_natures': str({k: [x['name'] for x in v] for k, v in d['affecting_natures'].items()}),
            'characteristics': ', '.join([c['name'] for c in d['characteristics']])
        }
    }
}

def get_all_resources(endpoint):
    """Obtém todos os recursos de um endpoint com paginação"""
    resources = []
    url = f"{BASE_URL}{endpoint}?limit=1000"

    while url:
        time.sleep(DELAY)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            resources.extend(data['results'])
            url = data.get('next')
        else:
            print(f"Erro ao acessar {url}")
            break

    return resources

def generate_csv_for_endpoint(endpoint, config):
    """Gera um arquivo CSV para um endpoint específico"""
    print(f"\nProcessando {endpoint}...")

    # Obter todos os recursos
    resources = get_all_resources(endpoint)

    # Coletar dados completos
    all_data = []
    for resource in tqdm(resources, desc=f"Baixando {endpoint}"):
        time.sleep(DELAY)
        try:
            data = requests.get(resource['url']).json()
            processed = config['processor'](data)
            all_data.append(processed)
        except Exception as e:
            print(f"\nErro ao processar {resource['url']}: {str(e)}")

    # Escrever CSV
    if all_data:
        filename = f"pokeapi_{endpoint}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=config['fields'])
            writer.writeheader()
            writer.writerows(all_data)
        print(f" Arquivo {filename} criado com {len(all_data)} registros.")
    else:
        print(f" Nenhum dado válido encontrado para {endpoint}.")

if __name__ == "__main__":
    for endpoint, config in SELECTED_ENDPOINTS.items():
        generate_csv_for_endpoint(endpoint, config)

    print("\n Todos os arquivos CSV foram gerados com sucesso!")

# Puxar todas as fotos dos pokemons (vai ficar bonitinho no looker)

def generate_official_artwork_url(pokemon_id):
    """Gera a URL da imagem oficial do Pokémon"""
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"


def create_images_csv(pokemon_csv_path, output_csv_path):
    """Cria um CSV com IDs, nomes e URLs das imagens oficiais"""

    # Ler o CSV original de Pokémon
    with open(pokemon_csv_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        pokemon_list = list(reader)

    # Preparar dados para o novo CSV
    image_data = []

    for pokemon in tqdm(pokemon_list, desc="Processando Pokémon"):
        pokemon_id = pokemon['id']
        image_url = generate_official_artwork_url(pokemon_id)


        image_data.append({
            'id': pokemon_id,
            'name': pokemon['name'],
            'image_url': image_url,
            'official_artwork': image_url,
            'sprite_default': f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png",
            'sprite_shiny': f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{pokemon_id}.png"
        })

    # Escrever o novo CSV
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'image_url', 'official_artwork', 'sprite_default', 'sprite_shiny']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(image_data)

    print(f"\n✅ Arquivo {output_csv_path} criado com {len(image_data)} Pokémon!")



POKEMON_CSV_PATH = 'pokeapi_pokemon.csv' 
IMAGES_CSV_PATH = 'pokemon_images.csv'  

# Executar
if __name__ == "__main__":
    create_images_csv(POKEMON_CSV_PATH, IMAGES_CSV_PATH)
