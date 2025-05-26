import numpy as np
import pandas as pd
import math
import folium
import random
from datetime import datetime, timedelta
import geopy.distance as geodist
import networkx as nx
from deap import base, creator, tools, algorithms
import io
import base64
import requests
import time

class TourismOptimizer:
    def __init__(self):
        self.df_places = self.create_tourism_data()
        self.distance_matrix = self.create_distance_matrix(self.df_places)
        self.travel_time_matrix = self.create_travel_time_matrix(self.distance_matrix)
        self.current_route = []
        self.current_position = 0
        self.current_schedule = None
        self.preferences = None
        self.dynamic_data = None


    def create_tourism_data(self):
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
                50000, 50000, 15000, 15000,
                15000, 10000, 35000, 10000,
                25000, 30000, 20000, 15000,
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
    
    def create_user_preferences(self, preferences_data=None):
        # Default preferences
        default_preferences = {
            'start_time': '08:00',
            'end_time': '20:00',
            'max_places': 6,
            'budget': 200000,
            'preferred_categories': ['Budaya', 'Alam'],
            'must_visit': [1, 2],
            'avoid_places': [],
            'lunch_time': '12:00',
            'lunch_duration': 60,
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
        
        # If no custom preferences provided, return defaults
        if not preferences_data:
            return default_preferences
        
        # Merge custom preferences with defaults
        merged_preferences = default_preferences.copy()
        
        # Update basic preferences
        for key in ['start_time', 'end_time', 'max_places', 'budget', 
                   'preferred_categories', 'must_visit', 'avoid_places', 
                   'lunch_time', 'lunch_duration']:
            if key in preferences_data:
                merged_preferences[key] = preferences_data[key]
        
        # Handle start_location
        if 'start_location' in preferences_data:
            start_loc = preferences_data['start_location']
            
            # Validate required fields
            if all(key in start_loc for key in ['name', 'latitude', 'longitude']):
                merged_preferences['start_location'] = {
                    'name': str(start_loc['name']),
                    'latitude': float(start_loc['latitude']),
                    'longitude': float(start_loc['longitude'])
                }
            else:
                raise ValueError("start_location must include 'name', 'latitude', and 'longitude'")
        
        # Handle end_location
        if 'end_location' in preferences_data:
            end_loc = preferences_data['end_location']
            
            # Validate required fields
            if all(key in end_loc for key in ['name', 'latitude', 'longitude']):
                merged_preferences['end_location'] = {
                    'name': str(end_loc['name']),
                    'latitude': float(end_loc['latitude']),
                    'longitude': float(end_loc['longitude'])
                }
            else:
                raise ValueError("end_location must include 'name', 'latitude', and 'longitude'")
        
        # If only start_location provided, use it as end_location too (round trip)
        if 'start_location' in preferences_data and 'end_location' not in preferences_data:
            merged_preferences['end_location'] = merged_preferences['start_location'].copy()
        
        return merged_preferences
    
    def create_dynamic_data(self):
        traffic_by_hour = {hour: 1.5 if (7 <= hour <= 9 or 16 <= hour <= 19) else
                                1.2 if 10 <= hour <= 15 else 1.0
                           for hour in range(24)}

        dynamic_data = {
            'traffic_by_hour': traffic_by_hour,
            'weather_condition': "Cerah",
            'is_weekend': True,
            'crowdedness_factor': 1.5,
            'closed_places': []
        }
        return dynamic_data
    
    def update_dynamic_data(self, current_time, old_dynamic_data=None):
        if old_dynamic_data is None:
            old_dynamic_data = self.create_dynamic_data()

        dynamic_data = old_dynamic_data.copy()
        hour = current_time.hour

        # Simulasi perubahan cuaca
        if 6 <= hour < 11:
            weather = "Cerah"
        elif 11 <= hour < 15:
            weather = "Panas" if random.random() < 0.7 else "Berawan"
        elif 15 <= hour < 18:
            weather = "Berawan" if random.random() < 0.6 else "Hujan Ringan"
        else:
            weather = "Cerah Berawan"

        dynamic_data['weather_condition'] = weather

        # Update crowd factor
        crowd_multiplier = 1.0
        if weather == "Hujan Ringan" or weather == "Hujan":
            crowd_multiplier = 0.7
        elif weather == "Panas":
            crowd_multiplier = 0.9

        is_weekend = old_dynamic_data.get('is_weekend', True)
        base_crowd = 1.5 if is_weekend else 1.0

        if 10 <= hour <= 14:
            time_multiplier = 1.3
        else:
            time_multiplier = 1.0

        dynamic_data['crowdedness_factor'] = base_crowd * crowd_multiplier * time_multiplier

        # Update traffic
        traffic_multiplier = 1.0
        if weather == "Hujan Ringan":
            traffic_multiplier = 1.3
        elif weather == "Hujan":
            traffic_multiplier = 1.5

        traffic_by_hour = old_dynamic_data.get('traffic_by_hour', {}).copy()
        base_traffic = traffic_by_hour.get(hour, 1.0)
        traffic_by_hour[hour] = base_traffic * traffic_multiplier
        dynamic_data['traffic_by_hour'] = traffic_by_hour

        # Update closed places
        closed_places = []
        if weather == "Hujan" and random.random() < 0.3:
            outdoor_places = [6, 7, 8, 13, 14]
            closed_places = random.sample(outdoor_places, 1)

        dynamic_data['closed_places'] = closed_places
        return dynamic_data
    
    def create_distance_matrix(self, df):
        n = len(df)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    point1 = (df.iloc[i]['latitude'], df.iloc[i]['longitude'])
                    point2 = (df.iloc[j]['latitude'], df.iloc[j]['longitude'])
                    distance_matrix[i][j] = geodist.distance(point1, point2).km

        return distance_matrix
    
    def create_travel_time_matrix(self, distance_matrix, traffic_factor=1.2):
        return (distance_matrix / 40) * 60 * traffic_factor
    
    # Tambahkan di dalam class TourismOptimizer
    def convert_to_json_serializable(self, obj):
            """Convert numpy/pandas types to JSON serializable types"""
            import numpy as np
            import pandas as pd
            
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Series):
                return obj.tolist()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict('records')
            elif isinstance(obj, dict):
                return {key: self.convert_to_json_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [self.convert_to_json_serializable(item) for item in obj]
            else:
                return obj

    def optimize_route(self, preferences_data=None, verbose=True):
        self.preferences = self.create_user_preferences(preferences_data)
        self.dynamic_data = self.create_dynamic_data()
        
        # Reset DEAP creators
        if 'FitnessMax' in dir(creator):
            del creator.FitnessMax
            del creator.Individual

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        def init_individual():
            individual = self.preferences['must_visit'].copy()
            potential_places = [i for i in range(1, len(self.df_places)+1)
                               if i not in individual and i not in self.preferences['avoid_places']]

            random.shuffle(potential_places)
            current_budget = sum(self.df_places.iloc[p-1]['entrance_fee'] for p in individual)

            for place_id in potential_places:
                if len(individual) >= self.preferences['max_places']:
                    break

                fee = self.df_places.iloc[place_id-1]['entrance_fee']
                if current_budget + fee <= self.preferences['budget']:
                    individual.append(place_id)
                    current_budget += fee

            random.shuffle(individual)
            return individual

        toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        
        def eval_wrapper(route):
            return self.eval_route_fixed(route, self.df_places, self.preferences, 
                                    self.distance_matrix, self.travel_time_matrix, self.dynamic_data)
        
        toolbox.register("evaluate", eval_wrapper)
        
        # Custom crossover
        def custom_cx(ind1, ind2):
            if not ind1 or not ind2:
                return ind1, ind2
            
            if len(ind1) > 1 and len(ind2) > 1:
                # Simple one-point crossover with validation
                cx_point1 = random.randint(0, len(ind1)-1)
                cx_point2 = random.randint(0, len(ind2)-1)

                # Create offspring
                offspring1 = ind1[:cx_point1] + [x for x in ind2 if x not in ind1[:cx_point1]]
                offspring2 = ind2[:cx_point2] + [x for x in ind1 if x not in ind2[:cx_point2]]

                # Ensure must_visit places are included
                for must_visit_id in self.preferences['must_visit']:
                    if must_visit_id not in offspring1:
                        offspring1.append(must_visit_id)
                    if must_visit_id not in offspring2:
                        offspring2.append(must_visit_id)

                # Limit places and budget
                while len(offspring1) > self.preferences['max_places']:
                    optional = [p for p in offspring1 if p not in self.preferences['must_visit']]
                    if optional:
                        offspring1.remove(random.choice(optional))
                    else:
                        break

                while len(offspring2) > self.preferences['max_places']:
                    optional = [p for p in offspring2 if p not in self.preferences['must_visit']]
                    if optional:
                        offspring2.remove(random.choice(optional))
                    else:
                        break

                # Budget constraints
                def enforce_budget(offspring):
                    budget = sum(self.df_places.iloc[p-1]['entrance_fee'] for p in offspring)
                    while budget > self.preferences['budget'] and len(offspring) > len(self.preferences['must_visit']):
                        optional = [p for p in offspring if p not in self.preferences['must_visit']]
                        if optional:
                            to_remove = max(optional, key=lambda p: self.df_places.iloc[p-1]['entrance_fee'])
                            offspring.remove(to_remove)
                            budget -= self.df_places.iloc[to_remove-1]['entrance_fee']
                        else:
                            break

                enforce_budget(offspring1)
                enforce_budget(offspring2)

                random.shuffle(offspring1)
                random.shuffle(offspring2)

                ind1[:] = offspring1
                ind2[:] = offspring2

            return ind1, ind2
        
        # Custom mutation
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
            if random.random() < indpb * 1.5:
                current_budget = sum(self.df_places.iloc[p-1]['entrance_fee'] for p in individual)

                # Add place if possible
                if len(individual) < self.preferences['max_places']:
                    available_places = [i for i in range(1, len(self.df_places)+1)
                                       if i not in individual and i not in self.preferences['avoid_places']]
                    if available_places:
                        new_place = random.choice(available_places)
                        fee = self.df_places.iloc[new_place-1]['entrance_fee']
                        if current_budget + fee <= self.preferences['budget']:
                            individual.append(new_place)

                # Remove optional place
                if random.random() < indpb and len(individual) > 1:
                    optional_places = [p for p in individual if p not in self.preferences['must_visit']]
                    if optional_places:
                        individual.remove(random.choice(optional_places))

            return individual,

        toolbox.register("mate", custom_cx)
        toolbox.register("mutate", custom_mutate, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # Setup statistics
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        stats.register("min", np.min)
        stats.register("std", np.std)

        # Run genetic algorithm dengan verbose output
        print("\n" + "="*60)
        print("🧬 GENETIC ALGORITHM EVOLUTION")
        print("="*60)
        print(f"Population Size: {50}")
        print(f"Generations: {50}")
        print(f"Crossover Rate: {70}%")
        print(f"Mutation Rate: {30}%")
        print("="*60)

        # Run genetic algorithm
        pop = toolbox.population(n=50)
        hof = tools.HallOfFame(1)
        
        pop, logbook = algorithms.eaSimple(
            pop, toolbox, cxpb=0.7, mutpb=0.3,
            ngen=50, stats=stats, halloffame=hof, 
            verbose=verbose   # ← Enable verbose output
        )

        self.current_route = list(hof[0])
        self.current_position = 0
        self.current_schedule = self.create_schedule()

        # Extract evolution data
        gen = logbook.select("gen")
        fit_avg = logbook.select("avg") 
        fit_max = logbook.select("max")
        fit_min = logbook.select("min")
        fit_std = logbook.select("std")

        result = {
            'route': [int(x) for x in self.current_route],
            'fitness': float(hof[0].fitness.values[0]),
            'schedule': self.current_schedule.to_dict('records'),
            'total_cost': int(sum(self.df_places.iloc[id-1]['entrance_fee'] for id in self.current_route)),
            'evolution_stats': {
                'generations': len(gen),
                'final_avg_fitness': float(fit_avg[-1]),
                'final_max_fitness': float(fit_max[-1]),
                'final_min_fitness': float(fit_min[-1]),
                'improvement': float(fit_max[-1] - fit_max[0]),
                'fitness_history': {
                    'generation': [int(x) for x in gen],
                    'avg_fitness': [float(x) for x in fit_avg],
                    'max_fitness': [float(x) for x in fit_max],
                    'min_fitness': [float(x) for x in fit_min],
                    'std_fitness': [float(x) for x in fit_std]
                }
            }
        }
    
        return self.convert_to_json_serializable(result)
    def create_schedule(self):
        if not self.current_route or not self.preferences:
            return pd.DataFrame()
        
        schedule = []
        start_time = datetime.strptime(self.preferences['start_time'], '%H:%M')
        current_time = start_time
        lunch_time = datetime.strptime(self.preferences['lunch_time'], '%H:%M')
        lunch_taken = False

        schedule.append({
            'location': self.preferences['start_location']['name'],
            'activity': 'Berangkat dari hotel',
            'time': current_time.strftime('%H:%M'),
            'type': 'departure'
        })

        for i, place_id in enumerate(self.current_route):
            place = self.df_places.iloc[place_id-1]

            # Travel time calculation
            if i == 0:
                start_loc = (self.preferences['start_location']['latitude'], 
                           self.preferences['start_location']['longitude'])
                place_loc = (place['latitude'], place['longitude'])
                distance = geodist.distance(start_loc, place_loc).km
            else:
                prev_place = self.df_places.iloc[self.current_route[i-1]-1]
                distance = self.distance_matrix[self.current_route[i-1]-1][place_id-1]

            travel_time = (distance / 40) * 60
            traffic_factor = self.dynamic_data['traffic_by_hour'].get(current_time.hour, 1.0)
            current_time += timedelta(minutes=travel_time * traffic_factor)

            if i > 0:
                schedule.append({
                    'location': f"Perjalanan ke {place['name']}",
                    'activity': f"Perjalanan ({distance:.1f} km)",
                    'time': current_time.strftime('%H:%M'),
                    'type': 'travel'
                })

            # Lunch check
            if not lunch_taken and current_time >= lunch_time:
                schedule.append({
                    'location': f"Makan Siang (di sekitar {place['name']})",
                    'activity': "Makan Siang",
                    'time': current_time.strftime('%H:%M'),
                    'type': 'lunch'
                })
                current_time += timedelta(minutes=self.preferences['lunch_duration'])
                lunch_taken = True

            # Visit
            place_open = datetime.strptime(place['open_time'], '%H:%M').time()
            if current_time.time() < place_open:
                current_time = datetime.combine(current_time.date(), place_open)

            schedule.append({
                'location': place['name'],
                'activity': f"Kunjungan ke {place['name']}",
                'time': current_time.strftime('%H:%M'),
                'type': 'visit',
                'place_id': place_id,
                'category': place['category'],
                'entrance_fee': place['entrance_fee']
            })

            visit_time = place['visit_duration_min'] * self.dynamic_data['crowdedness_factor'] * place['crowdedness_factor']
            current_time += timedelta(minutes=visit_time)

        # Return to hotel
        if self.current_route:
            last_place = self.df_places.iloc[self.current_route[-1]-1]
            end_loc = (self.preferences['end_location']['latitude'], 
                      self.preferences['end_location']['longitude'])
            last_loc = (last_place['latitude'], last_place['longitude'])
            distance = geodist.distance(last_loc, end_loc).km
            travel_time = (distance / 40) * 60
            current_time += timedelta(minutes=travel_time)

            schedule.append({
                'location': self.preferences['end_location']['name'],
                'activity': 'Kembali ke hotel',
                'time': current_time.strftime('%H:%M'),
                'type': 'return'
            })

        return pd.DataFrame(schedule)
    
    def get_next_place(self):
        """Menu 1: Lanjutkan ke tempat berikutnya"""
        if self.current_position < len(self.current_route) - 1:
            self.current_position += 1
            current_place_id = self.current_route[self.current_position]
            current_place = self.df_places.iloc[current_place_id - 1]
            
            result = {
                'success': True,
                'current_position': self.current_position,
                'current_place': {
                    'id': current_place_id,
                    'name': current_place['name'],
                    'category': current_place['category'],
                    'latitude': current_place['latitude'],
                    'longitude': current_place['longitude'],
                    'entrance_fee': current_place['entrance_fee'],
                    'open_time': current_place['open_time'],
                    'close_time': current_place['close_time']
                },
                'message': f"Berhasil pindah ke: {current_place['name']}"
            }
            
            # Convert to JSON serializable
            return self.convert_to_json_serializable(result)
        else:
            return {
                'success': False,
                'message': "Anda sudah berada di tempat terakhir dalam rute!"
            }
    
    def reoptimize_route(self, current_time_str=None):
        """Menu 2: Perbarui data real-time dan optimasi ulang rute"""
        if current_time_str:
            current_time = datetime.strptime(current_time_str, '%H:%M')
        else:
            current_time = datetime.now()
        
        # Update dynamic data
        self.dynamic_data = self.update_dynamic_data(current_time, self.dynamic_data)
        
        # Get remaining places
        remaining_places = self.current_route[self.current_position + 1:]
        visited_places = self.current_route[:self.current_position + 1]
        
        # Update preferences for reoptimization
        new_preferences = self.preferences.copy()
        new_preferences['start_time'] = current_time.strftime('%H:%M')
        new_preferences['avoid_places'] = self.preferences.get('avoid_places', []) + visited_places
        new_preferences['must_visit'] = []
        
        # Update start location to current place
        if self.current_position < len(self.current_route):
            current_place_id = self.current_route[self.current_position]
            current_place = self.df_places.iloc[current_place_id - 1]
            new_preferences['start_location'] = {
                'name': current_place['name'],
                'latitude': current_place['latitude'],
                'longitude': current_place['longitude']
            }
        
        # Update budget
        used_budget = sum(self.df_places.iloc[place_id - 1]['entrance_fee'] for place_id in visited_places)
        new_preferences['budget'] = self.preferences['budget'] - used_budget
        new_preferences['max_places'] = self.preferences['max_places'] - len(visited_places)
        
        # Reoptimize if there are still places to visit
        if new_preferences['max_places'] > 0 and new_preferences['budget'] > 0:
            # Reset DEAP creators
            if 'FitnessMax' in dir(creator):
                del creator.FitnessMax
                del creator.Individual
                
            result = self.optimize_route(new_preferences)
            
            # Combine with visited places
            self.current_route = visited_places + result['route']
            self.current_schedule = self.create_schedule()
        
        result = {
            'success': True,
            'dynamic_data': {
                'weather': self.dynamic_data['weather_condition'],
                'crowdedness_factor': self.dynamic_data['crowdedness_factor'],
                'closed_places': [self.df_places.iloc[id-1]['name'] for id in self.dynamic_data['closed_places']]
            },
            'updated_route': [self.df_places.iloc[id-1]['name'] for id in self.current_route],
            'schedule': self.current_schedule.to_dict('records'),
            'message': "Rute berhasil dioptimasi ulang"
        }

        return self.convert_to_json_serializable(result)
    
    def get_current_schedule(self):
        """Menu 3: Lihat jadwal saat ini"""
        if self.current_schedule is not None:
            result = {
                'success': True,
                'schedule': self.current_schedule.to_dict('records'),
                'total_activities': len(self.current_schedule)
            }
        else:
            result = {
                'success': False,
                'message': "Jadwal belum tersedia. Silakan optimasi rute terlebih dahulu."
            }

        return self.convert_to_json_serializable(result)
    
    def get_current_route(self):
        """Menu 4: Lihat rute saat ini"""
        if self.current_route:
            remaining_route = self.current_route[self.current_position + 1:]
            visited_route = self.current_route[:self.current_position + 1] if self.current_position >= 0 else []
            
            # Calculate costs
            total_cost = sum(self.df_places.iloc[place_id-1]['entrance_fee'] for place_id in self.current_route)
            visited_cost = sum(self.df_places.iloc[place_id-1]['entrance_fee'] for place_id in visited_route)
            remaining_cost = total_cost - visited_cost
            
            result = {
                'success': True,
                'current_position': self.current_position,
                'visited_places': [
                    {
                        'id': place_id,
                        'name': self.df_places.iloc[place_id-1]['name'],
                        'category': self.df_places.iloc[place_id-1]['category'],
                        'cost': self.df_places.iloc[place_id-1]['entrance_fee']
                    } for place_id in visited_route
                ],
                'remaining_places': [
                    {
                        'id': place_id,
                        'name': self.df_places.iloc[place_id-1]['name'],
                        'category': self.df_places.iloc[place_id-1]['category'],
                        'cost': self.df_places.iloc[place_id-1]['entrance_fee']
                    } for place_id in remaining_route
                ],
                'total_places': len(self.current_route),
                'costs': {
                    'total_cost': total_cost,
                    'visited_cost': visited_cost,
                    'remaining_cost': remaining_cost
                },
                'progress_percentage': ((self.current_position + 1) / len(self.current_route)) * 100
            }
        else:
            result = {
                'success': False,
                'message': "Rute belum tersedia. Silakan optimasi rute terlebih dahulu."
            }
        
        return self.convert_to_json_serializable(result)
    
    def end_journey(self):
        """Menu 5: Akhiri perjalanan"""
        total_visited = self.current_position + 1 if self.current_position >= 0 else 0
        total_cost = sum(self.df_places.iloc[place_id-1]['entrance_fee'] 
                        for place_id in self.current_route[:total_visited])
        
        # Calculate statistics
        categories_visited = {}
        for place_id in self.current_route[:total_visited]:
            category = self.df_places.iloc[place_id-1]['category']
            categories_visited[category] = categories_visited.get(category, 0) + 1
        
        journey_summary = {
            'success': True,
            'message': "Perjalanan berhasil diakhiri",
            'summary': {
                'total_places_planned': len(self.current_route),
                'total_places_visited': total_visited,
                'completion_percentage': (total_visited / len(self.current_route)) * 100 if self.current_route else 0,
                'total_cost': total_cost,
                'categories_visited': categories_visited,
                'visited_places': [
                    {
                        'id': place_id,
                        'name': self.df_places.iloc[place_id-1]['name'],
                        'category': self.df_places.iloc[place_id-1]['category'],
                        'cost': self.df_places.iloc[place_id-1]['entrance_fee']
                    } for place_id in self.current_route[:total_visited]
                ]
            }
        }
        
        # Reset state
        self.current_route = []
        self.current_position = 0
        self.current_schedule = None
        
        return self.convert_to_json_serializable(journey_summary)
    
    def eval_route_fixed(self, route, df_places, preferences, distance_matrix, time_matrix, dynamic_data):
        """Fitness function yang diperbaiki - selalu menghasilkan nilai positif"""
        
        if not route:
            return (1.0,)

        # KOMPONEN POSITIF (0-1 scale)
        place_count_score = len(route) / preferences['max_places']
        
        # Distance score
        total_distance = 0
        if route:
            start_loc = (preferences['start_location']['latitude'], preferences['start_location']['longitude'])
            first_loc = (df_places.iloc[route[0]-1]['latitude'], df_places.iloc[route[0]-1]['longitude'])
            total_distance += geodist.distance(start_loc, first_loc).km

        for i in range(len(route)-1):
            idx1, idx2 = route[i]-1, route[i+1]-1
            # ✅ KONVERSI numpy types ke Python types
            distance = float(distance_matrix[idx1][idx2])
            total_distance += distance

        if route:
            end_loc = (preferences['end_location']['latitude'], preferences['end_location']['longitude'])
            last_loc = (df_places.iloc[route[-1]-1]['latitude'], df_places.iloc[route[-1]-1]['longitude'])
            total_distance += geodist.distance(last_loc, end_loc).km

        distance_score = max(0, 1 - (total_distance / 200))
        
        # Category score
        category_matches = sum(1 for place_id in route 
                            if df_places.iloc[place_id-1]['category'] in preferences['preferred_categories'])
        category_score = category_matches / len(route) if route else 0
        
        # Popularity score
        popularity_score = sum(df_places.iloc[place_id-1]['popularity'] for place_id in route)
        popularity_score = (popularity_score / len(route)) / 10.0 if route else 0

        # BASE FITNESS (0-100)
        base_fitness = (
            0.40 * place_count_score +
            0.15 * distance_score +
            0.20 * category_score +
            0.25 * popularity_score
        ) * 100

        # PENALTY SYSTEM (Multiplicative)
        penalty_multiplier = 1.0

        # Budget penalty
        budget_used = sum(df_places.iloc[place_id-1]['entrance_fee'] for place_id in route)
        if budget_used > preferences['budget']:
            budget_ratio = preferences['budget'] / budget_used
            penalty_multiplier *= max(0.5, budget_ratio)

        # Must visit penalty
        must_visit_count = len(preferences['must_visit'])
        if must_visit_count > 0:
            visited_must = sum(1 for place_id in preferences['must_visit'] if place_id in route)
            must_visit_ratio = visited_must / must_visit_count
            penalty_multiplier *= (0.3 + 0.7 * must_visit_ratio)

        # Time feasibility penalty
        time_feasible = self.check_time_feasibility_simple(route, df_places, preferences, time_matrix, dynamic_data)
        if not time_feasible:
            penalty_multiplier *= 0.7

        # FINAL FITNESS (Selalu positif: 1-100)
        final_fitness = base_fitness * penalty_multiplier
        
        # ✅ KONVERSI hasil ke Python float
        return (max(1.0, float(final_fitness)),)
    
    def check_time_feasibility_simple(self, route, df_places, preferences, time_matrix, dynamic_data):
        """Simplified time feasibility check"""
        start_time = datetime.strptime(preferences['start_time'], '%H:%M')
        current_time = start_time
        end_time = datetime.strptime(preferences['end_time'], '%H:%M')
        
        for i, place_id in enumerate(route):
            place = df_places.iloc[place_id-1]
            
            # Add travel time
            if i > 0:
                prev_idx = route[i-1] - 1
                travel_time = time_matrix[prev_idx][place_id-1]
                # ✅ KONVERSI numpy.int64/float64 ke Python int/float
                travel_time = float(travel_time)  # atau int(travel_time)
                current_time += timedelta(minutes=travel_time)
            
            # Add visit time
            visit_time = place['visit_duration_min']
            # ✅ KONVERSI numpy.int64 ke Python int
            visit_time = int(visit_time)  # Konversi ke Python int
            current_time += timedelta(minutes=visit_time)
            
            # Check if exceeded end time
            if current_time > end_time:
                return False
        
        return True

    def plot_route_on_map(self):
        """Generate route map"""
        if not self.current_route or not self.preferences:
            return None
        
        center_lat = self.df_places['latitude'].mean()
        center_lon = self.df_places['longitude'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

        # Add hotel marker
        start_loc = self.preferences['start_location']
        folium.Marker(
            location=[start_loc['latitude'], start_loc['longitude']],
            popup=f"Start/End: {start_loc['name']}",
            tooltip=start_loc['name'],
            icon=folium.Icon(color='green', icon='home')
        ).add_to(m)

        # Add place markers
        for i, place_id in enumerate(self.current_route):
            place = self.df_places.iloc[place_id-1]
            
            # Different colors based on visit status
            if i <= self.current_position:
                color = 'red'  # Visited
                icon = 'ok'
            elif place_id in self.preferences.get('must_visit', []):
                color = 'orange'  # Must visit (not yet visited)
                icon = 'star'
            else:
                color = 'blue'  # Regular (not yet visited)
                icon = 'info-sign'

            # Create popup content
            popup_content = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="margin: 0 0 10px 0;">{i+1}. {place['name']}</h4>
                <p style="margin: 5px 0;"><strong>Kategori:</strong> {place['category']}</p>
                <p style="margin: 5px 0;"><strong>Biaya Masuk:</strong> Rp{place['entrance_fee']:,}</p>
                <p style="margin: 5px 0;"><strong>Jam Buka:</strong> {place['open_time']} - {place['close_time']}</p>
                <p style="margin: 5px 0;"><strong>Durasi:</strong> {place['visit_duration_min']} menit</p>
                <p style="margin: 5px 0;"><strong>Popularitas:</strong> {place['popularity']}/10</p>
                {"<p style='color: red; margin: 5px 0;'><strong>✓ DIKUNJUNGI</strong></p>" if i <= self.current_position else ""}
            </div>
            """

            folium.Marker(
                location=[place['latitude'], place['longitude']],
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=f"{place['name']} - {place['category']}",
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)

        # Add route line
        route_points = []
        route_points.append([start_loc['latitude'], start_loc['longitude']])

        for place_id in self.current_route:
            place = self.df_places.iloc[place_id-1]
            route_points.append([place['latitude'], place['longitude']])

        route_points.append([start_loc['latitude'], start_loc['longitude']])

        # Different line styles for visited vs planned route
        if self.current_position >= 0:
            # Visited route (thicker, green)
            visited_points = route_points[:self.current_position + 2]  # +2 for hotel start and current position
            if len(visited_points) >= 2:
                folium.PolyLine(
                    visited_points,
                    color='green',
                    weight=4,
                    opacity=0.8,
                    popup="Rute yang sudah dilalui"
                ).add_to(m)
            
            # Remaining route (thinner, blue)
            remaining_points = route_points[self.current_position + 1:]
            if len(remaining_points) >= 2:
                folium.PolyLine(
                    remaining_points,
                    color='blue',
                    weight=2,
                    opacity=0.6,
                    dash_array='5, 5',
                    popup="Rute yang akan dilalui"
                ).add_to(m)
        else:
            # Full planned route
            folium.PolyLine(
                route_points,
                color='blue',
                weight=3,
                opacity=0.7,
                popup="Rute lengkap"
            ).add_to(m)

        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><strong>Legenda</strong></p>
        <p><i class="fa fa-home" style="color:green"></i> Hotel</p>
        <p><i class="fa fa-check" style="color:red"></i> Sudah Dikunjungi</p>
        <p><i class="fa fa-star" style="color:orange"></i> Wajib Kunjung</p>
        <p><i class="fa fa-info" style="color:blue"></i> Akan Dikunjungi</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        # Convert map to HTML string
        map_html = m._repr_html_()
        return map_html