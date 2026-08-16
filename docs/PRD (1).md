# Product Requirements Document (PRD)

## 1. Project Overview
- **Project Name:** Melodex *(placeholder — rename whenever you like)*
- **Version:** 0.1 (MVP)
- **Authors:** [Your names]
- **Date:** [fill in]
- **Status:** Draft — MVP scope locked, details still evolving

---

## 2. Executive Summary

Melodex is a full-stack music database platform — an "IMDb for Music." Users
browse artists, albums, and songs, and rate them. Unlike Spotify or Apple
Music, there is no playback; the product is about information, ratings, and
discovery, not listening.

It is being built primarily as a learning project by two Computer Engineering
students, to gain real, hands-on experience with backend, frontend,
databases, and deployment.

---

## 3. Problem Statement

Music fans currently split their attention across streaming apps (playback,
but weak/thin metadata and no real rating culture) and niche community sites
like RateYourMusic or Discogs (rich data and ratings, but old UX and closed
platforms). There's no simple, open project combining clean music metadata
with a lightweight rating system — and building one from scratch is also one
of the best ways to learn full-stack engineering, because it naturally
touches relational data modeling, REST APIs, auth, and search.

---

## 4. Vision & Objectives

### Vision
A clean, simple database of artists, albums, and songs that anyone can
browse and rate — small in scope, but built end-to-end by hand.

### Goals
- Ship a working, deployed MVP — not a perfect one
- Learn database design, backend APIs, and frontend integration by doing them
- Keep the first version small enough to actually finish

### Success Criteria
- MVP is deployed and reachable via a public URL
- A seed dataset of at least 50 artists, 100 albums, and 500 songs is loaded
- A friend outside the project can register, rate an album, and build a list
  without being shown how

---

## 5. Target Audience

- **Primary Users:** Music listeners who want to log and rate albums they've
  heard, similar to how people use Letterboxd for films
- **Secondary Users:** The two developers, as the primary consumers of the
  learning outcomes
- **User Personas:** Not needed at MVP stage — the primary/secondary split
  above is enough detail for a project this size

---

## 6. Scope

### In Scope (MVP)
- Artist pages
- Album pages
- Song pages
- Search
- Authentication (register/login/logout)
- User profiles
- Ratings

### Out of Scope (for now)
- Reviews (write/edit/delete/like)
- Lists (curated collections)
- Admin dashboard / moderation tools
- Social features (following users, activity feed, comments)
- Image/file uploads by users (cover art and photos come from the seed
  dataset only, not user-submitted)
- Recommendations of any kind (see Future Scope)

### Future Scope
- Reviews and Lists (planned right after MVP — these were the P2 items)
- Music recommendation algorithms / ML
- Moderator/Admin roles and a moderation dashboard
- Public data submission / editing (wiki-style contributions)

---

## 7. Core Features

### Authentication
- **Description:** Register, log in, log out, JWT-based sessions
- **User Value:** Required before a user can rate anything
- **Priority:** High (P1)

### User Profiles
- **Description:** Username, basic info, list of the user's ratings
- **User Value:** Gives users an identity and a place to see their own activity
- **Priority:** High (P1)

### Artist Pages
- **Description:** Name, bio, image, genres, discography
- **User Value:** Core browsing entity — the starting point for discovery
- **Priority:** Highest (P0)

### Album Pages
- **Description:** Cover, release date, genres, tracklist, average rating
- **User Value:** Core browsing entity, and the main thing users rate
- **Priority:** Highest (P0)

### Song Pages
- **Description:** Title, duration, which album it belongs to, artist(s)
- **User Value:** Completes the artist → album → song hierarchy
- **Priority:** Highest (P0)

### Ratings
- **Description:** Logged-in users rate albums (and songs) on a 1–10 scale
- **User Value:** The core "opinion layer" of the product
- **Priority:** High (P1)

### Search
- **Description:** Search by artist, album, or song name
- **User Value:** Primary way users find things without browsing manually
- **Priority:** Highest (P0)

### Reviews *(deferred)*
- **Description:** Written text reviews attached to a rating
- **User Value:** Adds depth beyond a numeric score
- **Priority:** Low (P2) — build after MVP

### Lists *(deferred)*
- **Description:** User-curated, ordered collections (e.g. "Best Rock
  Albums")
- **User Value:** Lets users express taste beyond individual ratings
- **Priority:** Low (P2) — build after MVP

---

## 8. User Roles

- **Guest:** Can browse and search artists/albums/songs, cannot rate
- **User:** Registered account; can rate albums and songs, has a profile

*(Moderator and Admin roles are deferred — not needed until public
contributions or content moderation are in scope, which is post-MVP.)*

---

## 9. User Flow

Guest
→ Search for an artist
→ View artist page → view album page
→ Register
→ Log in
→ Rate an album
→ View own profile (see rating reflected there)

---

## 10. Functional Overview

At MVP, a user can: create an account, log in, browse artists/albums/songs,
search across all three, and rate albums and songs on a 1–10 scale. Average
ratings are shown on album/song pages. No reviews, lists, or user-generated
content beyond ratings exist yet.

---

## 11. Non-Functional Overview

- **Performance:** Pages should load in well under a second on a small seed
  dataset (this is not a scale problem at MVP size)
- **Security:** Passwords hashed (never stored in plaintext), JWT auth,
  standard input validation against SQL injection/XSS
- **Scalability:** Not a concern at MVP — a single small Postgres instance is
  more than enough
- **Accessibility:** Basic semantic HTML and reasonable color contrast; a
  full accessibility audit is not an MVP requirement
- **Reliability:** No formal uptime target — this is a learning project, not
  a production service with SLAs

---

## 12. Assumptions & Constraints

**Assumptions**
- Music metadata (artists, albums, songs, cover art) will be seeded manually
  or scraped/imported once, not submitted by users at MVP stage
- Two-person team, no fixed external deadline

**Constraints**
- Stack: React (JS) frontend, FastAPI backend, PostgreSQL + SQLAlchemy,
  JWT auth, Docker for deployment
- No dedicated design, QA, or DevOps roles — both of you do all of it

**Risks**
- Feature creep back toward reviews/lists before ratings even work — resist
  this, MVP scope is locked above
- Sourcing/seeding a real dataset of artists/albums/songs takes real time;
  treat it as its own task, not an afterthought

---

## 13. Roadmap

**Version 1 (MVP)**
Auth, user profiles, artist/album/song pages, search, ratings

**Version 2**
Reviews, Lists

**Version 3**
Public contributions/editing, richer discovery (browse by genre/label),
possibly moderator role if V3 opens up public edits

**Future Ideas**
Recommendation algorithms / ML-based suggestions

---

## 14. Open Questions

- Where does seed data come from — manual entry, a public music API, or a
  scrape? (Needed before backend work can be tested with real data.)
- Should the 1–10 rating scale allow half-points, or integers only?

*(Everything else that would normally sit here — target audience detail,
scope boundaries, MVP feature list — has already been decided above.)*

---

## 15. Appendix

- **References:** RateYourMusic, Discogs, Letterboxd (as UX/data-model
  inspiration, not code or content sources)
- **Glossary:** *(add terms as they come up — not needed yet at this scope)*
