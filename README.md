# RescueBite

RescueBite is a food surplus management app built with Python, Streamlit, and MongoDB Atlas. It models how partner businesses list discounted food packages and manage reservations, stock, and pickups.

I built RescueBite as a NoSQL Databases project for my master's program at the Bucharest University of Economic Studies. The demo uses fictional data and has a Romanian-language interface.

## Features

- Browse food offers by category and publication status.
- Create offers and update discounted prices.
- Reserve packages, cancel reservations, and confirm pickups.
- Update stock and reservation records together using MongoDB transactions.
- Track rescued packages, completed pickups, and revenue by partner through MongoDB aggregation pipelines.

## Screenshots

### Reporting dashboard
<img width="1279" height="581" alt="image" src="https://github.com/user-attachments/assets/82d93a1e-bd1d-45f2-9c0d-53c55ba8c643" />


### Offer catalog
<img width="1279" height="577" alt="image" src="https://github.com/user-attachments/assets/064b364b-1c23-4b76-9581-314d299c90b0" />


## Tech stack

Python · Streamlit · PyMongo · MongoDB Atlas · pandas · JavaScript

## Data model

| Collection | Purpose |
| --- | --- |
| `parteneri` | Partner businesses, addresses, and food categories |
| `pachete` | Offers, package contents, prices, stock, and pickup windows |
| `rezervari` | Reservations, quantities, prices at booking, and pickup status |

The model uses embedded documents for package contents and pickup windows, and references to link partners, offers, and reservations. The `mongodb/` folder contains sample data, CRUD examples, aggregation pipelines, schema validation, and indexes.

## Run locally

You need Python and a MongoDB Atlas cluster. Allow your IP address in Atlas and use a database user with read and write access to the demo database.

1. Clone the repository and enter the project folder.

   ```bash
   git clone https://github.com/IrinaAtodiresei/rescuebite.git
   cd rescuebite
   ```

2. Create a virtual environment and install the dependencies. These commands are for Windows PowerShell.

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

3. Open `.env` locally, set `MONGODB_URI` to your own Atlas connection string, and keep `MONGODB_DB=rescuebite` for the supplied seed script.

4. Connect to your Atlas cluster in a MongoDB client that can run scripts, such as NoSQLBooster. Select the `rescuebite` database and run [`mongodb/01_initializare.js`](mongodb/01_initializare.js) to load the sample data. The other scripts demonstrate database operations. Run the CRUD examples on a demo database because they modify data.

5. Start the app.

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

6. Open [http://localhost:8501](http://localhost:8501).

The seeded pickup windows are fixed dates. To test a new reservation after those windows expire, create an offer with a future pickup window in the **Administrare** tab.
