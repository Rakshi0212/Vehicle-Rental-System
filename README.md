# Vehicle Rental System (DBMS Project - ad034)

A comprehensive relational database implementation and management console for a **Vehicle Rental System**. This project details the design of SQL schemas, transactional triggers, stored procedures, core SQL optimization queries, a Python Flask REST API backend, and a premium glassmorphic frontend control panel dashboard.

## Database Design (Schema)

The database consists of 6 tables with proper constraints, indices, and references:

1. **Customer**: Holds customer accounts, contact details, and driving license numbers.
2. **Vehicle**: Inventory registry containing models, categories (Sedan, SUV, Truck, Motorcycle), rates, and status.
3. **Booking**: Manages rental bookings linking customers to vehicles.
4. **Rental**: Calculates check-out and check-in times and tracking aggregate prices.
5. **Payment**: Manages customer billing transaction records.
6. **Maintenance**: Tracks vehicles in repair shops and blocks them from bookings.

## Core Implementations

### Triggers
1. `after_booking_insert`: Automatically updates vehicle status to `'Rented'` when booked.
2. `before_booking_insert`: Aborts booking attempts if the target vehicle's status is `'Maintenance'`, using `SIGNAL SQLSTATE`.

### Stored Procedures
1. `CalculateRentalCharge`: Computes total billing amount based on daily price and duration, updating the `Rental` record.
2. `GetVehicleAvailabilityReport`: Returns summary aggregates of fleet count grouped by vehicle status.

### 10 Project Queries
1. **Retrieve all vehicles**
2. **Display available vehicles**
3. **Display rental & customer details** (2-table Join)
4. **Display rental, customer, & vehicle details** (3-table Join)
5. **Count rentals per vehicle type** (Group By)
6. **Display vehicle types with > 15 rentals** (Having)
7. **Retrieve vehicles priced above average** (Subquery)
8. **Retrieve customers who booked more than Customer 2** (Correlated Subquery)
9. **Display all vehicles including unbooked** (Left Join)
10. **Retrieve vehicles never booked** (Not Exists)

---

## Getting Started

Refer to [instructions.md](instructions.md) for full commands on Git setup, CMD logins, database seeding, and application launch.

### Quick Start
1. Create the database in MySQL:
   ```sql
   SOURCE database/schema.sql;
   ```
2. Run the application:
   ```bash
   python backend/app.py
   ```
3. Open `http://127.0.0.1:5000/` in your browser.
