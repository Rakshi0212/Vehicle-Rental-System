# VEHICLE RENTAL MANAGEMENT SYSTEM
## Database Management System — Project Report

| | |
|---|---|
| **Project Title** | Vehicle Rental Management System |
| **Student Name** | Rakshitha |
| **Roll Number** | ad034 |
| **Subject** | Database Management Systems (DBMS) |
| **Database** | MySQL |
| **Tech Stack** | MySQL · Python (Flask) · HTML · CSS · JavaScript |

---

## 1. INTRODUCTION

### 1.1 Project Overview
The **Vehicle Rental Management System** is a relational database-driven application designed to manage the complete lifecycle of a vehicle rental business. It handles customer registration, vehicle inventory, booking management, rental tracking, payment processing, and vehicle maintenance records.

### 1.2 Objectives
- Design a fully normalized relational database schema
- Implement referential integrity using Foreign Keys and Constraints
- Demonstrate SQL concepts: JOINs, Subqueries, GROUP BY, HAVING, NOT EXISTS
- Implement database automation using **Triggers**
- Create reusable **Stored Procedures** for business logic
- Build a full-stack web application connected to the MySQL database

### 1.3 Problem Statement
Manual tracking of vehicle rentals is error-prone and inefficient. This system automates:
- Vehicle availability tracking (via triggers)
- Rental cost calculation (via stored procedures)
- Prevention of invalid bookings (vehicles under maintenance)
- Comprehensive reporting (joins, aggregations, subqueries)

---

## 2. SYSTEM DESIGN

### 2.1 Entity-Relationship Overview

The system has **6 entities**:

```
Customer ──< Booking >── Vehicle
               │
             Rental
               │
             Payment

Vehicle ──< Maintenance
```

- A **Customer** can make multiple **Bookings**
- A **Booking** links one Customer to one Vehicle on a specific date
- Each **Booking** has one corresponding **Rental** record (dates + cost)
- A **Rental** can have one **Payment**
- A **Vehicle** can have multiple **Maintenance** records

### 2.2 Database Schema (6 Tables)

#### Table 1: Customer
```sql
CREATE TABLE Customer (
    customer_id      INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    phone            VARCHAR(15)  NOT NULL,
    license_number   VARCHAR(50)  UNIQUE NOT NULL
);
```
| Column | Type | Constraints |
|---|---|---|
| customer_id | INT | PRIMARY KEY, AUTO_INCREMENT |
| name | VARCHAR(100) | NOT NULL |
| phone | VARCHAR(15) | NOT NULL |
| license_number | VARCHAR(50) | UNIQUE, NOT NULL |

---

#### Table 2: Vehicle
```sql
CREATE TABLE Vehicle (
    vehicle_id           INT AUTO_INCREMENT PRIMARY KEY,
    model                VARCHAR(100) NOT NULL,
    type                 VARCHAR(50)  NOT NULL,
    rental_price_per_day DECIMAL(10,2) NOT NULL,
    status               VARCHAR(20) DEFAULT 'Available'
                         CHECK (status IN ('Available', 'Rented', 'Maintenance'))
);
```
| Column | Type | Constraints |
|---|---|---|
| vehicle_id | INT | PRIMARY KEY, AUTO_INCREMENT |
| model | VARCHAR(100) | NOT NULL |
| type | VARCHAR(50) | NOT NULL |
| rental_price_per_day | DECIMAL(10,2) | NOT NULL |
| status | VARCHAR(20) | DEFAULT 'Available', CHECK constraint |

---

#### Table 3: Booking
```sql
CREATE TABLE Booking (
    booking_id   INT AUTO_INCREMENT PRIMARY KEY,
    customer_id  INT  NOT NULL,
    vehicle_id   INT  NOT NULL,
    booking_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id)  REFERENCES Vehicle(vehicle_id)  ON DELETE CASCADE
);
```

---

#### Table 4: Rental
```sql
CREATE TABLE Rental (
    rental_id    INT AUTO_INCREMENT PRIMARY KEY,
    booking_id   INT           NOT NULL,
    start_date   DATE          NOT NULL,
    end_date     DATE          NOT NULL,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id) ON DELETE CASCADE
);
```

---

#### Table 5: Payment
```sql
CREATE TABLE Payment (
    payment_id   INT AUTO_INCREMENT PRIMARY KEY,
    rental_id    INT           NOT NULL,
    amount       DECIMAL(10,2) NOT NULL,
    payment_date DATE          NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES Rental(rental_id) ON DELETE CASCADE
);
```

---

#### Table 6: Maintenance
```sql
CREATE TABLE Maintenance (
    maintenance_id   INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id       INT  NOT NULL,
    description      TEXT NOT NULL,
    maintenance_date DATE NOT NULL,
    status           VARCHAR(20) DEFAULT 'Pending'
                     CHECK (status IN ('Pending', 'Completed')),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
);
```

---

## 3. SQL QUERIES (10 Queries)

### Query 1 — Retrieve All Vehicles
```sql
SELECT * FROM Vehicle;
```
**Purpose:** Get a complete inventory of the entire rental fleet.

---

### Query 2 — Available Vehicles
```sql
SELECT * FROM Vehicle WHERE status = 'Available';
```
**Purpose:** Filter the fleet to show only vehicles currently available for rent.

---

### Query 3 — Rental & Customer Details (2-Table INNER JOIN)
```sql
SELECT
    r.rental_id,
    c.name AS customer_name,
    c.phone,
    r.start_date,
    r.end_date,
    r.total_amount
FROM Rental r
INNER JOIN Booking b ON r.booking_id = b.booking_id
INNER JOIN Customer c ON b.customer_id = c.customer_id;
```
**Purpose:** Match rental records to customer information. Rental and Customer are not directly linked — Booking acts as the bridge table.

---

### Query 4 — Full Rental History (3-Table INNER JOIN)
```sql
SELECT
    r.rental_id,
    c.name        AS customer_name,
    v.model       AS vehicle_model,
    v.type        AS vehicle_type,
    r.start_date,
    r.end_date,
    r.total_amount
FROM Rental r
INNER JOIN Booking b  ON r.booking_id  = b.booking_id
INNER JOIN Customer c ON b.customer_id = c.customer_id
INNER JOIN Vehicle v  ON b.vehicle_id  = v.vehicle_id;
```
**Purpose:** Comprehensive rental history — who rented which vehicle and for how long.

---

### Query 5 — Rentals per Vehicle Type (GROUP BY)
```sql
SELECT
    v.type AS vehicle_type,
    COUNT(r.rental_id) AS total_rentals
FROM Rental r
INNER JOIN Booking b ON r.booking_id = b.booking_id
INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
GROUP BY v.type;
```
**Purpose:** Aggregate rental count by vehicle category (Sedan, SUV, Truck, etc.).

---

### Query 6 — Vehicle Types with More Than 15 Rentals (HAVING)
```sql
SELECT
    v.type AS vehicle_type,
    COUNT(r.rental_id) AS total_rentals
FROM Rental r
INNER JOIN Booking b ON r.booking_id = b.booking_id
INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
GROUP BY v.type
HAVING COUNT(r.rental_id) > 15;
```
**Purpose:** Find the most popular vehicle category. The seed data has exactly 16 Sedan rentals, so this query returns only 'Sedan'.
> **Note:** `HAVING` filters *after* grouping, unlike `WHERE` which filters *before* grouping.

---

### Query 7 — Vehicles Above Average Rental Price (Subquery)
```sql
SELECT * FROM Vehicle
WHERE rental_price_per_day > (
    SELECT AVG(rental_price_per_day) FROM Vehicle
);
```
**Purpose:** Identify premium vehicles priced above the fleet average. The inner query calculates the average; the outer query uses it as a filter.

---

### Query 8 — Customers Who Rented More Than Customer #2 (Correlated Subquery)
```sql
SELECT
    c1.customer_id,
    c1.name,
    (SELECT COUNT(*) FROM Booking b1 WHERE b1.customer_id = c1.customer_id) AS booking_count
FROM Customer c1
WHERE (
    SELECT COUNT(*) FROM Booking b1 WHERE b1.customer_id = c1.customer_id
) > (
    SELECT COUNT(*) FROM Booking b2 WHERE b2.customer_id = 2
);
```
**Purpose:** Identify high-value customers. This is a **correlated subquery** — the inner query references `c1.customer_id` from the outer query and re-executes for every customer row.

---

### Query 9 — All Vehicles Including Unbooked (LEFT JOIN)
```sql
SELECT
    v.vehicle_id,
    v.model,
    v.type,
    v.status,
    b.booking_id,
    b.booking_date
FROM Vehicle v
LEFT JOIN Booking b ON v.vehicle_id = b.vehicle_id;
```
**Purpose:** Show the entire fleet with booking information. Vehicles that were never booked still appear with NULL in the booking columns.
> **INNER JOIN** would exclude unbooked vehicles. **LEFT JOIN** keeps all vehicles.

---

### Query 10 — Vehicles Never Rented (NOT EXISTS)
```sql
SELECT * FROM Vehicle v
WHERE NOT EXISTS (
    SELECT 1 FROM Booking b WHERE b.vehicle_id = v.vehicle_id
);
```
**Purpose:** Identify idle inventory — vehicles that never appeared in any booking record. In the seed data, **Harley Davidson Iron 883** (Vehicle 7) and **Chevrolet Suburban** under maintenance (Vehicle 4) are never booked.

---

## 4. TRIGGERS

### Trigger 1 — AFTER INSERT: Auto-Update Vehicle Status to 'Rented'
```sql
CREATE TRIGGER after_booking_insert
AFTER INSERT ON Booking
FOR EACH ROW
BEGIN
    UPDATE Vehicle
    SET status = 'Rented'
    WHERE vehicle_id = NEW.vehicle_id;
END;
```
**When it fires:** Automatically after a new row is inserted into the Booking table.

**What it does:** Updates the booked vehicle's status from `Available` to `Rented` without requiring any application-level code.

**Key concept:** `NEW.vehicle_id` refers to the `vehicle_id` value of the newly inserted booking row.

---

### Trigger 2 — BEFORE INSERT: Block Booking if Vehicle is Under Maintenance
```sql
CREATE TRIGGER before_booking_insert
BEFORE INSERT ON Booking
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(20);
    SELECT status INTO v_status FROM Vehicle WHERE vehicle_id = NEW.vehicle_id;
    IF v_status = 'Maintenance' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cannot book this vehicle because it is currently under maintenance!';
    END IF;
END;
```
**When it fires:** Before any new row is inserted into the Booking table.

**What it does:** Checks the vehicle's current status. If it's `Maintenance`, it raises an error using `SIGNAL SQLSTATE '45000'` and aborts the INSERT entirely.

**Key concept:** `BEFORE` triggers can cancel the operation. `SIGNAL SQLSTATE` is MySQL's mechanism to throw a custom error.

---

## 5. STORED PROCEDURES

### Procedure 1 — CalculateRentalCharge
```sql
CREATE PROCEDURE CalculateRentalCharge(
    IN  p_rental_id    INT,
    OUT p_total_amount DECIMAL(10,2)
)
BEGIN
    DECLARE v_price_per_day DECIMAL(10,2);
    DECLARE v_days INT;

    -- Get rental price per day for the booked vehicle
    SELECT v.rental_price_per_day INTO v_price_per_day
    FROM Rental r
    JOIN Booking b ON r.booking_id = b.booking_id
    JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
    WHERE r.rental_id = p_rental_id;

    -- Calculate number of rental days (minimum 1 day)
    SELECT GREATEST(DATEDIFF(end_date, start_date), 1) INTO v_days
    FROM Rental WHERE rental_id = p_rental_id;

    -- Compute and store total charge
    SET p_total_amount = v_price_per_day * v_days;

    UPDATE Rental
    SET total_amount = p_total_amount
    WHERE rental_id = p_rental_id;
END;
```

**Parameters:**
- `IN p_rental_id` — the rental record to calculate for
- `OUT p_total_amount` — returns the calculated total

**How to call:**
```sql
SET @total = 0;
CALL CalculateRentalCharge(1, @total);
SELECT @total AS total_amount;
```

**What it does:** Retrieves the vehicle's daily rate, calculates the rental duration using `DATEDIFF`, multiplies them, updates the `Rental` table, and returns the result via the OUT parameter.

---

### Procedure 2 — GetVehicleAvailabilityReport
```sql
CREATE PROCEDURE GetVehicleAvailabilityReport()
BEGIN
    SELECT status, COUNT(*) AS vehicle_count
    FROM Vehicle
    GROUP BY status;
END;
```

**How to call:**
```sql
CALL GetVehicleAvailabilityReport();
```

**What it does:** Returns a summary report showing how many vehicles are in each status (Available / Rented / Maintenance).

---

## 6. SAMPLE DATA (Seed Data)

### Customers
| customer_id | name | phone | license_number |
|---|---|---|---|
| 1 | Rakshitha | 9876543210 | DL-5523910 |
| 2 | John Doe | 9887766554 | DL-8827394 |
| 3 | Alice Smith | 9123456789 | DL-1192834 |
| 4 | Bob Johnson | 9445566778 | DL-4483920 |
| 5 | Carol White | 9556677889 | DL-6672839 |

### Vehicles
| vehicle_id | model | type | price/day | status |
|---|---|---|---|---|
| 1 | Toyota Camry | Sedan | ₹50 | Available |
| 2 | Honda Civic | Sedan | ₹45 | Available |
| 3 | Ford Explorer | SUV | ₹80 | Available |
| 4 | Chevrolet Suburban | SUV | ₹100 | Maintenance |
| 5 | Tesla Model 3 | Sedan | ₹90 | Available |
| 6 | Jeep Wrangler | SUV | ₹85 | Available |
| 7 | Harley Davidson Iron 883 | Motorcycle | ₹40 | Available |
| 8 | BMW 3 Series | Sedan | ₹75 | Available |
| 9 | Ford F-150 | Truck | ₹70 | Available |

### Data Distribution (for queries)
| Vehicle Type | Bookings | Purpose |
|---|---|---|
| Sedan | **16** | Satisfies HAVING > 15 in Query 6 |
| SUV | 4 | Does NOT satisfy HAVING > 15 |
| Truck | 1 | Does NOT satisfy HAVING > 15 |
| Motorcycle | 0 | Demonstrates NOT EXISTS (Query 10) |

---

## 7. WEB APPLICATION

### 7.1 Architecture
```
Browser (HTML/CSS/JS)
        ↕ HTTP REST API
Flask Backend (Python) — app.py
        ↕ mysql-connector-python
MySQL Database — vehicle_rental_db
```

### 7.2 API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/customers` | Fetch all customers |
| POST | `/api/customers` | Add new customer |
| PUT | `/api/customers/<id>` | Update customer |
| DELETE | `/api/customers/<id>` | Delete customer |
| GET | `/api/vehicles` | Fetch all vehicles |
| POST | `/api/vehicles` | Add new vehicle |
| GET | `/api/bookings` | Fetch all bookings |
| POST | `/api/bookings` | Create booking (triggers fire here) |
| GET | `/api/rentals` | Fetch all rentals |
| POST | `/api/procedures/calculate-charge` | Run CalculateRentalCharge |
| GET | `/api/procedures/availability-report` | Run GetVehicleAvailabilityReport |
| POST | `/api/sql/execute` | Execute any SQL query |
| GET/POST | `/api/config` | View/update DB connection settings |

### 7.3 Features
- **Full CRUD** for Customers, Vehicles, Bookings, Maintenance
- **Live SQL Query Runner** — all 10 queries executable from the browser
- **Stored Procedure Executor** — call both procedures from the UI
- **Trigger Demonstration** — booking a vehicle auto-updates its status
- **Maintenance Block** — trying to book a maintenance vehicle shows the trigger error
- **Offline Fallback Mode** — switches to in-memory mock DB if MySQL is unavailable

### 7.4 How to Run
```bash
# 1. Start MySQL and ensure the database is set up
mysql -u root -p < database/schema.sql

# 2. Start the Flask backend
python backend/app.py

# 3. Open the web application
# Navigate to: http://127.0.0.1:5000
```

---

## 8. DBMS CONCEPTS DEMONSTRATED

| Concept | Where Used |
|---|---|
| Primary Key | All 6 tables |
| Foreign Key + CASCADE | Booking, Rental, Payment, Maintenance |
| UNIQUE constraint | Customer.license_number |
| CHECK constraint | Vehicle.status, Maintenance.status |
| INNER JOIN (2-table) | Query 3 |
| INNER JOIN (3-table) | Query 4 |
| GROUP BY | Query 5 |
| HAVING | Query 6 |
| Subquery | Query 7 |
| Correlated Subquery | Query 8 |
| LEFT JOIN | Query 9 |
| NOT EXISTS | Query 10 |
| AFTER Trigger | after_booking_insert |
| BEFORE Trigger + SIGNAL | before_booking_insert |
| Stored Procedure (IN/OUT) | CalculateRentalCharge |
| Stored Procedure (report) | GetVehicleAvailabilityReport |
| DATEDIFF, GREATEST | Inside stored procedure |
| AUTO_INCREMENT | All primary keys |
| DECIMAL | rental_price_per_day, total_amount |

---

## 9. PROJECT FILES

```
DBMS-ad034-project/
│
├── database/
│   ├── schema.sql        ← Table definitions, triggers, procedures, seed data
│   └── queries.sql       ← All 10 SQL queries with comments
│
├── backend/
│   └── app.py            ← Flask REST API (957 lines)
│
├── frontend/
│   ├── index.html        ← Single-page web application
│   ├── style.css         ← Styling
│   └── app.js            ← Frontend JavaScript logic
│
└── README.md             ← Setup instructions
```

---

*Project submitted for DBMS coursework — Roll No: ad034*
