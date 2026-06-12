# 🚗 Vehicle Rental Management System

An all-in-one digital platform for managing vehicle rentals. Think of it as a virtual garage and reservation desk combined! It helps rental businesses track customers, manage their fleet of vehicles, handle bookings, process payments, and track vehicle maintenance.

This project includes a **secure relational database (MySQL)**, a **smart automation layer (Triggers & Stored Procedures)**, a **Flask REST API (Backend)**, and an **interactive, modern Dashboard (Frontend)**.

---

## 🌟 How It Works (For Everyone)

To make it easy to understand, here is how the system handles the typical journey of a customer and a vehicle.

### 1. The Customer's Journey (Step-by-Step)
This flowchart shows exactly what happens from the moment a customer opens the app to rent a vehicle until they return it and complete their payment:

```mermaid
flowchart TD
    Start([1. Customer visits the app]) --> Browse[2. Browse the Fleet Registry]
    Browse --> Select{3. Choose a Vehicle}
    
    Select -->|Vehicle is Available| Book[4. Place a Booking]
    Select -->|Vehicle is in Maintenance| Blocked[4. Booking Blocked!<br>Database trigger prevents booking a car in repair]
    
    Book --> Lock[5. Vehicle Locked<br>Database trigger instantly changes status to 'Rented']
    Lock --> Drive[6. Customer drives and uses the vehicle]
    
    Drive --> Return[7. Customer returns the vehicle]
    Return --> Calc[8. Calculate Bill<br>Stored procedure multiplies daily rate by total days]
    
    Calc --> Pay[9. Process Payment]
    Pay --> Complete([10. Rental Completed!<br>Vehicle returned to 'Available' status])
    
    Blocked --> GoBack[Go back to browse other vehicles]
    GoBack --> Browse
```

---

### 2. The Vehicle Life Cycle (Status Transitions)
Vehicles are the core of our business. To ensure we never rent out a car that is currently in use or undergoing maintenance, the database automatically tracks and restricts a vehicle's status using this life cycle:

```mermaid
stateDiagram-v2
    [*] --> Available : New vehicle added to the fleet
    
    Available --> Rented : Customer books the vehicle<br>(Auto-triggered by Booking)
    Rented --> Available : Vehicle returned in clean, working condition
    
    Rented --> Maintenance : Vehicle returned with damage or needs service
    Available --> Maintenance : Scheduled routine inspection / repairs
    
    Maintenance --> Available : Repairs completed by mechanic<br>(Vehicle status updated to Available)
```

---

### 3. Behind the Scenes (System Architecture)
When you click a button on the screen, here is how the different parts of our application talk to each other:

```mermaid
graph TD
    User([You / The Operator]) <--> UI[1. Interactive Frontend Dashboard<br>Modern, clean screen with tabs and forms]
    UI <-->|2. JSON API Request| Server[2. Python Flask Server<br>The 'Brain' that coordinates data flow]
    Server <-->|3. Database Commands| DB[(3. MySQL Database Server<br>The 'Filing Cabinet' storing all information)]
    
    Server -.->|Connection Fails?| MockDB[(In-Memory Simulated Database<br>Allows the app to run offline for demonstrations)]
```

---

## 📊 Database Schema Design (The Structure)

Our database is designed using 6 separate tables, linked together securely. This layout ensures zero duplicated data and guarantees that if a customer or vehicle is deleted, their corresponding booking histories are cleaned up safely.

```mermaid
erDiagram
    CUSTOMER {
        int customer_id PK "Unique Customer ID"
        varchar name "Full Name"
        varchar phone "Contact Number"
        varchar license_number UK "Driving License Number"
    }
    VEHICLE {
        int vehicle_id PK "Unique Vehicle ID"
        varchar model "e.g., Tesla Model 3"
        varchar type "Sedan, SUV, Truck, Motorcycle"
        decimal rental_price_per_day "Daily Rate ($)"
        varchar status "Available, Rented, Maintenance"
    }
    BOOKING {
        int booking_id PK "Unique Booking ID"
        int customer_id FK "Links to Customer"
        int vehicle_id FK "Links to Vehicle"
        date booking_date "Reservation Date"
    }
    RENTAL {
        int rental_id PK "Unique Rental Agreement ID"
        int booking_id FK "Links to Booking"
        date start_date "Trip Start Date"
        date end_date "Trip End Date"
        decimal total_amount "Total Billed Cost"
    }
    PAYMENT {
        int payment_id PK "Unique Receipt ID"
        int rental_id FK "Links to Rental Invoice"
        decimal amount "Amount Paid ($)"
        date payment_date "Payment Date"
    }
    MAINTENANCE {
        int maintenance_id PK "Unique Service Ticket ID"
        int vehicle_id FK "Links to Vehicle"
        varchar description "Details of Repair / Inspection"
        date maintenance_date "Service Date"
        varchar status "Active or Completed"
    }

    CUSTOMER ||--o{ BOOKING : "places"
    VEHICLE ||--o{ BOOKING : "is selected in"
    BOOKING ||--|| RENTAL : "generates"
    RENTAL ||--o{ PAYMENT : "has"
    VEHICLE ||--o{ MAINTENANCE : "undergoes"
```

---

## ⚙️ Smart Database Automation

We use database-level automation to enforce rules and calculate prices. This means the rules are enforced directly by the database itself, making the system highly reliable and secure.

### 🛡️ 1. Database Triggers (Automatic Rules)
* **Rule 1: Prevent Renting Damaged Cars (`before_booking_insert`)**  
  If an operator attempts to book a vehicle whose status is currently `'Maintenance'`, the database will block the transaction immediately and display a friendly warning: *“Error: Cannot book this vehicle because it is currently under maintenance!”*
* **Rule 2: Auto-Rent Vehicles (`after_booking_insert`)**  
  As soon as a valid booking is inserted, the database automatically updates that vehicle’s status to `'Rented'`, preventing anybody else from booking it at the same time.

### 🧮 2. Stored Procedures (Pre-written Calculations)
* **`CalculateRentalCharge`**:  
  Calculates a rental agreement's final bill dynamically:  
  $$\text{Total Charge} = \text{Rental Duration (in Days)} \times \text{Daily Rate of the Vehicle}$$  
  It then updates the `Rental` invoice amount automatically.
* **`GetVehicleAvailabilityReport`**:  
  Aggregates counts of all vehicles in our fleet by their status (`Available`, `Rented`, `Maintenance`), feeding live charts on the dashboard.

---

## 🔍 Predefined Analysis Queries

The system has 10 built-in analytical queries that answer important business questions:

| Query # | Question Answered | SQL Implementation |
| :---: | :--- | :--- |
| **1** | What vehicles do we own? | `SELECT * FROM Vehicle;` |
| **2** | Which vehicles are ready to rent right now? | `SELECT * FROM Vehicle WHERE status = 'Available';` |
| **3** | Who rented what, and when? (2-Table Join) | Combines `Rental` and `Customer` details. |
| **4** | Can we get a complete history of customer details, vehicles, and charges? (3-Table Join) | Joins `Rental`, `Customer`, and `Vehicle` tables. |
| **5** | Which types of vehicles (Sedans, SUVs, etc.) are rented most? | `GROUP BY v.type` to count total rentals per vehicle type. |
| **6** | Which vehicle types have high demand (>15 rentals)? | Groups by type and filters using `HAVING COUNT(r.rental_id) > 15`. |
| **7** | Which vehicles cost more than our average fleet rental price? | Subquery: compares rates against `(SELECT AVG(price) FROM Vehicle)`. |
| **8** | Which power-users have booked more vehicles than Customer ID 2? | Correlated Subquery: compares customer booking counts. |
| **9** | List all vehicles, showing booking details even if they have never been rented. | `LEFT JOIN` on vehicle bookings. |
| **10** | Which vehicles are inactive/idle and have never been rented? | `NOT EXISTS` query to identify vehicles with zero booking history. |

---

## 🎨 Interactive Features in the Dashboard

Our management dashboard is packed with features designed to make administration effortless:

1. **Live Analytics Dashboard**: Look at current stats (total customers, bookings, active fleet count) and a beautiful chart of your vehicle distribution.
2. **Interactive Workbench**: Run any of the 10 built-in SQL analysis queries with one click and see the results instantly formatted as a table.
3. **Database Configuration Panel**: Click the settings slider in the sidebar to change the MySQL database username, password, hostname, or port dynamically without restarting the server!

---

## 🚀 Setup & Installation (Technical)

### Prerequisites
* **Python 3.x** installed.
* **MySQL 8.x** server running locally.

### Step 1: Set Up MySQL Schema & Seeding
Open your Command Prompt (CMD) or MySQL Workbench and execute:
```sql
CREATE DATABASE vehicle_rental_db;
USE vehicle_rental_db;
SOURCE C:/Users/Rakshitha/.gemini/antigravity-ide/scratch/DBMS-ad034-project/database/schema.sql;
```

### Step 2: Run the Application Server
Run the following commands in your terminal to install dependencies and run the server:
```bash
pip install flask mysql-connector-python
python backend/app.py
```

### Step 3: Open the Management App
Open your web browser and navigate to:  
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**
