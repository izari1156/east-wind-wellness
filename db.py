import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "east_wind_wellness.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_connection():
    """Open a fresh connection to the SQLite database file."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          #lets us access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """(Re)create all tables from schema.sql. Wipes existing data!"""
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def database_exists():
    return os.path.exists(DB_PATH)



#Starter data so the site is never empty on first run. Default testers etc

DEFAULT_ADMIN = {
    "full_name": "Shop Administrator",
    "email": "admin@eastwindwellness.sg",
    "phone": "6420 6767",
    "password": "admin123",   #default password, to be change after login in as admin.
}

DEFAULT_USER = {
    "full_name": "Demo Customer",
    "email": "customer@example.com",
    "phone": "9123 4567",
    "password": "customer123",
}

HERBS = [
    {
        "name": "Korean Ginseng 人参",
        "tagline": "Restores energy and vitality",
        "description": (
            "Lorem ipsum dolor sit amet - our ginseng root is prized for "
            "supporting energy levels and overall qi. Traditionally taken "
            "as a tea or added to double-boiled soups. Please replace this "
            "text with your own product details."
        ),
        "image_file": "herb_ginseng.png",
    },
    {
        "name": "Goji Berry 果杞",
        "tagline": "Nourishes the liver and eyes",
        "description": (
            "Lorem ipsum dolor sit amet - sweet, sun-dried goji berries "
            "commonly brewed into teas or soups, said to support eye "
            "health and the liver meridian. Replace with your own copy."
        ),
        "image_file": "herb_goji.png",
    },
    {
        "name": "Cordyceps 螬草",
        "tagline": "Supports the lungs and kidneys",
        "description": (
            "Lorem ipsum dolor sit amet - a prized tonic herb traditionally "
            "used to support respiratory health and stamina. Placeholder "
            "description, feel free to edit in the admin dashboard."
        ),
        "image_file": "herb_cordyceps.png",
    },
    {
        "name": "Bird's Nest 燕窝",
        "tagline": "Nourishes skin and complexion",
        "description": (
            "Lorem ipsum dolor sit amet - double-boiled bird's nest is a "
            "classic tonic said to nourish the skin and complexion. "
            "Placeholder text - update with your own sourcing details."
        ),
        "image_file": "herb_birdsnest.png",
    },
    {
        "name": "Astragalus Root 黄芪",
        "tagline": "Strengthens the body's defences",
        "description": (
            "Lorem ipsum dolor sit amet - sliced astragalus root is often "
            "added to soups to help support the immune system. "
            "Placeholder description text."
        ),
        "image_file": "herb_astragalus.png",
    },
    {
        "name": "Chrysanthemum Flower 菊花",
        "tagline": "Cooling and calming tea",
        "description": (
            "Lorem ipsum dolor sit amet - dried chrysanthemum flowers "
            "make a light, cooling tea that is popular in warm weather. "
            "Placeholder description text."
        ),
        "image_file": "herb_chrysanthemum.png",
    },
]

SERVICES = [
    {
        "name": "Acupuncture 针灸",
        "tagline": "Fine needles to relieve pain & tension",
        "description": (
            "Lorem ipsum dolor sit amet - our physicians use traditional "
            "acupuncture to help with pain management and general "
            "wellness. Replace this placeholder with your real service "
            "details."
        ),
        "image_file": "service_acupuncture.png",
    },
    {
        "name": "Tui Na Massage 推拿",
        "tagline": "Therapeutic Chinese massage",
        "description": (
            "Lorem ipsum dolor sit amet - a hands-on therapy that combines "
            "massage and acupressure to ease muscle tension. Placeholder "
            "description - edit any time from the admin dashboard."
        ),
        "image_file": "service_tuina.png",
    },
    {
        "name": "Cupping Therapy 拔罐",
        "tagline": "Improves circulation & relieves tightness",
        "description": (
            "Lorem ipsum dolor sit amet - suction cups are placed on the "
            "skin to help improve blood flow and ease muscle tightness. "
            "Placeholder description text."
        ),
        "image_file": "service_cupping.png",
    },
    {
        "name": "Herbal Consultation 看诊",
        "tagline": "Personalised diagnosis & herbal prescription",
        "description": (
            "Lorem ipsum dolor sit amet - meet one of our physicians for a "
            "full consultation and a herbal prescription tailored to you. "
            "Placeholder description text."
        ),
        "image_file": "service_consultation.png",
    },
    {
        "name": "Moxibustion 艾灸",
        "tagline": "Gentle heat therapy",
        "description": (
            "Lorem ipsum dolor sit amet - burning moxa near the skin to "
            "warm and invigorate the flow of qi. Placeholder description "
            "text, please replace."
        ),
        "image_file": "service_moxibustion.png",
    },
]


def seed_if_empty():
    """Insert a default admin/user account and starter catalogue once."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS n FROM users")
    if cur.fetchone()["n"] == 0:
        cur.execute(
            "INSERT INTO users (full_name, email, phone, password_hash, role) "
            "VALUES (?, ?, ?, ?, 'admin')",
            (
                DEFAULT_ADMIN["full_name"],
                DEFAULT_ADMIN["email"],
                DEFAULT_ADMIN["phone"],
                generate_password_hash(DEFAULT_ADMIN["password"]),
            ),
        )
        cur.execute(
            "INSERT INTO users (full_name, email, phone, password_hash, role) "
            "VALUES (?, ?, ?, ?, 'user')",
            (
                DEFAULT_USER["full_name"],
                DEFAULT_USER["email"],
                DEFAULT_USER["phone"],
                generate_password_hash(DEFAULT_USER["password"]),
            ),
        )

    cur.execute("SELECT COUNT(*) AS n FROM items")
    if cur.fetchone()["n"] == 0:
        for herb in HERBS:
            cur.execute(
                "INSERT INTO items (category, name, tagline, description, image_file) "
                "VALUES ('herb', ?, ?, ?, ?)",
                (herb["name"], herb["tagline"], herb["description"], herb["image_file"]),
            )
        for svc in SERVICES:
            cur.execute(
                "INSERT INTO items (category, name, tagline, description, image_file) "
                "VALUES ('service', ?, ?, ?, ?)",
                (svc["name"], svc["tagline"], svc["description"], svc["image_file"]),
            )

    conn.commit()
    conn.close()
