# -*- coding: utf-8 -*-
import urllib.request
from pathlib import Path
from shutil import copyfileobj


def download(url, to_file):
    Path(to_file).parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={'User-Agent': 'ua-alerts-map/1.0'})
    with urllib.request.urlopen(request) as response, open(to_file, 'wb') as output:
        copyfileobj(response, output)

region_ids = {
  'Вінницька область': 90726,
  'Волинська область': 71064,
  'Дніпропетровська область': 101746,
  'Донецька область': 71973,
  'Житомирська область': 71245,
  'Закарпатська область': 72489,
  'Запорізька область': 71980,
  'Івано-Франківська область': 72488,
  'Київська область': 71248,
  'Кіровоградська область': 101859,
  'Луганська область': 71971,
  'Львівська область': 72380,
  'Миколаївська область': 72635,
  'Одеська область': 72634,
  'Полтавська область': 91294,
  'Рівненська область': 71236,
  'Сумська область': 71250,
  'Тернопільська область': 72525,
  'Харківська область': 71254,
  'Херсонська область': 71022,
  'Хмельницька область': 90742,
  'Черкаська область': 91278,
  'Чернівецька область': 72526,
  'Чернігівська область': 71249,
  'м. Київ': 421866
}


def download_regions():
    for region_name, region_id in region_ids.items():
        print(f"Downloading file for {region_name}...")
        url = f"polygons.openstreetmap.fr/get_geojson.py?id={region_id}"
        to_file = f"./src/data/regions/{region_name}.json"
        download(f"https://{url}&params=0", to_file)
        print(f"Downloading file for {region_name} completed")


def download_alerts():
    url = "https://vadimklimenko.com/map/statuses.json"
    download(url, "./src/data/alerts.json")
    print("Downloading alerts/statuses completed")


if __name__ == '__main__':
    download_regions()
    download_alerts()
