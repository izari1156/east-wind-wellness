## What's inside

- **Flask** (Python web framework) for the website and routes
- **SQLite** (via Python's built-in `sqlite3` module - no extra database
  software to install) for storage
- Plain HTML/CSS templates - no JavaScript build tools, no frontend
  framework, so everything is easy to read and edit

## 1. Requirements

- Python 3.8 or newer (tested with Python 3.8.6)
- pip (comes with Python)

## 2. Setup

Open a terminal in this folder and run:

```bash
# (optional but recommended) create a virtual environment
python3 -m venv venv             
source venv/bin/activate        # on Windows: venv\Scripts\activate

# install the one dependency
pip install -r requirements.txt

# run the website 
python3 app.py 
```

Then proced to open **http://127.0.0.1:5000** in your browser.

The first time run, a file called `instance/east_wind_wellness.db`
is created automatically with some starter data (a demo admin account, a
demo customer account, and the herb/service catalogue). 

## 3. Demo accounts

| Role     | Email                        | Password     |
|----------|-------------------------------|--------------|
| Admin    | admin@eastwindwellness.sg     | admin123     |
| Customer | customer@example.com          | customer123  |

Click **Sign up** to create customer account. New
accounts are always created as regular customers - to make someone an
admin, open `instance/east_wind_wellness.db` with a SQLite browser (e.g.
the free "DB Browser for SQLite" app) and change their `role` column from
`user` to `admin`.

**Please change the demo admin password if intending to show the website to anyone other than teachers
** The app's session secret key now reads from
an environment variable (see the GitHub section below) so you don't have
to edit code for that part.

## 4. What users can do

**Any visitor** can browse Home, Products & Services, About Us and Contact.

**Logged-in customers** can additionally book an appointment and view /
cancel their own appointments under "My Appointments".

**The admin account** gets an "Admin" dashboard where they can:
- see counts of pending/confirmed appointments, customers, etc.
- view every appointment and change its status (pending / confirmed /
  completed / cancelled)
- add, edit or delete items on the Products & Services page (herbs and
  services), including uploading a new picture for each one

## 5. Where to edit things

- **Shop name, address, phone, email, opening hours** - edit the `SHOP`
  dictionary near the top of `app.py`.
- **About Us team members** - edit the `TEAM` list in `app.py`.
- **Herbs / services text and starter photos** - edit `HERBS` and
  `SERVICES` in `db.py` (this is only used the very first time the database
  is created - after that, edit them from the Admin > Manage Products &
  Services page instead).
- **Colours / fonts / layout** - `static/css/style.css`.
- **Page text and structure** - the files in `templates/`.


## 6. About the pictures

Can:
- replace any file in `static/images/` with a real photo of the same name, or
- use the Admin > Manage Products & Services page to upload a new photo for
  any herb or service, or
- add own photos for the About Us team by replacing
  `static/images/team_*.png`.

## 7. About the map on the Contact page

The map on the Contact page is a Google Maps embed that needs an internet
connection to load (it does **not** need a Google API key). If you're
offline it will show a broken image icon.

## 8. Project structure

```
east_wind_wellness/
  app.py                  - all the website routes/logic
  db.py                   - database helper functions + starter data
  schema.sql              - the database table definitions
  requirements.txt        - the one package you need to pip install
  templates/               - HTML pages (Jinja2 templates)
    base.html              - shared header/footer/navigation
    index.html              - Home page
    products_services.html  - Product and Services page
    about.html               - About Us page
    contact.html              - Contact Us page
    login.html / register.html
    book_appointment.html / my_appointments.html
    admin/                   - admin-only pages
  static/
    css/style.css           - all the styling
    images/                 - herb/service/team pictures, logo, banners
  instance/                 - the SQLite database file lives here (created
                               automatically, not included in the download)
```

## 9. Putting this on GitHub

This project is already set up for it - `.gitignore` excludes the database,
`__pycache__`, and any virtual environment folder, and `requirements.txt`
means anyone who clones it can get running with `pip install -r
requirements.txt`.

The one thing to know: `app.py` will use a `FLASK_SECRET_KEY` environment
variable if you set one, and otherwise falls back to a default value so the
app still runs out of the box. That default is fine for a private/class
repo. If your repo will be public, you can set your own before running:

```bash
export FLASK_SECRET_KEY="something-random-and-long"   # on Windows (cmd): set FLASK_SECRET_KEY=something-random-and-long
python3 app.py
```

To actually create the repo:

```bash
cd east_wind_wellness
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

Create the empty repository on GitHub first (don't let GitHub auto-add a
README, .gitignore or license there, since this project already has a
README and .gitignore - ticking those boxes on GitHub would cause a merge
conflict on your first push).

## 10. Common issues

- **"ModuleNotFoundError: No module named 'flask'"** - you forgot to run
  `pip install -r requirements.txt` (or you're not inside the virtual
  environment you created).
- **Port 5000 already in use** - another program is using that port. Stop
  it, or change the last line of `app.py` to `app.run(debug=True, port=5050)`
  and visit http://127.0.0.1:5050 instead.
- **I want to start over with a clean database** - just delete the
  `instance/east_wind_wellness.db` file and restart the app; it will be
  recreated with the starter data.
