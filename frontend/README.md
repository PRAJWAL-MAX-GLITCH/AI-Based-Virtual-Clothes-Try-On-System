# AI-Based Virtual Clothes Try-On System — Frontend

> React + Vite frontend for the AI-powered 2D virtual try-on system.

---

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| Vite | 8 | Build tool + dev server |
| React Router DOM | 6 | Client-side routing |
| Axios | 1.x | HTTP client |
| Lucide React | latest | Icon library |

---

## Getting Started

```bash
# 1. Install dependencies
npm install

# 2. Copy environment file
cp .env.example .env

# 3. Start development server
npm run dev
```

App runs at: **http://localhost:3000**

---

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/                  # Static assets
│   ├── components/
│   │   └── layout/
│   │       ├── Navbar.jsx       # Top navigation bar
│   │       ├── Navbar.css
│   │       ├── Sidebar.jsx      # Left sidebar nav
│   │       └── Sidebar.css
│   ├── context/
│   │   └── AuthContext.jsx      # Global auth state
│   ├── layouts/
│   │   ├── AppLayout.jsx        # Authenticated pages shell
│   │   ├── AppLayout.css
│   │   ├── AuthLayout.jsx       # Login/Register split panel
│   │   └── AuthLayout.css
│   ├── pages/
│   │   ├── LandingPage.jsx      # /        — Public marketing
│   │   ├── LoginPage.jsx        # /login
│   │   ├── RegisterPage.jsx     # /register
│   │   ├── DashboardPage.jsx    # /dashboard
│   │   ├── TryOnPage.jsx        # /try-on
│   │   ├── ClothingPage.jsx     # /clothing
│   │   ├── MyClothingPage.jsx   # /my-clothing
│   │   ├── HistoryPage.jsx      # /history
│   │   ├── ProfilePage.jsx      # /profile
│   │   └── NotFoundPage.jsx     # * (404)
│   ├── services/
│   │   ├── api.js               # Axios instance (centralized)
│   │   └── authService.js       # Auth API stubs
│   ├── utils/
│   │   ├── helpers.js           # Date, string, file URL utils
│   │   └── validators.js        # Form validation helpers
│   ├── App.jsx                  # Root router
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global design system + CSS vars
├── .env                         # VITE_API_BASE_URL (git-ignored)
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

---

## Routes

| Path | Layout | Page |
|---|---|---|
| `/` | None | LandingPage |
| `/login` | AuthLayout | LoginPage |
| `/register` | AuthLayout | RegisterPage |
| `/dashboard` | AppLayout | DashboardPage |
| `/try-on` | AppLayout | TryOnPage |
| `/clothing` | AppLayout | ClothingPage |
| `/my-clothing` | AppLayout | MyClothingPage |
| `/history` | AppLayout | HistoryPage |
| `/profile` | AppLayout | ProfilePage |
| `*` | None | NotFoundPage (404) |

---

## Environment Variables

```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

All API calls use the centralized Axios instance in `src/services/api.js`.

---

## Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start dev server at :3000 |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview production build locally |

---

## Design System

Dark-first UI with CSS custom properties defined in `index.css`:
- **Brand gradient**: `#6475f4 → #a855f7`
- **Dark surfaces**: `#0a0b0f / #10121a / #1a1d2e`
- **Typography**: Inter + Plus Jakarta Sans (Google Fonts)
- **Radius tokens**: `--radius-sm` through `--radius-2xl`
- **Shadow tokens**: `--shadow-sm` through `--shadow-glow`
