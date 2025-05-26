import numpy as np
import pandas as pd
import folium
import random
from datetime import datetime, timedelta
# from IPython.display import display, HTML

# Library untuk optimasi rute
import geopy.distance as geodist  # Untuk menghitung jarak antar lokasi
import networkx as nx  # Untuk representasi graf

# DEAP untuk algoritma genetika (alternatif ke mlrose)
from deap import base, creator, tools, algorithms

# 1. Data tempat wisata - menggunakan pandas DataFrame
def create_tourism_data():
    tourism_data = {
        'id': list(range(1, 16)),
        'name': [
            'Candi Borobudur', 'Candi Prambanan', 'Kraton Yogyakarta', 'Malioboro',
            'Taman Sari', 'Pantai Parangtritis', 'Goa Pindul', 'Gunung Merapi',
            'Keraton Ratu Boko', 'Candi Sewu', 'Museum Affandi', 'Alun-Alun Kidul',
            'Pantai Indrayanti', 'Hutan Pinus Pengger', 'Desa Wisata Kasongan'
        ],
        'latitude': [
            -7.6079, -7.7520, -7.8050, -7.7929,
            -7.8100, -8.0257, -7.9515, -7.5407,
            -7.7701, -7.7426, -7.7828, -7.8120,
            -8.1512, -7.8684, -7.8450
        ],
        'longitude': [
            110.2038, 110.4914, 110.3644, 110.3668,
            110.3594, 110.3329, 110.6543, 110.4457,
            110.4892, 110.4939, 110.3957, 110.3644,
            110.6129, 110.3985, 110.3490
        ],
        'category': [
            'Budaya', 'Budaya', 'Budaya', 'Belanja',
            'Budaya', 'Alam', 'Alam', 'Alam',
            'Budaya', 'Budaya', 'Budaya', 'Rekreasi',
            'Alam', 'Alam', 'Budaya'
        ],
        'open_time': [
            '06:00', '06:00', '08:00', '08:00',
            '08:00', '07:00', '08:00', '07:00',
            '06:00', '06:00', '09:00', '18:00',
            '07:00', '07:00', '08:00'
        ],
        'close_time': [
            '17:00', '17:00', '14:00', '21:00',
            '15:00', '18:00', '17:00', '17:00',
            '17:00', '17:00', '16:00', '23:00',
            '18:00', '18:00', '17:00'
        ],
        'visit_duration_min': [
            120, 120, 90, 180,
            60, 120, 90, 240,
            60, 60, 60, 60,
            180, 90, 120
        ],
        'entrance_fee': [
            50000, 50000, 15000, 0,
            15000, 10000, 35000, 10000,
            25000, 30000, 20000, 0,
            10000, 5000, 5000
        ],
        'popularity': [
            9.5, 9.0, 8.5, 9.0,
            8.0, 8.0, 8.2, 8.5,
            7.5, 7.0, 7.5, 8.0,
            8.2, 7.8, 7.5
        ],
        'crowdedness_factor': [
            0.9, 0.8, 0.7, 0.9,
            0.6, 0.7, 0.6, 0.5,
            0.4, 0.4, 0.3, 0.7,
            0.7, 0.5, 0.4
        ]
    }

    return pd.DataFrame(tourism_data)

# 2. Preferensi pengguna
def create_user_preferences():
    preferences = {
        'start_time': '08:00',
        'end_time': '20:00',
        'max_places': 6,
        'budget': 200000,
        'preferred_categories': ['Budaya', 'Alam'],
        'must_visit': [1, 2],  # ID tempat yang harus dikunjungi
        'avoid_places': [],
        'lunch_time': '12:00',
        'lunch_duration': 60,  # Menit
        'start_location': {
            'name': 'Hotel Malioboro',
            'latitude': -7.7925,
            'longitude': 110.3668
        },
        'end_location': {
            'name': 'Hotel Malioboro',
            'latitude': -7.7925,
            'longitude': 110.3668
        }
    }

    return preferences

# 3. Membuat data dinamis (traffic, cuaca)
def create_dynamic_data():
    # Data lalu lintas berdasarkan jam
    traffic_by_hour = {hour: 1.5 if (7 <= hour <= 9 or 16 <= hour <= 19) else
                            1.2 if 10 <= hour <= 15 else 1.0
                       for hour in range(24)}

    dynamic_data = {
        'traffic_by_hour': traffic_by_hour,
        'weather_condition': "Cerah",
        'is_weekend': True,
        'crowdedness_factor': 1.5,  # Weekend factor
        'closed_places': []
    }

    return dynamic_data


def update_dynamic_data(current_time, old_dynamic_data=None):
    """
    Memperbarui data dinamis berdasarkan waktu saat ini

    Args:
        current_time (datetime): Waktu saat ini
        old_dynamic_data (dict, optional): Data dinamis lama yang akan diperbarui

    Returns:
        dict: Data dinamis yang sudah diperbarui
    """
    # Jika tidak ada data lama, buat data baru
    if old_dynamic_data is None:
        old_dynamic_data = create_dynamic_data()

    # Salin data lama ke data baru
    dynamic_data = old_dynamic_data.copy()

    # Simulasi API cuaca - dalam implementasi nyata, ini akan memanggil API cuaca
    # Misalnya menggunakan OpenWeatherMap, AccuWeather, dll.
    hour = current_time.hour

    # Simulasi perubahan cuaca berdasarkan waktu
    if 6 <= hour < 11:
        weather = "Cerah"
    elif 11 <= hour < 15:
        weather = "Panas" if random.random() < 0.7 else "Berawan"
    elif 15 <= hour < 18:
        weather = "Berawan" if random.random() < 0.6 else "Hujan Ringan"
    else:
        weather = "Cerah Berawan"

    dynamic_data['weather_condition'] = weather

    # Perbarui faktor keramaian berdasarkan cuaca dan waktu
    crowd_multiplier = 1.0
    if weather == "Hujan Ringan" or weather == "Hujan":
        crowd_multiplier = 0.7
    elif weather == "Panas":
        crowd_multiplier = 0.9

    # Weekend tetap ramai
    is_weekend = old_dynamic_data.get('is_weekend', True)
    base_crowd = 1.5 if is_weekend else 1.0

    # Keramaian juga dipengaruhi waktu
    if 10 <= hour <= 14:  # Jam puncak wisata
        time_multiplier = 1.3
    else:
        time_multiplier = 1.0

    dynamic_data['crowdedness_factor'] = base_crowd * crowd_multiplier * time_multiplier

    # Perbarui data lalu lintas - dalam implementasi nyata, gunakan API Maps
    # Perbarui traffic_by_hour untuk jam saat ini berdasarkan kondisi cuaca
    traffic_multiplier = 1.0
    if weather == "Hujan Ringan":
        traffic_multiplier = 1.3
    elif weather == "Hujan":
        traffic_multiplier = 1.5

    # Buat salinan traffic_by_hour
    traffic_by_hour = old_dynamic_data.get('traffic_by_hour', {}).copy()

    # Perbarui jam saat ini dengan data lalu lintas terbaru
    base_traffic = traffic_by_hour.get(hour, 1.0)
    traffic_by_hour[hour] = base_traffic * traffic_multiplier

    dynamic_data['traffic_by_hour'] = traffic_by_hour

    # Perbarui tempat yang tutup (misalnya karena cuaca buruk)
    closed_places = []
    if weather == "Hujan" and random.random() < 0.3:
        # Beberapa tempat outdoor mungkin tutup saat hujan deras
        outdoor_places = [6, 7, 8, 13, 14]  # ID tempat outdoor
        closed_places = random.sample(outdoor_places, 1)  # Tutup 1 tempat secara acak

    dynamic_data['closed_places'] = closed_places

    return dynamic_data

# 4. Menciptakan matriks jarak menggunakan geopy
def create_distance_matrix(df):
    n = len(df)
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                # Menggunakan geopy untuk menghitung jarak
                point1 = (df.iloc[i]['latitude'], df.iloc[i]['longitude'])
                point2 = (df.iloc[j]['latitude'], df.iloc[j]['longitude'])
                distance_matrix[i][j] = geodist.distance(point1, point2).km

    return distance_matrix

# 5. Membuat matriks waktu tempuh
def create_travel_time_matrix(distance_matrix, traffic_factor=1.2):
    # Asumsi rata-rata 40 km/jam
    return (distance_matrix / 40) * 60 * traffic_factor

# 6. Fitness function untuk mlrose
def fitness_function(route, df_places, preferences, distance_matrix, time_matrix, dynamic_data):
    """Evaluasi fitness dari rute"""
    # Skip jika rute kosong
    if not route:
        return -1000  # Penalti besar

    # Penalti untuk tempat wajib yang tidak dikunjungi
    must_visit_penalty = 0
    for place_id in preferences['must_visit']:
        if place_id not in route:
            must_visit_penalty += 10000

    # Hitung total budget
    budget_used = sum(df_places.iloc[place_id-1]['entrance_fee'] for place_id in route)
    budget_penalty = 0
    if budget_used > preferences['budget']:
        budget_penalty = 15000 * (budget_used / preferences['budget'])

    # Hitung total jarak
    total_distance = 0

    # Jarak dari hotel ke tempat pertama
    if route:
        start_loc = (preferences['start_location']['latitude'], preferences['start_location']['longitude'])
        first_loc = (df_places.iloc[route[0]-1]['latitude'], df_places.iloc[route[0]-1]['longitude'])
        total_distance += geodist.distance(start_loc, first_loc).km

    # Jarak antar tempat
    for i in range(len(route)-1):
        idx1, idx2 = route[i]-1, route[i+1]-1
        total_distance += distance_matrix[idx1][idx2]

    # Jarak kembali ke hotel
    if route:
        end_loc = (preferences['end_location']['latitude'], preferences['end_location']['longitude'])
        last_loc = (df_places.iloc[route[-1]-1]['latitude'], df_places.iloc[route[-1]-1]['longitude'])
        total_distance += geodist.distance(last_loc, end_loc).km

    # Hitung score lainnya berdasarkan preferensi kategori dan popularitas
    category_score = sum(1 for place_id in route if df_places.iloc[place_id-1]['category'] in preferences['preferred_categories'])
    category_score = category_score / len(route) if route else 0

    popularity_score = sum(df_places.iloc[place_id-1]['popularity'] for place_id in route)
    popularity_score = popularity_score / len(route) if route else 0

    # Cek apakah jadwal sesuai waktu
    start_time = datetime.strptime(preferences['start_time'], '%H:%M')
    current_time = start_time
    lunch_time = datetime.strptime(preferences['lunch_time'], '%H:%M')
    lunch_taken = False
    time_feasible = True

    # Simulasi jadwal
    for i, place_id in enumerate(route):
        place_idx = place_id - 1
        place = df_places.iloc[place_idx]

        # Tambah waktu tempuh
        if i > 0:
            prev_idx = route[i-1] - 1
            travel_time = time_matrix[prev_idx][place_idx]
            hour = current_time.hour
            traffic_factor = dynamic_data['traffic_by_hour'].get(hour, 1.0)
            current_time += timedelta(minutes=travel_time * traffic_factor)

        # Cek waktu makan siang
        if not lunch_taken and current_time >= lunch_time:
            current_time += timedelta(minutes=preferences['lunch_duration'])
            lunch_taken = True

        # Cek jam buka/tutup
        place_open = datetime.strptime(place['open_time'], '%H:%M').time()
        place_close = datetime.strptime(place['close_time'], '%H:%M').time()

        if current_time.time() < place_open:
            current_time = datetime.combine(current_time.date(), place_open)

        if current_time.time() > place_close:
            time_feasible = False
            break

        # Tambah waktu kunjungan
        visit_time = place['visit_duration_min'] * dynamic_data['crowdedness_factor'] * place['crowdedness_factor']
        current_time += timedelta(minutes=visit_time)

    # Cek apakah kembali sebelum end_time
    end_time = datetime.strptime(preferences['end_time'], '%H:%M')
    if current_time > end_time:
        time_feasible = False

    # Hitung fitness
    place_count_score = len(route) / preferences['max_places']
    distance_score = 1 - (total_distance / 200) if total_distance <= 200 else 0

    fitness = (
        0.40 * place_count_score +
        0.15 * distance_score +
        0.20 * category_score +
        0.25 * popularity_score
    ) * 100

    # Kurangi penalti
    fitness -= budget_penalty + must_visit_penalty
    if not time_feasible:
        fitness -= 5000

    return fitness

# 7. Fungsi untuk membangun dan mengoptimasi rute dengan DEAP
def optimize_route(df_places, preferences, distance_matrix, travel_time_matrix, dynamic_data):
    """Optimasi rute menggunakan algoritma genetika dengan DEAP"""
    # Buat tipe fitness
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    # Registrasi fungsi untuk inisialisasi individu (rute)
    def create_valid_place():
        # Mengembalikan ID tempat 1-15 (harus dikurangi 1 karena Python 0-indexed)
        return random.randint(1, len(df_places))

    # Inisialisasi individu dengan memastikan elemen unik (tidak ada tempat dikunjungi 2x)
    def init_individual():
        # Mulai dengan tempat yang harus dikunjungi
        individual = preferences['must_visit'].copy()

        # Tambah tempat secara acak
        potential_places = [i for i in range(1, len(df_places)+1)
                           if i not in individual and i not in preferences['avoid_places']]

        # Batasi sesuai budget dan max_places
        random.shuffle(potential_places)
        current_budget = sum(df_places.iloc[p-1]['entrance_fee'] for p in individual)

        for place_id in potential_places:
            if len(individual) >= preferences['max_places']:
                break

            fee = df_places.iloc[place_id-1]['entrance_fee']
            if current_budget + fee <= preferences['budget']:
                individual.append(place_id)
                current_budget += fee

        random.shuffle(individual)  # Acak urutan
        return individual

    # Registrasi fungsi
    toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Fungsi fitness
    def eval_route(route):
        """Evaluasi fitness dari rute"""
        # Check jika rute kosong
        if not route:
            return (-1000,)  # Penalti besar

        # Pengecekan tempat wajib
        must_visit_penalty = 0
        for place_id in preferences['must_visit']:
            if place_id not in route:
                must_visit_penalty += 10000

        # Hitung total budget
        budget_used = sum(df_places.iloc[place_id-1]['entrance_fee'] for place_id in route)
        budget_penalty = 0
        if budget_used > preferences['budget']:
            budget_penalty = 15000 * (budget_used / preferences['budget'])

        # Hitung jarak total
        total_distance = 0

        # Jarak dari hotel ke tempat pertama
        if route:
            start_loc = (preferences['start_location']['latitude'], preferences['start_location']['longitude'])
            first_loc = (df_places.iloc[route[0]-1]['latitude'], df_places.iloc[route[0]-1]['longitude'])
            total_distance += geodist.distance(start_loc, first_loc).km

        # Jarak antar tempat
        for i in range(len(route)-1):
            idx1, idx2 = route[i]-1, route[i+1]-1
            total_distance += distance_matrix[idx1][idx2]

        # Jarak kembali ke hotel
        if route:
            end_loc = (preferences['end_location']['latitude'], preferences['end_location']['longitude'])
            last_loc = (df_places.iloc[route[-1]-1]['latitude'], df_places.iloc[route[-1]-1]['longitude'])
            total_distance += geodist.distance(last_loc, end_loc).km

        # Score kategori dan popularitas
        category_score = sum(1 for place_id in route if df_places.iloc[place_id-1]['category'] in preferences['preferred_categories'])
        category_score = category_score / len(route) if route else 0

        popularity_score = sum(df_places.iloc[place_id-1]['popularity'] for place_id in route)
        popularity_score = popularity_score / len(route) if route else 0

        # Cek waktu
        start_time = datetime.strptime(preferences['start_time'], '%H:%M')
        current_time = start_time
        lunch_time = datetime.strptime(preferences['lunch_time'], '%H:%M')
        lunch_taken = False
        time_feasible = True

        # Simulasi jadwal
        for i, place_id in enumerate(route):
            place_idx = place_id - 1
            place = df_places.iloc[place_idx]

            # Tambah waktu tempuh
            if i > 0:
                prev_idx = route[i-1] - 1
                travel_time = travel_time_matrix[prev_idx][place_idx]
                hour = current_time.hour
                traffic_factor = dynamic_data['traffic_by_hour'].get(hour, 1.0)
                current_time += timedelta(minutes=travel_time * traffic_factor)

            # Cek makan siang
            if not lunch_taken and current_time >= lunch_time:
                current_time += timedelta(minutes=preferences['lunch_duration'])
                lunch_taken = True

            # Cek jam buka/tutup
            place_open = datetime.strptime(place['open_time'], '%H:%M').time()
            place_close = datetime.strptime(place['close_time'], '%H:%M').time()

            if current_time.time() < place_open:
                current_time = datetime.combine(current_time.date(), place_open)

            if current_time.time() > place_close:
                time_feasible = False
                break

            # Tambah waktu kunjungan
            visit_time = place['visit_duration_min'] * dynamic_data['crowdedness_factor'] * place['crowdedness_factor']
            current_time += timedelta(minutes=visit_time)

        # Cek selesai tepat waktu
        end_time = datetime.strptime(preferences['end_time'], '%H:%M')
        if current_time > end_time:
            time_feasible = False

        # Hitung fitness
        place_count_score = len(route) / preferences['max_places']
        distance_score = 1 - (total_distance / 200) if total_distance <= 200 else 0

        fitness = (
            0.40 * place_count_score +
            0.15 * distance_score +
            0.20 * category_score +
            0.25 * popularity_score
        ) * 100

        # Kurangi penalti
        fitness -= budget_penalty + must_visit_penalty
        if not time_feasible:
            fitness -= 5000

        return (fitness,)

    # Registrasi fungsi evaluasi
    toolbox.register("evaluate", eval_route)

    # Custom crossover untuk rute dengan panjang variabel
    def custom_cx(ind1, ind2):
        """Custom crossover yang menjaga tempat wajib dan validitas rute"""
        if not ind1 or not ind2:
            return ind1, ind2

        # Pilih titik crossover
        if len(ind1) > 1 and len(ind2) > 1:
            cx_point1 = random.randint(0, len(ind1)-1)
            cx_point2 = random.randint(0, len(ind2)-1)

            # Buat offspring dengan menggabungkan segmen
            offspring1 = ind1[:cx_point1] + [x for x in ind2 if x not in ind1[:cx_point1]]
            offspring2 = ind2[:cx_point2] + [x for x in ind1 if x not in ind2[:cx_point2]]

            # Pastikan tempat wajib ada
            for must_visit_id in preferences['must_visit']:
                if must_visit_id not in offspring1:
                    offspring1.append(must_visit_id)
                if must_visit_id not in offspring2:
                    offspring2.append(must_visit_id)

            # Batasi jumlah tempat dan budget
            while len(offspring1) > preferences['max_places']:
                # Pilih tempat opsional untuk dihapus
                optional = [p for p in offspring1 if p not in preferences['must_visit']]
                if optional:
                    to_remove = random.choice(optional)
                    offspring1.remove(to_remove)
                else:
                    break

            while len(offspring2) > preferences['max_places']:
                optional = [p for p in offspring2 if p not in preferences['must_visit']]
                if optional:
                    to_remove = random.choice(optional)
                    offspring2.remove(to_remove)
                else:
                    break

            # Cek budget dan hapus tempat yang paling mahal jika melebihi
            budget1 = sum(df_places.iloc[p-1]['entrance_fee'] for p in offspring1)
            while budget1 > preferences['budget'] and len(offspring1) > len(preferences['must_visit']):
                optional = [p for p in offspring1 if p not in preferences['must_visit']]
                if optional:
                    # Pilih yang paling mahal
                    to_remove = max(optional, key=lambda p: df_places.iloc[p-1]['entrance_fee'])
                    offspring1.remove(to_remove)
                    budget1 -= df_places.iloc[to_remove-1]['entrance_fee']
                else:
                    break

            budget2 = sum(df_places.iloc[p-1]['entrance_fee'] for p in offspring2)
            while budget2 > preferences['budget'] and len(offspring2) > len(preferences['must_visit']):
                optional = [p for p in offspring2 if p not in preferences['must_visit']]
                if optional:
                    to_remove = max(optional, key=lambda p: df_places.iloc[p-1]['entrance_fee'])
                    offspring2.remove(to_remove)
                    budget2 -= df_places.iloc[to_remove-1]['entrance_fee']
                else:
                    break

            # Acak urutan
            random.shuffle(offspring1)
            random.shuffle(offspring2)

            ind1[:] = offspring1
            ind2[:] = offspring2

        return ind1, ind2

    toolbox.register("mate", custom_cx)

    # Mutasi khusus: swap, insert, atau add/remove
    def custom_mutate(individual, indpb):
        if random.random() < indpb and len(individual) >= 2:
            # Swap mutation
            idx1, idx2 = random.sample(range(len(individual)), 2)
            individual[idx1], individual[idx2] = individual[idx2], individual[idx1]

        if random.random() < indpb and len(individual) >= 2:
            # Insert mutation
            idx1 = random.randint(0, len(individual) - 1)
            idx2 = random.randint(0, len(individual) - 1)
            if idx1 != idx2:
                value = individual.pop(idx1)
                individual.insert(idx2, value)

        # Add/remove mutation
        if random.random() < indpb * 1.5:  # Lebih sering
            # Cek budget saat ini
            current_budget = sum(df_places.iloc[p-1]['entrance_fee'] for p in individual)

            # Tambah tempat jika memungkinkan
            if len(individual) < preferences['max_places']:
                available_places = [i for i in range(1, len(df_places)+1)
                                   if i not in individual and i not in preferences['avoid_places']]
                if available_places:
                    new_place = random.choice(available_places)
                    fee = df_places.iloc[new_place-1]['entrance_fee']
                    if current_budget + fee <= preferences['budget']:
                        individual.append(new_place)

            # Hapus tempat opsional
            if random.random() < indpb and len(individual) > 1:
                optional_places = [p for p in individual if p not in preferences['must_visit']]
                if optional_places:
                    to_remove = random.choice(optional_places)
                    individual.remove(to_remove)

        return individual,

    toolbox.register("mutate", custom_mutate, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Jalankan algoritma genetika
    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)

    pop, logbook = algorithms.eaSimple(
        pop, toolbox, cxpb=0.7, mutpb=0.3,
        ngen=150, stats=stats, halloffame=hof, verbose=True
    )

    # Ekstrak solusi terbaik
    best_route = hof[0]

    # Buat jadwal dari rute terbaik
    schedule = create_schedule(best_route, df_places, preferences, distance_matrix, travel_time_matrix, dynamic_data)

    # Ekstrak fitness history
    gen = logbook.select("gen")
    fit_max = logbook.select("max")
    fit_avg = logbook.select("avg")

    return {
        'best_route': best_route,
        'best_fitness': hof[0].fitness.values[0],
        'fitness_curve': {'gen': gen, 'max': fit_max, 'avg': fit_avg},
        'schedule': schedule
    }


def reoptimize_route(current_route, current_position, df_places, preferences,
                     distance_matrix, travel_time_matrix, current_time):
    """
    Mengoptimasi ulang rute berdasarkan posisi dan waktu saat ini

    Args:
        current_route (list): Rute saat ini
        current_position (int): Indeks tempat saat ini dalam rute
        df_places (DataFrame): Data tempat wisata
        preferences (dict): Preferensi pengguna
        distance_matrix (array): Matriks jarak
        travel_time_matrix (array): Matriks waktu tempuh
        current_time (datetime): Waktu saat ini

    Returns:
        dict: Hasil optimasi rute baru
    """
    # Perbarui data dinamis
    dynamic_data = update_dynamic_data(current_time)

    # Periksa apakah kita sudah selesai dengan rute
    if current_position >= len(current_route) - 1:
        print("Anda sudah berada di tempat terakhir dalam rute.")
        return {
            'best_route': current_route,
            'best_fitness': 0,
            'schedule': create_schedule(current_route, df_places, preferences,
                                        distance_matrix, travel_time_matrix, dynamic_data),
            'dynamic_data': dynamic_data
        }

    # Ambil tempat yang sudah dikunjungi
    visited_places = current_route[:current_position + 1]

    # Ambil tempat yang belum dikunjungi
    remaining_places = current_route[current_position + 1:]

    # Perbarui preferensi dengan menambahkan tempat yang sudah dikunjungi ke must_visit
    new_preferences = preferences.copy()
    new_preferences['must_visit'] = []  # Reset must_visit
    new_preferences['avoid_places'] = preferences.get('avoid_places', []) + visited_places

    # Sesuaikan waktu mulai dengan waktu saat ini
    new_preferences['start_time'] = current_time.strftime('%H:%M')

    # Sesuaikan lokasi mulai dengan posisi saat ini
    current_place_id = current_route[current_position]
    current_place = df_places.iloc[current_place_id - 1]
    new_preferences['start_location'] = {
        'name': current_place['name'],
        'latitude': current_place['latitude'],
        'longitude': current_place['longitude']
    }

    # Perbarui budget yang tersisa
    used_budget = sum(df_places.iloc[place_id - 1]['entrance_fee'] for place_id in visited_places)
    new_preferences['budget'] = preferences['budget'] - used_budget

    # Perbarui jumlah tempat maksimal
    new_preferences['max_places'] = preferences['max_places'] - len(visited_places)

    # Reset creator untuk algoritma genetika
    if 'FitnessMax' in dir(creator):
        del creator.FitnessMax
        del creator.Individual

    # Optimasi rute baru
    results = optimize_route(df_places, new_preferences, distance_matrix,
                             travel_time_matrix, dynamic_data)

    # Gabungkan rute yang sudah dikunjungi dengan rute baru
    results['best_route'] = visited_places + results['best_route']

    # Tambahkan data dinamis ke hasil
    results['dynamic_data'] = dynamic_data

    return results

# 8. Membuat jadwal dari rute optimal
def create_schedule(route, df_places, preferences, distance_matrix, travel_time_matrix, dynamic_data):
    """Buat jadwal berdasarkan rute yang diberikan"""
    schedule = []

    # Waktu awal
    start_time = datetime.strptime(preferences['start_time'], '%H:%M')
    current_time = start_time
    lunch_time = datetime.strptime(preferences['lunch_time'], '%H:%M')
    lunch_taken = False

    # Tambahkan keberangkatan
    schedule.append({
        'location': preferences['start_location']['name'],
        'activity': 'Berangkat dari hotel',
        'time': current_time.strftime('%H:%M')
    })

    # Hitung jarak ke tempat pertama
    if route:
        start_loc = (preferences['start_location']['latitude'], preferences['start_location']['longitude'])
        first_loc = (df_places.iloc[route[0]-1]['latitude'], df_places.iloc[route[0]-1]['longitude'])
        distance_to_first = geodist.distance(start_loc, first_loc).km
        travel_time = (distance_to_first / 40) * 60  # Menit

        # Sesuaikan dengan lalu lintas
        traffic_factor = dynamic_data['traffic_by_hour'].get(current_time.hour, 1.0)
        current_time += timedelta(minutes=travel_time * traffic_factor)

        schedule.append({
            'location': f"Perjalanan ke {df_places.iloc[route[0]-1]['name']}",
            'activity': f"Perjalanan ({distance_to_first:.1f} km)",
            'time': current_time.strftime('%H:%M')
        })

    # Kunjungi setiap tempat
    for i, place_id in enumerate(route):
        place_idx = place_id - 1
        place = df_places.iloc[place_idx]

        # Tambah waktu tempuh antar tempat
        if i > 0:
            prev_idx = route[i-1] - 1
            distance = distance_matrix[prev_idx][place_idx]
            travel_time = travel_time_matrix[prev_idx][place_idx]

            traffic_factor = dynamic_data['traffic_by_hour'].get(current_time.hour, 1.0)
            current_time += timedelta(minutes=travel_time * traffic_factor)

            schedule.append({
                'location': f"Perjalanan ke {place['name']}",
                'activity': f"Perjalanan ({distance:.1f} km)",
                'time': current_time.strftime('%H:%M')
            })

        # Cek makan siang
        if not lunch_taken and current_time >= lunch_time:
            schedule.append({
                'location': f"Makan Siang (di sekitar {place['name']})",
                'activity': "Makan Siang",
                'time': current_time.strftime('%H:%M')
            })

            current_time += timedelta(minutes=preferences['lunch_duration'])
            lunch_taken = True

            schedule.append({
                'location': "Selesai Makan Siang",
                'activity': "Lanjut Wisata",
                'time': current_time.strftime('%H:%M')
            })

        # Cek jam buka
        place_open = datetime.strptime(place['open_time'], '%H:%M').time()
        if current_time.time() < place_open:
            schedule.append({
                'location': f"{place['name']}",
                'activity': f"Menunggu tempat buka",
                'time': current_time.strftime('%H:%M')
            })

            current_time = datetime.combine(current_time.date(), place_open)

        # Mulai kunjungan
        schedule.append({
            'location': f"{place['name']}",
            'activity': "Mulai kunjungan",
            'time': current_time.strftime('%H:%M')
        })

        # Durasi kunjungan
        visit_time = place['visit_duration_min'] * dynamic_data['crowdedness_factor'] * place['crowdedness_factor']
        current_time += timedelta(minutes=visit_time)

        schedule.append({
            'location': f"{place['name']}",
            'activity': f"Selesai kunjungan (Durasi: {visit_time:.0f} menit)",
            'time': current_time.strftime('%H:%M')
        })

    # Kembali ke hotel
    if route:
        last_loc = (df_places.iloc[route[-1]-1]['latitude'], df_places.iloc[route[-1]-1]['longitude'])
        end_loc = (preferences['end_location']['latitude'], preferences['end_location']['longitude'])
        distance_to_hotel = geodist.distance(last_loc, end_loc).km
        travel_time = (distance_to_hotel / 40) * 60  # Menit

        traffic_factor = dynamic_data['traffic_by_hour'].get(current_time.hour, 1.0)
        current_time += timedelta(minutes=travel_time * traffic_factor)

        schedule.append({
            'location': f"Perjalanan kembali ke {preferences['end_location']['name']}",
            'activity': f"Perjalanan ({distance_to_hotel:.1f} km)",
            'time': current_time.strftime('%H:%M')
        })

        schedule.append({
            'location': preferences['end_location']['name'],
            'activity': "Tiba di hotel - Akhir perjalanan",
            'time': current_time.strftime('%H:%M')
        })

    return pd.DataFrame(schedule)

# 9. Visualisasi rute pada peta
def plot_route_on_map(route, df_places, preferences):
    """Visualisasi rute pada peta menggunakan folium"""
    # Inisialisasi peta
    center_lat = df_places['latitude'].mean()
    center_lon = df_places['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # Tambahkan marker hotel
    start_loc = preferences['start_location']
    folium.Marker(
        location=[start_loc['latitude'], start_loc['longitude']],
        popup=f"Start/End: {start_loc['name']}",
        tooltip=start_loc['name'],
        icon=folium.Icon(color='green', icon='home')
    ).add_to(m)

    # Tambahkan marker tempat wisata
    for i, place_id in enumerate(route):
        place = df_places.iloc[place_id-1]

        # Pilih warna berdasarkan kategori
        color = 'red' if place_id in preferences['must_visit'] else 'blue'

        folium.Marker(
            location=[place['latitude'], place['longitude']],
            popup=f"{i+1}. {place['name']} - {place['category']}",
            tooltip=place['name'],
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

    # Tambahkan garis rute
    route_points = []
    # Dari hotel
    route_points.append([start_loc['latitude'], start_loc['longitude']])

    # Tempat wisata
    for place_id in route:
        place = df_places.iloc[place_id-1]
        route_points.append([place['latitude'], place['longitude']])

    # Kembali ke hotel
    route_points.append([start_loc['latitude'], start_loc['longitude']])

    folium.PolyLine(
        route_points,
        color='green',
        weight=2.5,
        opacity=1
    ).add_to(m)

    return m

# 10. Fungsi utama
def main():
    # Import di dalam fungsi juga untuk memastikan availability
    # try:
    #     from IPython.display import display as ipython_display
    # except ImportError:
    #     # Jika tidak bisa import, buat fungsi display sederhana
    #     def ipython_display(obj):
    #         print(obj)

    # Buat data
    df_places = create_tourism_data()
    preferences = create_user_preferences()
    distance_matrix = create_distance_matrix(df_places)
    travel_time_matrix = create_travel_time_matrix(distance_matrix)

    # Tanyakan mode yang diinginkan
    print("Pilih mode:")
    print("1. Optimasi rute standar (tanpa pembaruan real-time)")
    print("2. Simulasi perjalanan interaktif (dengan pembaruan real-time)")

    mode = input("Mode yang dipilih: ")

    if mode == '2':
        # Mode interaktif dengan pembaruan real-time
        journey_results = interactive_journey(
            df_places, preferences, distance_matrix, travel_time_matrix
        )
        return journey_results
    else:
        # Mode standar (sesuai kode original)
        print("Mengoptimasi rute wisata...")

        # Reset creator sebelum membuat ulang (untuk mengatasi konflik definisi fitness)
        if 'FitnessMax' in dir(creator):
            del creator.FitnessMax
            del creator.Individual

        dynamic_data = create_dynamic_data()
        results = optimize_route(df_places, preferences, distance_matrix, travel_time_matrix, dynamic_data)

        print(f"Rute optimal: {[df_places.iloc[id - 1]['name'] for id in results['best_route']]}")
        print(f"Fitness score: {results['best_fitness']:.2f}")

        # Total biaya
        total_cost = sum(df_places.iloc[id - 1]['entrance_fee'] for id in results['best_route'])
        print(f"Total biaya: Rp{total_cost}")

        # Tampilkan jadwal
        print("\nJadwal perjalanan:")
        print(results['schedule'])

        # Buat peta dan tampilkan
        print("\nPeta Rute Wisata:")
        route_map = plot_route_on_map(results['best_route'], df_places, preferences)

        # Simpan peta ke file HTML
        map_file = 'yogyakarta_tour_route.html'
        route_map.save(map_file)
        print(f"Peta disimpan ke file: {map_file}")

        # Tampilkan peta di notebook jika IPython tersedia
        try:
            print('lalal')
            # ipython_display(route_map)
        except:
            print("Tidak dapat menampilkan peta di notebook.")

        return results


def interactive_journey(df_places, initial_preferences, distance_matrix, travel_time_matrix):
    """
    Simulasi perjalanan interaktif dengan pembaruan data real-time
    """
    # Optimasi rute awal
    dynamic_data = create_dynamic_data()
    initial_results = optimize_route(df_places, initial_preferences,
                                     distance_matrix, travel_time_matrix, dynamic_data)

    current_route = initial_results['best_route']
    current_schedule = initial_results['schedule']

    print("\n=== RENCANA PERJALANAN AWAL ===")
    print(f"Rute: {[df_places.iloc[id - 1]['name'] for id in current_route]}")
    print("\nJadwal:")
    print(current_schedule)

    # Plot rute awal
    route_map = plot_route_on_map(current_route, df_places, initial_preferences)
    route_map.save('initial_route.html')
    print("Peta rute awal disimpan sebagai 'initial_route.html'")

    # Mulai simulasi perjalanan
    current_position = 0
    print("\n=== SIMULASI PERJALANAN REAL-TIME ===")

    while current_position < len(current_route):
        # Tampilkan informasi posisi saat ini
        current_place_id = current_route[current_position]
        current_place = df_places.iloc[current_place_id - 1]

        print(f"\nAnda berada di: {current_place['name']}")

        # Dapatkan waktu dari jadwal
        current_time_str = current_schedule.iloc[current_position * 2 + 1]['time']
        current_time = datetime.strptime(current_time_str, '%H:%M')

        print(f"Waktu saat ini: {current_time_str}")

        # Menu interaktif
        print("\nOpsi:")
        print("1. Lanjutkan ke tempat berikutnya")
        print("2. Perbarui data real-time dan optimasi ulang rute")
        print("3. Lihat jadwal saat ini")
        print("4. Lihat rute saat ini")
        print("5. Akhiri perjalanan")

        choice = input("Pilihan Anda: ")

        if choice == '1':
            # Lanjut ke tempat berikutnya
            if current_position < len(current_route) - 1:
                current_position += 1
            else:
                print("Anda telah menyelesaikan semua tempat dalam rute!")
                break

        elif choice == '2':
            # Perbarui data real-time dan optimasi ulang
            print("\nMemperbarui data real-time dan mengoptimasi ulang rute...")

            # Perbarui waktu untuk simulasi - misalnya tambah 1 jam
            updated_time = current_time + timedelta(hours=1)
            print(f"Waktu diperbarui ke: {updated_time.strftime('%H:%M')}")

            # Reoptimasi
            new_results = reoptimize_route(
                current_route, current_position, df_places,
                initial_preferences, distance_matrix, travel_time_matrix, updated_time
            )

            # Perbarui rute dan jadwal
            current_route = new_results['best_route']
            current_schedule = new_results['schedule']
            dynamic_data = new_results['dynamic_data']

            # Tampilkan informasi terbaru
            print("\n=== DATA DINAMIS TERBARU ===")
            print(f"Cuaca: {dynamic_data['weather_condition']}")
            print(f"Faktor keramaian: {dynamic_data['crowdedness_factor']:.2f}")
            if dynamic_data['closed_places']:
                closed_names = [df_places.iloc[id - 1]['name'] for id in dynamic_data['closed_places']]
                print(f"Tempat yang tutup: {', '.join(closed_names)}")

            print("\n=== RUTE YANG DIPERBARUI ===")
            print(f"Rute: {[df_places.iloc[id - 1]['name'] for id in current_route]}")

            # Plot rute baru
            route_map = plot_route_on_map(current_route, df_places, initial_preferences)
            route_map.save('updated_route.html')
            print("Peta rute baru disimpan sebagai 'updated_route.html'")

        elif choice == '3':
            # Tampilkan jadwal
            print("\n=== JADWAL SAAT INI ===")
            print(current_schedule)

        elif choice == '4':
            # Tampilkan rute
            print("\n=== RUTE SAAT INI ===")
            remaining_route = current_route[current_position:]
            print(f"Tempat yang tersisa: {[df_places.iloc[id - 1]['name'] for id in remaining_route]}")

        elif choice == '5':
            # Akhiri perjalanan
            print("\nMengakhiri perjalanan...")
            break

        else:
            print("Pilihan tidak valid. Silakan pilih lagi.")

    print("\n=== PERJALANAN SELESAI ===")
    total_visited = current_position + 1
    print(f"Total tempat yang dikunjungi: {total_visited}/{len(initial_results['best_route'])}")

    return {
        'initial_route': initial_results['best_route'],
        'final_route': current_route,
        'visited_places': current_route[:total_visited]
    }


if __name__ == "__main__":
    main()