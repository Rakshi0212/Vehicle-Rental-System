from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Database config state
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'RK!02006',  # Configured user password
    'database': 'vehicle_rental_db',
    'port': 3306
}

is_mock_mode = False

# Fallback Mock Database (In-Memory)
mock_db = {
    'customers': [
        { 'customer_id': 1, 'name': 'Rakshitha Shetty', 'phone': '9876543210', 'license_number': 'DL-5523910' },
        { 'customer_id': 2, 'name': 'John Doe', 'phone': '9887766554', 'license_number': 'DL-8827394' },
        { 'customer_id': 3, 'name': 'Alice Smith', 'phone': '9123456789', 'license_number': 'DL-1192834' },
        { 'customer_id': 4, 'name': 'Bob Johnson', 'phone': '9445566778', 'license_number': 'DL-4483920' },
        { 'customer_id': 5, 'name': 'Carol White', 'phone': '9556677889', 'license_number': 'DL-6672839' }
    ],
    'vehicles': [
        { 'vehicle_id': 1, 'model': 'Toyota Camry', 'type': 'Sedan', 'rental_price_per_day': 50.00, 'status': 'Available' },
        { 'vehicle_id': 2, 'model': 'Honda Civic', 'type': 'Sedan', 'rental_price_per_day': 45.00, 'status': 'Available' },
        { 'vehicle_id': 3, 'model': 'Ford Explorer', 'type': 'SUV', 'rental_price_per_day': 80.00, 'status': 'Available' },
        { 'vehicle_id': 4, 'model': 'Chevrolet Suburban', 'type': 'SUV', 'rental_price_per_day': 100.00, 'status': 'Maintenance' },
        { 'vehicle_id': 5, 'model': 'Tesla Model 3', 'type': 'Sedan', 'rental_price_per_day': 90.00, 'status': 'Available' },
        { 'vehicle_id': 6, 'model': 'Jeep Wrangler', 'type': 'SUV', 'rental_price_per_day': 85.00, 'status': 'Available' },
        { 'vehicle_id': 7, 'model': 'Harley Davidson Iron 883', 'type': 'Motorcycle', 'rental_price_per_day': 40.00, 'status': 'Available' },
        { 'vehicle_id': 8, 'model': 'BMW 3 Series', 'type': 'Sedan', 'rental_price_per_day': 75.00, 'status': 'Available' },
        { 'vehicle_id': 9, 'model': 'Ford F-150', 'type': 'Truck', 'rental_price_per_day': 70.00, 'status': 'Available' }
    ],
    'bookings': [],
    'rentals': [],
    'payments': [],
    'maintenances': [
        { 'maintenance_id': 1, 'vehicle_id': 4, 'description': 'Engine oil leakage and brake replacement', 'maintenance_date': '2026-06-10', 'status': 'Pending' }
    ]
}

# Seed mock bookings/rentals to replicate SQL script
def seed_mock_data():
    global mock_db
    mock_db['bookings'] = []
    mock_db['rentals'] = []
    mock_db['payments'] = []
    
    booking_id_count = 1
    rental_id_count = 1
    
    # 16 Sedan rentals (required to satisfy HAVING > 15 count query)
    sedan_bookings = [
        (1, 1, '2026-05-01', '2026-05-01', '2026-05-03', 100.00),
        (2, 1, '2026-05-03', '2026-05-03', '2026-05-06', 150.00),
        (3, 1, '2026-05-05', '2026-05-05', '2026-05-06', 50.00),
        (4, 1, '2026-05-07', '2026-05-07', '2026-05-10', 150.00),
        (5, 2, '2026-05-02', '2026-05-02', '2026-05-04', 90.00),
        (1, 2, '2026-05-04', '2026-05-04', '2026-05-07', 135.00),
        (2, 2, '2026-05-06', '2026-05-06', '2026-05-07', 45.00),
        (3, 2, '2026-05-08', '2026-05-08', '2026-05-12', 180.00),
        (4, 5, '2026-05-10', '2026-05-10', '2026-05-11', 90.00),
        (5, 5, '2026-05-12', '2026-05-12', '2026-05-15', 270.00),
        (1, 5, '2026-05-14', '2026-05-14', '2026-05-15', 90.00),
        (2, 5, '2026-05-16', '2026-05-16', '2026-05-20', 360.00),
        (3, 8, '2026-05-11', '2026-05-11', '2026-05-13', 150.00),
        (4, 8, '2026-05-13', '2026-05-13', '2026-05-16', 225.00),
        (5, 8, '2026-05-15', '2026-05-15', '2026-05-16', 75.00),
        (1, 8, '2026-05-17', '2026-05-17', '2026-05-22', 375.00)
    ]
    
    for cust, veh, bk_date, start, end, amt in sedan_bookings:
        mock_db['bookings'].append({ 'booking_id': booking_id_count, 'customer_id': cust, 'vehicle_id': veh, 'booking_date': bk_date })
        mock_db['rentals'].append({ 'rental_id': rental_id_count, 'booking_id': booking_id_count, 'start_date': start, 'end_date': end, 'total_amount': amt })
        booking_id_count += 1
        rental_id_count += 1

    # 4 SUV rentals
    suv_bookings = [
        (2, 3, '2026-05-20', '2026-05-20', '2026-05-23', 240.00),
        (3, 3, '2026-05-22', '2026-05-22', '2026-05-24', 160.00),
        (4, 6, '2026-05-24', '2026-05-24', '2026-05-26', 170.00),
        (5, 6, '2026-05-26', '2026-05-26', '2026-05-30', 340.00)
    ]
    
    for cust, veh, bk_date, start, end, amt in suv_bookings:
        mock_db['bookings'].append({ 'booking_id': booking_id_count, 'customer_id': cust, 'vehicle_id': veh, 'booking_date': bk_date })
        mock_db['rentals'].append({ 'rental_id': rental_id_count, 'booking_id': booking_id_count, 'start_date': start, 'end_date': end, 'total_amount': amt })
        booking_id_count += 1
        rental_id_count += 1

    # 1 Truck rental
    mock_db['bookings'].append({ 'booking_id': booking_id_count, 'customer_id': 1, 'vehicle_id': 9, 'booking_date': '2026-05-28' })
    mock_db['rentals'].append({ 'rental_id': rental_id_count, 'booking_id': booking_id_count, 'start_date': '2026-05-28', 'end_date': '2026-05-30', 'total_amount': 140.00 })
    booking_id_count += 1
    rental_id_count += 1

    # Seed mock payments
    mock_db['payments'] = [
        { 'payment_id': 1, 'rental_id': 1, 'amount': 100.00, 'payment_date': '2026-05-03' },
        { 'payment_id': 2, 'rental_id': 2, 'amount': 150.00, 'payment_date': '2026-05-06' },
        { 'payment_id': 3, 'rental_id': 5, 'amount': 90.00, 'payment_date': '2026-05-04' },
        { 'payment_id': 4, 'rental_id': 17, 'amount': 240.00, 'payment_date': '2026-05-23' }
    ]

seed_mock_data()

# Check MySQL connection helper
def get_db_connection():
    global is_mock_mode
    if is_mock_mode:
        return None
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            port=db_config['port']
        )
        return conn
    except Error as e:
        print(f"[Warning] Database connection failed: {e}. Switching to Mock Database Mode.")
        is_mock_mode = True
        return None

# Attempt initial connection
try:
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        port=db_config['port']
    )
    if conn.is_connected():
        print("Connected to MySQL database successfully!")
        conn.close()
except Exception:
    print("[Warning] Could not connect to MySQL. Starting in Mock Mode (Offline).")
    is_mock_mode = True

# Helper to run raw SQL (returns list of dicts)
def execute_sql_query(query, params=None):
    conn = get_db_connection()
    if conn is None:
        return run_mock_query(query, params)
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("SHOW") or query.strip().upper().startswith("CALL"):
            try:
                result = cursor.fetchall()
            except mysql.connector.errors.InterfaceError:
                # In case stored procedure returns nothing or has multiple result sets
                result = []
        else:
            conn.commit()
            result = {"affected_rows": cursor.rowcount}
        return result
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# Mock SQL Parser for fallbacks
def run_mock_query(query, params):
    global mock_db
    q = query.strip().replace('\n', ' ').replace('\t', ' ').lower()
    
    # Simple Mock SELECT queries
    if q.startswith("select * from vehicle") and "where status = 'available'" in q:
        return [v for v in mock_db['vehicles'] if v['status'] == 'Available']
    elif q.startswith("select * from vehicle"):
        return mock_db['vehicles']
    elif q.startswith("select * from customer"):
        return mock_db['customers']
    elif q.startswith("select * from booking"):
        return mock_db['bookings']
    elif q.startswith("select * from rental"):
        return mock_db['rentals']
    elif q.startswith("select * from payment"):
        return mock_db['payments']
    elif q.startswith("select * from maintenance"):
        return mock_db['maintenances']

    # Query 3: Rental & Customer Join (2-Table INNER JOIN)
    elif "inner join booking b on r.booking_id = b.booking_id" in q and "inner join customer c" in q and "vehicle" not in q:
        results = []
        for r in mock_db['rentals']:
            bk = next((b for b in mock_db['bookings'] if b['booking_id'] == r['booking_id']), None)
            cust = next((c for c in mock_db['customers'] if c['customer_id'] == bk['customer_id']), None) if bk else None
            if cust:
                results.append({
                    'rental_id': r['rental_id'],
                    'customer_name': cust['name'],
                    'phone': cust['phone'],
                    'start_date': r['start_date'],
                    'end_date': r['end_date'],
                    'total_amount': float(r['total_amount'])
                })
        return results

    # Query 4: Rental, Customer & Vehicle 3-Table Join
    elif "inner join booking b on r.booking_id = b.booking_id" in q and "inner join customer c" in q and "inner join vehicle v" in q:
        results = []
        for r in mock_db['rentals']:
            bk = next((b for b in mock_db['bookings'] if b['booking_id'] == r['booking_id']), None)
            cust = next((c for c in mock_db['customers'] if c['customer_id'] == bk['customer_id']), None) if bk else None
            veh = next((v for v in mock_db['vehicles'] if v['vehicle_id'] == bk['vehicle_id']), None) if bk else None
            if cust and veh:
                results.append({
                    'rental_id': r['rental_id'],
                    'customer_name': cust['name'],
                    'vehicle_model': veh['model'],
                    'vehicle_type': veh['type'],
                    'start_date': r['start_date'],
                    'end_date': r['end_date'],
                    'total_amount': float(r['total_amount'])
                })
        return results

    # Query 5 & 6: GROUP BY / HAVING (Rentals per vehicle type)
    elif "group by v.type" in q or "group by type" in q:
        counts = {}
        for r in mock_db['rentals']:
            bk = next((b for b in mock_db['bookings'] if b['booking_id'] == r['booking_id']), None)
            veh = next((v for v in mock_db['vehicles'] if v['vehicle_id'] == bk['vehicle_id']), None) if bk else None
            if veh:
                counts[veh['type']] = counts.get(veh['type'], 0) + 1
        
        has_having = "having count(r.rental_id) > 15" in q or "having count(" in q
        results = []
        for vtype, count in counts.items():
            if has_having and count <= 15:
                continue
            results.append({
                'vehicle_type': vtype,
                'total_rentals': count
            })
        return results

    # Query 7: Subquery (Vehicles rental price > average price)
    elif "rental_price_per_day > (select avg" in q:
        avg_price = sum(v['rental_price_per_day'] for v in mock_db['vehicles']) / len(mock_db['vehicles'])
        return [v for v in mock_db['vehicles'] if v['rental_price_per_day'] > avg_price]

    # Query 8: Correlated Subquery (Customers who rented more than customer 2)
    elif "customer_id = 2" in q:
        # Count bookings for customer_id = 2
        cust2_bookings = sum(1 for b in mock_db['bookings'] if b['customer_id'] == 2)
        results = []
        for c in mock_db['customers']:
            c_bookings = sum(1 for b in mock_db['bookings'] if b['customer_id'] == c['customer_id'])
            if c_bookings > cust2_bookings:
                results.append({
                    'customer_id': c['customer_id'],
                    'name': c['name'],
                    'booking_count': c_bookings
                })
        return results

    # Query 9: LEFT JOIN (All vehicles including not rented)
    elif "left join booking" in q:
        results = []
        for v in mock_db['vehicles']:
            bookings = [b for b in mock_db['bookings'] if b['vehicle_id'] == v['vehicle_id']]
            if not bookings:
                results.append({
                    'vehicle_id': v['vehicle_id'],
                    'model': v['model'],
                    'type': v['type'],
                    'status': v['status'],
                    'booking_id': None,
                    'booking_date': None
                })
            else:
                for b in bookings:
                    results.append({
                        'vehicle_id': v['vehicle_id'],
                        'model': v['model'],
                        'type': v['type'],
                        'status': v['status'],
                        'booking_id': b['booking_id'],
                        'booking_date': b['booking_date']
                    })
        return results

    # Query 10: NOT EXISTS (Vehicles never rented)
    elif "not exists" in q:
        booked_vehicle_ids = {b['vehicle_id'] for b in mock_db['bookings']}
        return [v for v in mock_db['vehicles'] if v['vehicle_id'] not in booked_vehicle_ids]

    # Stored Procedures
    elif "getvehicleavailabilityreport" in q:
        counts = {}
        for v in mock_db['vehicles']:
            counts[v['status']] = counts.get(v['status'], 0) + 1
        return [{'status': k, 'vehicle_count': v} for k, v in counts.items()]

    raise ValueError(f"Query simulation not fully implemented in Mock Mode for: '{query}'. Run on real MySQL for full engine support.")


# -------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Config Endpoint (Check DB mode and modify credentials)
@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    global is_mock_mode, db_config
    if request.method == 'POST':
        data = request.json
        db_config['host'] = data.get('host', db_config['host'])
        db_config['user'] = data.get('user', db_config['user'])
        db_config['password'] = data.get('password', db_config['password'])
        db_config['database'] = data.get('database', db_config['database'])
        db_config['port'] = int(data.get('port', db_config['port']))
        
        # Test connection
        is_mock_mode = False
        try:
            conn = mysql.connector.connect(**db_config)
            is_connected = conn.is_connected()
            conn.close()
            if is_connected:
                return jsonify({
                    "status": "connected",
                    "message": f"Successfully connected to MySQL database '{db_config['database']}'!",
                    "is_mock": False
                })
        except Exception as e:
            is_mock_mode = True
            return jsonify({
                "status": "failed",
                "message": f"Connection failed: {str(e)}. Automatically fallback to Mock Mode.",
                "is_mock": True
            })
            
    # GET method
    # Try testing connection briefly
    test_mock = is_mock_mode
    if not test_mock:
        try:
            conn = mysql.connector.connect(**db_config)
            conn.close()
        except Exception:
            test_mock = True
            
    return jsonify({
        "config": {
            "host": db_config['host'],
            "user": db_config['user'],
            "database": db_config['database'],
            "port": db_config['port']
        },
        "is_mock": test_mock
    })

# ----------------- CUSTOMERS -----------------
@app.route('/api/customers', methods=['GET', 'POST'])
def manage_customers():
    global mock_db
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Customer")
                records = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(records)
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify(mock_db['customers'])
            
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        license_number = data.get('license_number')
        
        if not name or not phone or not license_number:
            return jsonify({"error": "Missing required fields"}), 400
            
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Customer (name, phone, license_number) VALUES (%s, %s, %s)",
                    (name, phone, license_number)
                )
                conn.commit()
                new_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return jsonify({"message": "Customer added successfully!", "customer_id": new_id}), 201
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            # Check unique license
            if any(c['license_number'] == license_number for c in mock_db['customers']):
                return jsonify({"error": "Error: Duplicate entry for license number!"}), 400
            new_id = max([c['customer_id'] for c in mock_db['customers']], default=0) + 1
            new_cust = { "customer_id": new_id, "name": name, "phone": phone, "license_number": license_number }
            mock_db['customers'].append(new_cust)
            return jsonify({"message": "Customer added successfully (Mock Mode)!", "customer_id": new_id}), 201

@app.route('/api/customers/<int:id>', methods=['PUT', 'DELETE'])
def detail_customer(id):
    global mock_db
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        license_number = data.get('license_number')
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Customer SET name = %s, phone = %s, license_number = %s WHERE customer_id = %s",
                    (name, phone, license_number, id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"message": "Customer updated successfully!"})
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            cust = next((c for c in mock_db['customers'] if c['customer_id'] == id), None)
            if not cust:
                return jsonify({"error": "Customer not found"}), 404
            
            # Check license uniqueness excluding current record
            if any(c['license_number'] == license_number and c['customer_id'] != id for c in mock_db['customers']):
                return jsonify({"error": "Error: License number must be unique!"}), 400
                
            cust['name'] = name
            cust['phone'] = phone
            cust['license_number'] = license_number
            return jsonify({"message": "Customer updated successfully (Mock Mode)!"})
            
    elif request.method == 'DELETE':
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Customer WHERE customer_id = %s", (id,))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"message": "Customer deleted successfully!"})
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            idx = next((i for i, c in enumerate(mock_db['customers']) if c['customer_id'] == id), -1)
            if idx == -1:
                return jsonify({"error": "Customer not found"}), 404
            mock_db['customers'].pop(idx)
            # Cascade delete mock bookings
            mock_db['bookings'] = [b for b in mock_db['bookings'] if b['customer_id'] != id]
            return jsonify({"message": "Customer deleted successfully (Mock Mode)!"})

# ----------------- VEHICLES -----------------
@app.route('/api/vehicles', methods=['GET', 'POST'])
def manage_vehicles():
    global mock_db
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Vehicle")
                records = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(records)
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify(mock_db['vehicles'])
            
    elif request.method == 'POST':
        data = request.json
        model = data.get('model')
        vtype = data.get('type')
        rental_price = data.get('rental_price_per_day')
        status = data.get('status', 'Available')
        
        if not model or not vtype or rental_price is None:
            return jsonify({"error": "Missing required fields"}), 400
            
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Vehicle (model, type, rental_price_per_day, status) VALUES (%s, %s, %s, %s)",
                    (model, vtype, rental_price, status)
                )
                conn.commit()
                new_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return jsonify({"message": "Vehicle added successfully!", "vehicle_id": new_id}), 201
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            new_id = max([v['vehicle_id'] for v in mock_db['vehicles']], default=0) + 1
            new_veh = { "vehicle_id": new_id, "model": model, "type": vtype, "rental_price_per_day": float(rental_price), "status": status }
            mock_db['vehicles'].append(new_veh)
            return jsonify({"message": "Vehicle added successfully (Mock Mode)!", "vehicle_id": new_id}), 201

@app.route('/api/vehicles/<int:id>', methods=['PUT', 'DELETE'])
def detail_vehicle(id):
    global mock_db
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        model = data.get('model')
        vtype = data.get('type')
        rental_price = data.get('rental_price_per_day')
        status = data.get('status')
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Vehicle SET model = %s, type = %s, rental_price_per_day = %s, status = %s WHERE vehicle_id = %s",
                    (model, vtype, rental_price, status, id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"message": "Vehicle updated successfully!"})
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            veh = next((v for v in mock_db['vehicles'] if v['vehicle_id'] == id), None)
            if not veh:
                return jsonify({"error": "Vehicle not found"}), 404
            veh['model'] = model
            veh['type'] = vtype
            veh['rental_price_per_day'] = float(rental_price)
            veh['status'] = status
            return jsonify({"message": "Vehicle updated successfully (Mock Mode)!"})
            
    elif request.method == 'DELETE':
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Vehicle WHERE vehicle_id = %s", (id,))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"message": "Vehicle deleted successfully!"})
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            idx = next((i for i, v in enumerate(mock_db['vehicles']) if v['vehicle_id'] == id), -1)
            if idx == -1:
                return jsonify({"error": "Vehicle not found"}), 404
            mock_db['vehicles'].pop(idx)
            # Cascade deletes mock bookings, maintenances
            mock_db['bookings'] = [b for b in mock_db['bookings'] if b['vehicle_id'] != id]
            mock_db['maintenances'] = [m for m in mock_db['maintenances'] if m['vehicle_id'] != id]
            return jsonify({"message": "Vehicle deleted successfully (Mock Mode)!"})

# ----------------- BOOKINGS -----------------
@app.route('/api/bookings', methods=['GET', 'POST'])
def manage_bookings():
    global mock_db
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT b.*, c.name AS customer_name, v.model AS vehicle_model 
                    FROM Booking b 
                    JOIN Customer c ON b.customer_id = c.customer_id 
                    JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
                """)
                records = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(records)
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            results = []
            for b in mock_db['bookings']:
                c = next((cust for cust in mock_db['customers'] if cust['customer_id'] == b['customer_id']), None)
                v = next((veh for veh in mock_db['vehicles'] if veh['vehicle_id'] == b['vehicle_id']), None)
                results.append({
                    **b,
                    "customer_name": c['name'] if c else "Unknown",
                    "vehicle_model": v['model'] if v else "Unknown"
                })
            return jsonify(results)
            
    elif request.method == 'POST':
        data = request.json
        customer_id = data.get('customer_id')
        vehicle_id = data.get('vehicle_id')
        booking_date = data.get('booking_date', datetime.today().strftime('%Y-%m-%d'))
        
        # Rental details (to automatically insert Rental details when booking is made)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not customer_id or not vehicle_id:
            return jsonify({"error": "Missing customer_id or vehicle_id"}), 400
            
        if conn:
            try:
                cursor = conn.cursor()
                
                # Check transaction triggers (handled automatically by MySQL triggers, but we run in a transaction)
                # Inserting a Booking will trigger:
                # 1. BEFORE: Prevent if Maintenance (raises 45000 state)
                # 2. AFTER: Update Vehicle status to 'Rented'
                cursor.execute(
                    "INSERT INTO Booking (customer_id, vehicle_id, booking_date) VALUES (%s, %s, %s)",
                    (customer_id, vehicle_id, booking_date)
                )
                booking_id = cursor.lastrowid
                
                # Also insert Rental record if date range is provided
                if start_date and end_date:
                    cursor.execute(
                        "INSERT INTO Rental (booking_id, start_date, end_date, total_amount) VALUES (%s, %s, %s, 0.00)",
                        (booking_id, start_date, end_date)
                    )
                
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"message": "Booking successful! Vehicle status updated to 'Rented' by database trigger.", "booking_id": booking_id}), 201
            except Error as e:
                # Catch trigger SIGNAL SQLSTATE errors
                return jsonify({"error": str(e)}), 400
        else:
            # Trigger Sim 2: Prevent booking if under maintenance
            veh = next((v for v in mock_db['vehicles'] if v['vehicle_id'] == int(vehicle_id)), None)
            if not veh:
                return jsonify({"error": "Vehicle not found"}), 404
            if veh['status'] == 'Maintenance':
                return jsonify({"error": "Error: Cannot book this vehicle because it is currently under maintenance! (Mock Trigger Prevention)"}), 400
                
            # Insert booking
            new_booking_id = max([b['booking_id'] for b in mock_db['bookings']], default=0) + 1
            mock_db['bookings'].append({
                "booking_id": new_booking_id,
                "customer_id": int(customer_id),
                "vehicle_id": int(vehicle_id),
                "booking_date": booking_date
            })
            
            # Trigger Sim 1: Update status to 'Rented'
            veh['status'] = 'Rented'
            
            # Create corresponding Rental automatically
            if start_date and end_date:
                new_rental_id = max([r['rental_id'] for r in mock_db['rentals']], default=0) + 1
                mock_db['rentals'].append({
                    "rental_id": new_rental_id,
                    "booking_id": new_booking_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_amount": 0.00
                })
                
            return jsonify({"message": "Booking successful (Mock Mode)! Vehicle status updated to 'Rented' by mock trigger.", "booking_id": new_booking_id}), 201

# ----------------- RENTALS & PROCEDURES -----------------
@app.route('/api/rentals', methods=['GET'])
def get_rentals():
    global mock_db
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, c.name AS customer_name, v.model AS vehicle_model 
                FROM Rental r
                JOIN Booking b ON r.booking_id = b.booking_id
                JOIN Customer c ON b.customer_id = c.customer_id
                JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
            """)
            records = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(records)
        except Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        results = []
        for r in mock_db['rentals']:
            bk = next((b for b in mock_db['bookings'] if b['booking_id'] == r['booking_id']), None)
            c = next((cust for cust in mock_db['customers'] if cust['customer_id'] == bk['customer_id']), None) if bk else None
            v = next((veh for veh in mock_db['vehicles'] if veh['vehicle_id'] == bk['vehicle_id']), None) if bk else None
            results.append({
                **r,
                "customer_name": c['name'] if c else "Unknown",
                "vehicle_model": v['model'] if v else "Unknown"
            })
        return jsonify(results)

# Execute Procedure 1: CalculateRentalCharge
@app.route('/api/procedures/calculate-charge', methods=['POST'])
def run_procedure_calculate():
    global mock_db
    data = request.json
    rental_id = data.get('rental_id')
    
    if not rental_id:
        return jsonify({"error": "Missing rental_id"}), 400
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Call procedure CalculateRentalCharge
            # Syntax: CALL CalculateRentalCharge(rental_id, @out_total); SELECT @out_total;
            cursor.execute("SET @out_total = 0.00;")
            cursor.execute(f"CALL CalculateRentalCharge({rental_id}, @out_total);")
            cursor.execute("SELECT @out_total AS total_amount;")
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            total_amt = result[0] if result else 0.00
            return jsonify({
                "message": f"Procedure CalculateRentalCharge completed successfully!",
                "rental_id": rental_id,
                "total_amount": float(total_amt)
            })
        except Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Mock calculation
        rental = next((r for r in mock_db['rentals'] if r['rental_id'] == int(rental_id)), None)
        if not rental:
            return jsonify({"error": "Rental record not found"}), 404
            
        bk = next((b for b in mock_db['bookings'] if b['booking_id'] == rental['booking_id']), None)
        veh = next((v for v in mock_db['vehicles'] if v['vehicle_id'] == bk['vehicle_id']), None) if bk else None
        
        if not veh:
            return jsonify({"error": "Associated vehicle not found for this rental booking"}), 400
            
        try:
            d1 = datetime.strptime(rental['start_date'], '%Y-%m-%d')
            d2 = datetime.strptime(rental['end_date'], '%Y-%m-%d')
            days = max((d2 - d1).days, 1)
        except Exception:
            days = 1
            
        calculated_amt = float(veh['rental_price_per_day']) * days
        rental['total_amount'] = calculated_amt
        return jsonify({
            "message": "Procedure CalculateRentalCharge completed successfully (Mock Mode)!",
            "rental_id": rental_id,
            "total_amount": calculated_amt
        })

# Execute Procedure 2: GetVehicleAvailabilityReport
@app.route('/api/procedures/availability-report', methods=['GET'])
def run_procedure_report():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("CALL GetVehicleAvailabilityReport()")
            records = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(records)
        except Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Mock aggregation
        counts = {}
        for v in mock_db['vehicles']:
            counts[v['status']] = counts.get(v['status'], 0) + 1
        records = [{'status': k, 'vehicle_count': v} for k, v in counts.items()]
        return jsonify(records)

# ----------------- SQL WORKBENCH (Execute custom query) -----------------
@app.route('/api/query', methods=['POST'])
def run_custom_query():
    data = request.json
    raw_query = data.get('query', '').strip()
    
    if not raw_query:
        return jsonify({"error": "Query cannot be empty"}), 400
        
    try:
        results = execute_sql_query(raw_query)
        return jsonify({
            "status": "success",
            "results": results
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400

# ----------------- OTHER TABLES FOR DISPLAY -----------------
@app.route('/api/maintenances', methods=['GET', 'POST'])
def manage_maintenances():
    global mock_db
    conn = get_db_connection()
    if request.method == 'GET':
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT m.*, v.model AS vehicle_model 
                    FROM Maintenance m
                    JOIN Vehicle v ON m.vehicle_id = v.vehicle_id
                """)
                records = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(records)
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            results = []
            for m in mock_db['maintenances']:
                v = next((veh for veh in mock_db['vehicles'] if veh['vehicle_id'] == m['vehicle_id']), None)
                results.append({
                    **m,
                    "vehicle_model": v['model'] if v else "Unknown"
                })
            return jsonify(results)
            
    elif request.method == 'POST':
        data = request.json
        vehicle_id = data.get('vehicle_id')
        description = data.get('description')
        m_date = data.get('maintenance_date', datetime.today().strftime('%Y-%m-%d'))
        status = data.get('status', 'Pending')
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Maintenance (vehicle_id, description, maintenance_date, status) VALUES (%s, %s, %s, %s)",
                    (vehicle_id, description, m_date, status)
                )
                # Also set vehicle status to 'Maintenance'
                cursor.execute("UPDATE Vehicle SET status = 'Maintenance' WHERE vehicle_id = %s", (vehicle_id,))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"message": "Maintenance ticket created, vehicle set to 'Maintenance'!"}), 201
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            new_id = max([m['maintenance_id'] for m in mock_db['maintenances']], default=0) + 1
            mock_db['maintenances'].append({
                "maintenance_id": new_id,
                "vehicle_id": int(vehicle_id),
                "description": description,
                "maintenance_date": m_date,
                "status": status
            })
            # Update status in vehicle list
            veh = next((v for v in mock_db['vehicles'] if v['vehicle_id'] == int(vehicle_id)), None)
            if veh:
                veh['status'] = 'Maintenance'
            return jsonify({"message": "Maintenance ticket created (Mock), vehicle status updated!"}), 201

@app.route('/api/payments', methods=['GET', 'POST'])
def manage_payments():
    global mock_db
    conn = get_db_connection()
    if request.method == 'GET':
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Payment")
                records = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(records)
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify(mock_db['payments'])
            
    elif request.method == 'POST':
        data = request.json
        rental_id = data.get('rental_id')
        amount = data.get('amount')
        p_date = data.get('payment_date', datetime.today().strftime('%Y-%m-%d'))
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Payment (rental_id, amount, payment_date) VALUES (%s, %s, %s)",
                    (rental_id, amount, p_date)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"message": "Payment logged successfully!"}), 201
            except Error as e:
                return jsonify({"error": str(e)}), 500
        else:
            new_id = max([p['payment_id'] for p in mock_db['payments']], default=0) + 1
            mock_db['payments'].append({
                "payment_id": new_id,
                "rental_id": int(rental_id),
                "amount": float(amount),
                "payment_date": p_date
            })
            return jsonify({"message": "Payment logged successfully (Mock Mode)!"}), 201

if __name__ == '__main__':
    # Start server on local port 5000
    print("Flask backend server running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
