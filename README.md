# LifeIO 🎮

LifeIO is a production-ready, open-source gamified life tracker. Turn your daily habits, work, and study into an RPG experience. Track your activities, level up, monitor your finances, and maintain a healthy sleep cycle—all in a beautiful pixel-art dashboard.

## ✨ Features

- **RPG Progression**: Earn XP for productive activities and level up your character.
- **Skill Bars**: Visualize your progress in different "skills" like Work, Study, Workout, and Cooking.
- **Activity Overlap Management**: Smart logic ensuring only one activity happens at a time.
- **Auto-Stop**: Activities automatically stop at midnight, so you don't have to worry about the clock.
- **Finance Tracking**: Log daily income and expenses with 30-day visual summaries.
- **Sleep Quality**: Log sleep/wake times and track quality with a 5-star rating system.
- **Pixel Aesthetics**: Custom retro-inspired UI for an immersive "Life as a Game" feel.
- **Single-User Admin Mode**: Enforced security for personal use via `ADMIN_EMAIL` restriction.

## 🛠 Tech Stack

- **Backend**: Python (Flask)
- **Database**: Supabase (PostgreSQL with RLS)
- **Frontend**: Vanilla JS, Alpine.js, TailwindCSS
- **Deployment**: Docker, Gunicorn

## 🚀 Quick Start

### 1. Prerequisites
- [Python 3.11+](https://www.python.org/)
- [Supabase Account](https://supabase.com/)
- [Docker](https://www.docker.com/) (Optional, for containerized run)

### 2. Supabase Setup
1. Create a new project in Supabase.
2. Go to the **SQL Editor** and run the contents of `supabase/schema.sql`.
3. Enable **Supabase Auth** and note your Project URL and API Key.

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
ADMIN_EMAIL=your_email@example.com
FLASK_SECRET_KEY=generate_a_random_string
```

### 4. Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```
Visit `http://localhost:5000`.

### 5. Run with Docker
```bash
docker-compose up --build
```
Visit `http://localhost:5000`.

## 📂 Project Structure
```text
lifeio/
├── app/
│   ├── routes/      # Blueprint-based API endpoints
│   ├── static/      # CSS, JS, and Pixel Assets
│   ├── templates/   # Jinja2 HTML templates
│   ├── utils/       # Middleware, Supabase client, XP engine
│   └── app.py       # Application Factory
├── supabase/
│   └── schema.sql   # Database schema & RLS policies
├── Dockerfile       # Container build instructions
└── README.md        # This file
```

## 🌐 Hosting

Since LifeIO is built with Flask and includes a `Dockerfile`, you can host it almost anywhere.

### Recommended Platforms (Cloud)
1. **[Render](https://render.com/) (Easiest)**:
   - Connect your GitHub repository.
   - Select **Web Service**.
   - Render will detect the `Dockerfile` and deploy automatically.
   - Add your `.env` variables in the Render "Environment" tab.

2. **[Railway](https://railway.app/)**:
   - Extremely fast setup for Docker-based apps.
   - Just point it to your repo and it handles the rest.

3. **[Fly.io](https://fly.io/)**:
   - Best for low-latency globally, but requires more CLI setup.

### Database Hosting
- **Supabase** already hosts your database for free in their cloud. You only need to host the Flask backend and point it to your Supabase URL/Key.

## 📜 License
This project is open-source. Feel free to use and modify it for your personal life tracking!
