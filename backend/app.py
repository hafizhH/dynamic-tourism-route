from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from tourism_optimizer import TourismOptimizer
import json
from datetime import datetime
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global optimizer instance
optimizer = TourismOptimizer()

@app.route('/')
def home():
    """API Documentation"""
    docs = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tourism Route Optimizer API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: white; padding: 5px 10px; border-radius: 3px; margin-right: 10px; }
            .get { background: #61affe; }
            .post { background: #49cc90; }
            .put { background: #fca130; }
        </style>
    </head>
    <body>
        <h1>🗺️ Tourism Route Optimizer API</h1>
        <p>API untuk optimasi rute wisata dengan 5 fitur utama</p>
        
        <h2>📋 Endpoints</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/optimize</strong>
            <p>Optimasi rute awal berdasarkan preferensi pengguna</p>
            <pre>Body: { "preferences": { "start_time": "08:00", "budget": 200000, ... } }</pre>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/next-place</strong>
            <p>Menu 1: Lanjutkan ke tempat berikutnya</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/reoptimize</strong>
            <p>Menu 2: Perbarui data real-time dan optimasi ulang rute</p>
            <pre>Body: { "current_time": "14:30" }</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/schedule</strong>
            <p>Menu 3: Lihat jadwal saat ini</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/route</strong>
            <p>Menu 4: Lihat rute saat ini</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/end-journey</strong>
            <p>Menu 5: Akhiri perjalanan</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/next-and-reoptimize</strong>
            <p>Gabungan Menu 1 & 2: Otomatis lanjut ke tempat berikutnya + reoptimasi rute</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/places</strong>
            <p>Lihat semua tempat wisata yang tersedia</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/map</strong>
            <p>Dapatkan peta rute dalam format HTML</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(docs)

@app.route('/api/optimize', methods=['POST'])
def optimize_route():
    print("🎯 STARTING ROUTE OPTIMIZATION")
    start_time = datetime.now()
    """Optimasi rute awal"""
    try:
        data = request.get_json() or {}
        preferences = data.get('preferences', {})
        
        print(f"📊 User Preferences: {preferences}")

        # Validate location data if provided
        if 'start_location' in preferences:
            start_loc = preferences['start_location']
            required_fields = ['name', 'latitude', 'longitude']
            if not all(field in start_loc for field in required_fields):
                print(f"❌ Invalid start_location: missing {required_fields}")
                return jsonify({
                    'status': 'error',
                    'message': f"start_location must include: {', '.join(required_fields)}"
                }), 400
            print(f"📍 Start Location: {start_loc['name']} ({start_loc['latitude']}, {start_loc['longitude']})")
        
        if 'end_location' in preferences:
            end_loc = preferences['end_location']
            required_fields = ['name', 'latitude', 'longitude']
            if not all(field in end_loc for field in required_fields):
                print(f"❌ Invalid end_location: missing {required_fields}")
                return jsonify({
                    'status': 'error',
                    'message': f"end_location must include: {', '.join(required_fields)}"
                }), 400
            print(f"🏁 End Location: {end_loc['name']} ({end_loc['latitude']}, {end_loc['longitude']})")
        
        # Check if user wants verbose output
        verbose = data.get('verbose', True)  # Default ke True untuk menampilkan GA progres
        # Optimize route with user preferences
        print("🧬 Running Genetic Algorithm...")
        result = optimizer.optimize_route(preferences, verbose=verbose)
        
        # Add location info to response
        result['used_preferences'] = {
            'start_location': optimizer.preferences['start_location'],
            'end_location': optimizer.preferences['end_location'],
            'budget': optimizer.preferences['budget'],
            'max_places': optimizer.preferences['max_places']
        }

        execution_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ OPTIMIZATION COMPLETED in {execution_time:.2f}s")
        print(f"🗺️ Best Route: {[optimizer.df_places.iloc[id-1]['name'] for id in result['route']]}")
        print(f"💰 Total Cost: Rp{result['total_cost']:,}")
        print(f"📈 Fitness Score: {result['fitness']:.2f}")
        
        return jsonify({
            'status': 'success',
            'data': result,
            'message': 'Rute berhasil dioptimasi'
        })
        
    except ValueError as ve:
        print(f"❌ Validation Error: {str(ve)}")
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400
        
    except Exception as e:
        print(f"💥 Optimization Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/next-place', methods=['POST'])
def next_place():
    """Menu 1: Lanjutkan ke tempat berikutnya"""
    print("➡️ NEXT PLACE REQUEST")
    try:
        print(f"📍 Current Position: {optimizer.current_position}")
        print(f"🗺️ Total Places in Route: {len(optimizer.current_route)}")
        result = optimizer.get_next_place()

        if result['success']:
            current_place = result['current_place']
            print(f"✅ Moved to: {current_place['name']} (Position {result['current_position']})")
            print(f"📂 Category: {current_place['category']}")
            print(f"💰 Entrance Fee: Rp{current_place['entrance_fee']:,}")
        else:
            print(f"⚠️ Cannot move: {result['message']}")
        
        return jsonify({
            'status': 'success' if result['success'] else 'error',
            'data': result,
            'message': result['message']
        })
        
    except Exception as e:
        print(f"💥 Next Place Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/reoptimize', methods=['POST'])
def reoptimize_route():
    """Menu 2: Perbarui data real-time dan optimasi ulang rute"""
    try:
        data = request.get_json() or {}
        current_time = data.get('current_time')
        
        result = optimizer.reoptimize_route(current_time)
        
        return jsonify({
            'status': 'success' if result['success'] else 'error',
            'data': result,
            'message': result['message']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Menu 3: Lihat jadwal saat ini"""
    try:
        result = optimizer.get_current_schedule()
        
        return jsonify({
            'status': 'success' if result['success'] else 'error',
            'data': result,
            'message': result.get('message', 'Jadwal berhasil diambil')
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/route', methods=['GET'])
def get_route():
    """Menu 4: Lihat rute saat ini"""
    try:
        result = optimizer.get_current_route()
        
        return jsonify({
            'status': 'success' if result['success'] else 'error',
            'data': result,
            'message': result.get('message', 'Rute berhasil diambil')
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/end-journey', methods=['POST'])
def end_journey():
    """Menu 5: Akhiri perjalanan"""
    try:
        result = optimizer.end_journey()
        
        return jsonify({
            'status': 'success',
            'data': result,
            'message': result['message']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/places', methods=['GET'])
def get_places():
    """Lihat semua tempat wisata yang tersedia"""
    try:
        places_data = optimizer.df_places.to_dict('records')
        
        return jsonify({
            'status': 'success',
            'data': {
                'places': places_data,
                'total': len(places_data)
            },
            'message': 'Data tempat wisata berhasil diambil'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/map', methods=['GET'])
def get_map():
    """Dapatkan peta rute dalam format HTML"""
    try:
        map_html = optimizer.plot_route_on_map()
        
        if map_html:
            return jsonify({
                'status': 'success',
                'data': {
                    'map_html': map_html
                },
                'message': 'Peta berhasil dibuat'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Belum ada rute yang tersedia untuk ditampilkan'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Dapatkan status perjalanan saat ini"""
    try:
        current_route = optimizer.current_route
        current_position = optimizer.current_position
        
        if current_route:
            current_place_id = current_route[current_position] if current_position < len(current_route) else None
            current_place = None
            
            if current_place_id:
                current_place = {
                    'id': current_place_id,
                    'name': optimizer.df_places.iloc[current_place_id-1]['name'],
                    'category': optimizer.df_places.iloc[current_place_id-1]['category']
                }
            
            return jsonify({
                'status': 'success',
                'data': {
                    'has_route': True,
                    'current_position': current_position,
                    'total_places': len(current_route),
                    'current_place': current_place,
                    'progress_percentage': ((current_position + 1) / len(current_route)) * 100
                },
                'message': 'Status perjalanan berhasil diambil'
            })
        else:
            return jsonify({
                'status': 'success',
                'data': {
                    'has_route': False,
                    'message': 'Belum ada rute yang dioptimasi'
                },
                'message': 'Belum ada perjalanan aktif'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_journey():
    """Reset state perjalanan"""
    try:
        global optimizer
        optimizer = TourismOptimizer()
        
        return jsonify({
            'status': 'success',
            'message': 'State perjalanan berhasil direset'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    

@app.route('/api/next-and-reoptimize', methods=['POST'])
def next_place_and_reoptimize():
    print("➡️ NEXT PLACE AND REOPTIMIZED")
    """Gabungan Menu 1 & 2: Lanjut ke tempat berikutnya + Reoptimasi rute"""
    try:
        # Handle both empty body and JSON body
        if request.content_type == 'application/json':
            data = request.get_json() or {}
        else:
            data = {}
        
        # Generate current time otomatis dari server
        from datetime import datetime
        current_time = datetime.now().strftime('%H:%M')
        
        # Step 1: Jalankan next-place (Menu 1)
        next_place_result = optimizer.get_next_place()
        
        if not next_place_result['success']:
            # Jika tidak bisa next place, return error
            return jsonify({
                'status': 'error',
                'data': {
                    'next_place': next_place_result,
                    'reoptimize': None
                },
                'message': next_place_result['message']
            })
        
        # Step 2: Jalankan reoptimize (Menu 2)
        reoptimize_result = optimizer.reoptimize_route(current_time)
        
        # Gabungkan hasil kedua proses
        combined_result = {
            'success': True,
            'step1_next_place': next_place_result,
            'step2_reoptimize': reoptimize_result,
            'summary': {
                'moved_to': next_place_result.get('current_place', {}).get('name', 'Unknown'),
                'new_position': next_place_result.get('current_position', 0),
                'route_updated': reoptimize_result.get('success', False),
                'weather_condition': reoptimize_result.get('dynamic_data', {}).get('weather', 'Unknown'),
                'total_places_in_route': len(reoptimize_result.get('updated_route', []))
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': combined_result,
            'message': f"Berhasil pindah ke {next_place_result.get('current_place', {}).get('name', 'tempat berikutnya')} dan rute telah dioptimasi ulang"
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Error dalam proses gabungan: {str(e)}"
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint tidak ditemukan'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'Method tidak diizinkan'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Terjadi kesalahan internal server'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Tourism Route Optimizer API...")
    print("📍 API Documentation: http://localhost:5000")
    print("🗺️  Optimize Route: POST http://localhost:5000/api/optimize")
    print("➡️  Next Place: POST http://localhost:5000/api/next-place")
    print("🔄 Reoptimize: POST http://localhost:5000/api/reoptimize")
    print("📅 Schedule: GET http://localhost:5000/api/schedule")
    print("🛣️  Route: GET http://localhost:5000/api/route")
    print("🏁 End Journey: POST http://localhost:5000/api/end-journey")
    
    app.run(debug=True, host='0.0.0.0', port=5000)