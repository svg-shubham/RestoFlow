# 🍽️ RestoFlow - Real-Time Restaurant Management & POS System

**RestoFlow** is a comprehensive Full-Stack ERP solution designed for modern restaurants to streamline the journey from **Order Placement** to **Final Payment Settlement**. 

It focuses on high coordination between the Manager, Kitchen, and Cashier using real-time communication patterns.

---

## 🚀 Key Problem-Solving Features

### 🔔 Real-Time Billing Coordination (The 'Cashier Popup')
Implemented a non-blocking **AJAX Polling System** that monitors the database every 5 seconds. When a manager requests a bill, the Cashier receives an instant visual and audio notification without refreshing the page.

### 💰 Financial Precision
Used Python’s `Decimal` library instead of `float` to handle currency calculations, ensuring 100% accuracy in GST and Subtotal calculations—a critical requirement for fintech/POS software.

### 👨‍🍳 Role-Based Orchestration
- **Manager Dashboard:** Interactive Floor Plan to manage table occupancy and KOT (Kitchen Order Ticket) generation.
- **Kitchen Display System (KDS):** Live feed for chefs to track pending orders and mark them as 'Served'.
- **Cashier Desk:** Advanced search functionality and automated invoice generation with multi-mode payment support (UPI, Cash, Card).

---

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Django 5.x
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Database:** PostgreSQL (Production) / SQLite (Dev)
- **Architecture:** Monolithic with AJAX-based asynchronous components

---

## 📸 System Workflow



1. **Ordering:** Manager assigns a table and adds menu items.
2. **KOT:** Items are sent to the Kitchen view instantly.
3. **Billing Request:** Once the guest finishes, the Manager triggers a "Bill Request".
4. **Checkout:** Cashier sees a **Red Alert Popup**, generates a tax-compliant invoice, and clears the table for the next guest.

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/RestoFlow.git](https://github.com/yourusername/RestoFlow.git)
   cd RestoFlow
Setup Virtual Environment:

Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:

Bash

pip install -r requirements.txt
Run Migrations & Start Server:

Bash

python manage.py migrate
python manage.py runserver
📈 Future Roadmap
[ ] Integration with Thermal Printers (via ESC/POS).

[ ] Daily/Monthly Analytics Dashboard using Chart.js.

[ ] QR-Code based self-ordering for customers.
