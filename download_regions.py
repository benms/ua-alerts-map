# -*- coding: utf-8 -*-
import urllib.request

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
        urllib.request.urlretrieve(f"https://{url}&params=0", to_file)
        print(f"Downloading file for {region_name} completed")


def download_alerts():
    url = "https://emapa.fra1.cdn.digitaloceanspaces.com/statuses.json"
    urllib.request.urlretrieve(url, "./src/data/alerts.json")
    print("Downloading alerts/statuses completed")


if __name__ == '__main__':
    download_regions()
    download_alerts()
