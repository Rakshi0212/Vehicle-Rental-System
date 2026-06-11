# Detailed Guide: Database Setup, Frontend Application, and GitHub Push
### Project Repository: DBMS-ad034-project

Follow this step-by-step guide to run the **Vehicle Rental System** database in your Command Prompt (CMD), execute the Flask API backend, and push all files to your GitHub repository `DBMS-ad034-project`.

---

## Part 1: Initializing and Pushing to GitHub

Since you have created the repository `DBMS-ad034-project` on GitHub, follow these commands in CMD to initialize Git locally, commit all our files, and push them to your repository:

### Step 1: Open Command Prompt (CMD) in the project folder
1. Open Command Prompt on your computer.
2. Navigate to the project folder by running:
   ```cmd
   cd "C:\Users\Rakshitha\.gemini\antigravity-ide\scratch\DBMS-ad034-project"
   ```

### Step 2: Initialize Git and Link GitHub
Run the following commands one by one:
```cmd
-- Initialize local git repository
git init

-- Stage all files we created
git add .

-- Commit the files
git commit -m "Initial commit - Vehicle Rental System Database and Frontend App"

-- Set the default branch name to main
git branch -M main

-- Link your remote GitHub repository (Replace USERNAME with your actual GitHub username)
git remote add origin https://github.com/USERNAME/DBMS-ad034-project.git

-- Push the files to GitHub (You may be prompted to log in/authenticate)
git push -u origin main
```

---

## Part 2: Database Setup & CMD Implementation (MySQL)

We will execute the SQL scripts using the MySQL command-line client.

### Step 1: Log in to MySQL via CMD
Open a fresh Command Prompt window and log in to your MySQL server:
```cmd
mysql -u root -p
```
*Note: Press Enter, then type your MySQL root password and press Enter.*

### Step 2: Run the Setup Script
Once logged in to the MySQL terminal (`mysql>`), run the following SQL command to execute the entire schema (tables, triggers, procedures, and seed data) from the file we created:
```sql
SOURCE C:/Users/Rakshitha/.gemini/antigravity-ide/scratch/DBMS-ad034-project/database/schema.sql;
```
*You will see multiple "Query OK" messages, indicating that all tables, 2 triggers, 2 procedures, and 21 seed records were created successfully!*

### Step 3: Run the 10 Queries inside CMD
You can copy and run these queries in your MySQL CMD prompt to verify the database:

1. **Retrieve all vehicles:**
   ```sql
   SELECT * FROM Vehicle;
   ```
2. **Display vehicles available for rent:**
   ```sql
   SELECT * FROM Vehicle WHERE status = 'Available';
   ```
3. **Display rental and customer details (2-table INNER JOIN):**
   ```sql
   SELECT r.rental_id, c.name AS customer_name, c.phone, r.start_date, r.end_date, r.total_amount 
   FROM Rental r 
   INNER JOIN Booking b ON r.booking_id = b.booking_id 
   INNER JOIN Customer c ON b.customer_id = c.customer_id;
   ```
4. **Display rental, customer, and vehicle details (3-table JOIN):**
   ```sql
   SELECT r.rental_id, c.name AS customer_name, v.model AS vehicle_model, v.type AS vehicle_type, r.start_date, r.end_date, r.total_amount 
   FROM Rental r 
   INNER JOIN Booking b ON r.booking_id = b.booking_id 
   INNER JOIN Customer c ON b.customer_id = c.customer_id 
   INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id;
   ```
5. **Count number of rentals per vehicle type (GROUP BY):**
   ```sql
   SELECT v.type AS vehicle_type, COUNT(r.rental_id) AS total_rentals 
   FROM Rental r 
   INNER JOIN Booking b ON r.booking_id = b.booking_id 
   INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id 
   GROUP BY v.type;
   ```
6. **Display vehicle types having more than 15 rentals (HAVING):**
   ```sql
   SELECT v.type AS vehicle_type, COUNT(r.rental_id) AS total_rentals 
   FROM Rental r 
   INNER JOIN Booking b ON r.booking_id = b.booking_id 
   INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id 
   GROUP BY v.type 
   HAVING COUNT(r.rental_id) > 15;
   ```
7. **Retrieve vehicles whose rental charge is greater than the average rental charge (Subquery):**
   ```sql
   SELECT * FROM Vehicle 
   WHERE rental_price_per_day > (SELECT AVG(rental_price_per_day) FROM Vehicle);
   ```
8. **Retrieve customers who rented more vehicles than customer 2 (Correlated Subquery):**
   ```sql
   SELECT c1.customer_id, c1.name, (SELECT COUNT(*) FROM Booking b1 WHERE b1.customer_id = c1.customer_id) AS booking_count 
   FROM Customer c1 
   WHERE (SELECT COUNT(*) FROM Booking b1 WHERE b1.customer_id = c1.customer_id) > (SELECT COUNT(*) FROM Booking b2 WHERE b2.customer_id = 2);
   ```
9. **Display all vehicles including those not rented (LEFT JOIN):**
   ```sql
   SELECT v.vehicle_id, v.model, v.type, v.status, b.booking_id, b.booking_date 
   FROM Vehicle v 
   LEFT JOIN Booking b ON v.vehicle_id = b.vehicle_id;
   ```
10. **Retrieve vehicles that were never rented (NOT EXISTS):**
    ```sql
    SELECT * FROM Vehicle v 
    WHERE NOT EXISTS (SELECT 1 FROM Booking b WHERE b.vehicle_id = v.vehicle_id);
    ```

---

## Part 3: Running the Frontend Application

The frontend connects directly to your local MySQL database. If the connection fails (e.g. if database is offline or credentials differ), it will run in a **Simulated/Mock Database mode** automatically so you can immediately view and demonstrate the system without getting connection errors.

### Step 1: Open CMD in the project folder
```cmd
cd "C:\Users\Rakshitha\.gemini\antigravity-ide\scratch\DBMS-ad034-project"
```

### Step 2: Start the Backend Server
Run the Flask server:
```cmd
python backend/app.py
```
*You will see the message:*
`🚀 Flask backend server running on http://127.0.0.1:5000`

### Step 3: Access in the Browser
Open your browser and navigate to:
```url
http://127.0.0.1:5000/
```

---

## Part 4: Exploring Features in the Dashboard

1. **Dashboard Tab**: Displays database stats (total customers, fleet size, bookings) and the **Vehicle Status Distribution** bar graph generated using the `GetVehicleAvailabilityReport` Stored Procedure.
2. **Customers Tab**: Displays all customer records. Includes forms to **Insert** new customers, **Update** details, and **Delete** records.
3. **Vehicles Tab**: Displays the fleet records. Allows CRUD management (Insert, Update, Delete).
4. **Bookings & Rentals Tab**: 
   - **Insert Booking**: Place bookings using the form.
   - **Trigger Test**: Try booking "Chevrolet Suburban" (status: Maintenance). The system will alert you that the transaction is rejected by the database trigger constraint!
   - **Auto-Rent**: Placing a valid booking triggers the database update, automatically changing the vehicle status to "Rented" and creating a Rental entry.
5. **SQL Workbench Tab**: Select any of the 10 project queries, preview the SQL syntax in the terminal editor, click **Run Query**, and see the live data results displayed in a dynamically generated layout.
6. **Procedures Tab**:
   - **CalculateRentalCharge**: Select a rental, click Execute, and the procedure computes the price based on days rented and updates the total amount.
   - **GetVehicleAvailabilityReport**: Click to run the procedure and see current counts.
7. **Database Configurations (Slider Icon in Sidebar)**: Open the slider to dynamically change MySQL hostname, user, password, and port to establish a live connection instantly.
