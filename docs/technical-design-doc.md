# Technical Design Document (TRD)
## Music Database Platform — MVP Features

**Status:** Draft v0.1 — fully filled in, edit anything you disagree with
**Scope:** Auth, User Profiles, Artist Pages, Album Pages, Song Pages,
Search, Ratings

---

# 1. Authentication

### 1.1 Overview
Users can register, log in, and log out. Sessions are managed via JWT.
Authenticated requests carry a bearer token; unauthenticated requests are
treated as guests with read-only access.

### 1.2 Goals
- User can register with email + password
- User can log in and receive a JWT
- User can log out (client discards token; no server-side blacklist at MVP)
- Protected endpoints reject requests without a valid token

### 1.3 Non-Goals
- No OAuth/social login (Google, GitHub, etc.) at MVP
- No email verification flow at MVP
- No password reset flow at MVP (documented as a known gap, not silently skipped)
- No refresh tokens — a single JWT with a reasonable expiry (e.g. 24h) is enough for MVP

### 1.4 Data Model

New table: `users`

| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| username | string, unique | displayed publicly |
| email | string, unique | used for login |
| password_hash | string | never store plaintext; use bcrypt/argon2 |
| created_at | timestamp | |

### 1.5 API Endpoints

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| POST | `/auth/register` | None | `{ username, email, password }` | `201` + user (no password hash) |
| POST | `/auth/login` | None | `{ email, password }` | `200` + `{ access_token, token_type }` |
| GET | `/auth/me` | Required | — | Current user's own profile data |

Logout is a client-side action (discard the token) — no endpoint is
required for a stateless JWT setup like this.

### 1.6 Business Logic & Edge Cases
- Duplicate email or username on register → `409 Conflict`
- Wrong password on login → `401 Unauthorized` (don't reveal whether the
  email exists — return the same generic error either way, to avoid
  leaking which emails are registered)
- Missing/expired/invalid token on a protected route → `401 Unauthorized`
- Password minimum length (e.g. 8 characters) enforced server-side, not
  just in the frontend form

### 1.7 Dependencies
- Nothing upstream — this is the foundation everything else builds on
- User Profiles, Ratings, Reviews, and Lists all depend on this

### 1.8 Alternatives Considered
- **JWT (chosen)** vs. **server-side sessions with cookies**. JWT was
  chosen because it's stateless (no session store needed) and simpler to
  reason about for a learning project, at the cost of not being able to
  easily "revoke" a token before it expires. For a project this size, that
  trade-off is acceptable.

### 1.9 Open Questions
- None blocking MVP — password reset and email verification are known,
  deliberately deferred gaps, not oversights.

### 1.10 Testing Plan
- Register with valid data → `201`, no password hash in response
- Register with duplicate email → `409`
- Login with correct credentials → `200` + token
- Login with wrong password → `401`
- Access `/auth/me` with no token → `401`
- Access `/auth/me` with valid token → returns correct user

---

# 2. User Profiles

### 2.1 Overview
Every registered user has a public profile page showing their username,
join date, and the ratings they've submitted.

### 2.2 Goals
- Any visitor (guest or logged in) can view a user's public profile
- Profile shows: username, join date, list of ratings given (album/song +
  value)
- A logged-in user can view a slightly more detailed version of their own
  profile (e.g. their email — not shown to other users)

### 2.3 Non-Goals
- No profile editing (avatar upload, bio) at MVP — display-only
- No follow/follower system
- No activity feed beyond the ratings list

### 2.4 Data Model
No new table required — this feature reads from `users` and `ratings`
(joined with `albums`/`songs` for display names). If a bio field is wanted
later, it's a single nullable column added to `users`.

### 2.5 API Endpoints

| Method | Path | Auth | Response |
|---|---|---|---|
| GET | `/users/{username}` | None | Public profile: username, join date, ratings list |
| GET | `/auth/me` | Required | Same as above + email (private view, reuses Auth endpoint) |

### 2.6 Business Logic & Edge Cases
- Requesting a username that doesn't exist → `404 Not Found`
- Ratings list should be paginated (see Search section for the shared
  pagination pattern) — a very active user's ratings list shouldn't return
  unbounded rows in one response

### 2.7 Dependencies
- Requires Auth (users must exist)
- Requires Ratings (to have anything to display)

### 2.8 Alternatives Considered
- Considered a separate `/profiles/{id}` endpoint distinct from
  `/users/{username}`, but merging them keeps the API smaller for MVP scope
  — split later only if profiles grow enough fields to justify it.

### 2.9 Open Questions
- None blocking MVP.

### 2.10 Testing Plan
- View an existing user's profile → correct data, no email exposed
- View a non-existent username → `404`
- View own profile while logged in → email included
- Profile with zero ratings → empty list, not an error

---

# 3. Artist Pages

### 3.1 Overview
Displays an artist's name, bio, image, genres, and full discography
(list of their albums).

### 3.2 Goals
- Any visitor can view an artist's page
- Page shows: name, bio, image, genre tags, list of albums (linked)

### 3.3 Non-Goals
- No "related artists" or "members" (band lineup) at MVP — these require
  additional relationship modeling (artist-to-artist links) that's better
  tackled once the core hierarchy is solid
- No user-editable artist data at MVP (seed data only)

### 3.4 Data Model

New table: `artists`

| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| name | string | |
| bio | text, nullable | |
| image_url | string, nullable | |
| created_at | timestamp | |

New table: `genres`

| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| name | string, unique | e.g. "Rock", "Hip-Hop" |

Join table: `artist_genres` (many-to-many: an artist can have multiple
genres, a genre applies to many artists)

| Column | Type |
|---|---|
| artist_id | FK → artists.id |
| genre_id | FK → genres.id |

*(`genres` and `artist_genres` are shared infrastructure — Album Pages
below reuses the same `genres` table via its own join table.)*

### 3.5 API Endpoints

| Method | Path | Auth | Response |
|---|---|---|---|
| GET | `/artists/{id}` | None | Artist details + genre list + album list |
| GET | `/artists` | None | Paginated list of all artists (for browsing) |

### 3.6 Business Logic & Edge Cases
- Non-existent artist id → `404`
- Artist with no albums yet → return empty discography array, not an error
- `bio`/`image_url` nullable — frontend should handle missing gracefully
  (placeholder image, "No bio available" text)

### 3.7 Dependencies
- Album Pages depend on `artists` existing (an album belongs to an artist)
- Search depends on `artists` for name-based lookup

### 3.8 Alternatives Considered
- Considered storing genre as a plain string column on `artists` instead of
  a separate `genres` table + join table. Rejected because genres need to
  be shared/reused across artists and albums consistently (e.g. filtering
  "all Rock albums" later), which a free-text column can't support cleanly.

### 3.9 Open Questions
- None blocking MVP.

### 3.10 Testing Plan
- Fetch existing artist → correct fields, correct album list
- Fetch non-existent artist → `404`
- Artist with zero albums → empty array, `200` (not an error)

---

# 4. Album Pages

### 4.1 Overview
Displays an album's cover, release date, genres, tracklist, and average
rating.

### 4.2 Goals
- Any visitor can view an album's page
- Page shows: title, cover image, release date, genre tags, artist (linked),
  ordered tracklist, average rating + rating count

### 4.3 Non-Goals
- No reviews displayed here yet (deferred feature)
- No "various artists" / compilation album support at MVP — every album
  has exactly one primary artist for now

### 4.4 Data Model

New table: `albums`

| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| title | string | |
| artist_id | FK → artists.id | |
| release_date | date | |
| cover_url | string, nullable | |
| created_at | timestamp | |

Join table: `album_genres` (same many-to-many pattern as `artist_genres`,
reusing the shared `genres` table from section 3.4)

| Column | Type |
|---|---|
| album_id | FK → albums.id |
| genre_id | FK → genres.id |

Tracklist ordering is handled in the Song Pages section below (a `songs`
row references its `album_id` and a `track_number`).

### 4.5 API Endpoints

| Method | Path | Auth | Response |
|---|---|---|---|
| GET | `/albums/{id}` | None | Album details + genres + artist + ordered tracklist + `average_rating`/`rating_count` |
| GET | `/albums` | None | Paginated list (for browsing) |

### 4.6 Business Logic & Edge Cases
- Non-existent album id → `404`
- Tracklist returned ordered by `track_number` ascending
- `average_rating` is `null` (not `0`) when there are zero ratings — same
  rule as defined in the Ratings design

### 4.7 Dependencies
- Requires Artists (every album has an artist)
- Requires Ratings (to compute average)
- Song Pages depend on Albums existing

### 4.8 Alternatives Considered
- Considered allowing multiple artists per album (many-to-many) to support
  compilations/collaborations from day one. Deferred to keep the schema
  and API simpler for MVP — a single `artist_id` foreign key covers the
  vast majority of albums and can be extended later without breaking
  existing data (existing single-artist albums remain valid).

### 4.9 Open Questions
- None blocking MVP.

### 4.10 Testing Plan
- Fetch existing album → correct fields, tracklist in correct order
- Fetch non-existent album → `404`
- Album with zero ratings → `average_rating: null`, `rating_count: 0`

---

# 5. Song Pages

### 5.1 Overview
Displays a song's title, duration, its album, its artist(s), and its
average rating.

### 5.2 Goals
- Any visitor can view a song's page
- Page shows: title, duration, album (linked), artist (linked), average
  rating + rating count

### 5.3 Non-Goals
- No credits (producer, songwriter, featured artists) at MVP — this needs
  a `people` + `credits` join model that's a reasonable v1.1 addition, not
  worth the complexity before the core hierarchy is proven

### 5.4 Data Model

New table: `songs`

| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| title | string | |
| album_id | FK → albums.id | |
| track_number | integer | position within the album |
| duration_seconds | integer | |
| created_at | timestamp | |

Artist for a song is derived through its album (`song → album → artist`)
rather than duplicated on the `songs` table — avoids data getting out of
sync if it's stored in two places.

### 5.5 API Endpoints

| Method | Path | Auth | Response |
|---|---|---|---|
| GET | `/songs/{id}` | None | Song details + album + artist (via album) + `average_rating`/`rating_count` |

A dedicated `/songs` list endpoint isn't needed at MVP — songs are
primarily discovered through their album's tracklist or via Search.

### 5.6 Business Logic & Edge Cases
- Non-existent song id → `404`
- `duration_seconds` displayed as `mm:ss` on the frontend, stored as a
  plain integer in the database (simplest to sort/compare)
- Same `average_rating: null` vs `0` rule as Albums

### 5.7 Dependencies
- Requires Albums (every song belongs to an album)
- Requires Ratings (to compute average)

### 5.8 Alternatives Considered
- Considered letting a song belong to multiple albums (e.g. also appearing
  on a "Greatest Hits" compilation). Deferred — a song belonging to exactly
  one album is a reasonable MVP simplification; modeling reissues/
  compilations properly is a good post-MVP schema exercise.

### 5.9 Open Questions
- None blocking MVP.

### 5.10 Testing Plan
- Fetch existing song → correct fields, correct album/artist linkage
- Fetch non-existent song → `404`
- Song with zero ratings → `average_rating: null`

---

# 6. Search

### 6.1 Overview
A single search endpoint that looks up artists, albums, and songs by name
and returns matches grouped by type.

### 6.2 Goals
- User (or guest) can search by a text query
- Results include matching artists, albums, and songs (grouped, not one
  flat mixed list)
- Search is case-insensitive and matches partial names

### 6.3 Non-Goals
- No search by user, genre, or label at MVP (per the trimmed MVP scope —
  those were on the original full feature list but are deferred along
  with Lists/Reviews-adjacent discovery features)
- No fuzzy/typo-tolerant search (e.g. no full-text search engine like
  Elasticsearch) — a simple `ILIKE '%query%'` in Postgres is enough at
  MVP scale
- No search result ranking beyond basic relevance (exact prefix match
  first, then contains-match)

### 6.4 Data Model
No new tables. Uses existing `artists`, `albums`, `songs` tables with a
case-insensitive pattern match on their `name`/`title` columns. An index
on these columns (e.g. `CREATE INDEX ... USING gin` with `pg_trgm`, or a
simple B-tree if `ILIKE` prefix-matching is enough) can be added if search
feels slow — not needed for a small seed dataset.

### 6.5 API Endpoints

| Method | Path | Auth | Response |
|---|---|---|---|
| GET | `/search?q={query}` | None | `{ artists: [...], albums: [...], songs: [...] }`, each capped (e.g. top 5 per type) |

### 6.6 Business Logic & Edge Cases
- Empty or missing `q` param → `400 Bad Request`
- No matches in any category → `200` with empty arrays, not an error
- Query is trimmed and lowercased server-side before matching
- Each result includes enough to link directly to the item (id, name/title,
  type) — the frontend shouldn't need a second request just to render a
  result row

### 6.7 Dependencies
- Requires Artists, Albums, and Songs to already exist and be populated

### 6.8 Alternatives Considered
- Considered one combined `/search` returning a single ranked list across
  all types, vs. grouping by type (chosen). Grouping was chosen because
  it's simpler to reason about and display (three short lists) and avoids
  needing a cross-type relevance ranking algorithm, which is unnecessary
  complexity at MVP scale.

### 6.9 Open Questions
- None blocking MVP.

### 6.10 Testing Plan
- Search a term matching an artist, album, and song simultaneously →
  all three appear in their respective groups
- Search a term with no matches → all empty arrays, `200`
- Missing `q` param → `400`
- Search is case-insensitive (e.g. "beatles" matches "The Beatles")

---

# 7. Ratings

*(Carried over from the earlier draft, included here for completeness.)*

### 7.1 Overview
Logged-in users can assign a numeric rating (1–10) to an album or a song.
Each album/song page shows the average rating across all users. A user can
change their own rating, but each user can only have one active rating per
album/song.

### 7.2 Goals
- A logged-in user can submit a rating for an album or song
- A user can update their existing rating (not create duplicates)
- Album/song pages display the current average rating and total number of
  ratings
- Guests cannot rate (read-only access)

### 7.3 Non-Goals
- No written review text (separate, later feature)
- No liking/reacting to other users' ratings
- No rating history/versioning — only the current rating per user is stored

### 7.4 Data Model

New table: `ratings`

| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| user_id | FK → users.id | |
| album_id | FK → albums.id, nullable | set if rating an album |
| song_id | FK → songs.id, nullable | set if rating a song |
| value | integer | 1–10 |
| created_at | timestamp | |
| updated_at | timestamp | |

**Constraints:**
- Exactly one of `album_id`/`song_id` set (via `CHECK` constraint)
- Unique constraint on `(user_id, album_id)` and `(user_id, song_id)` —
  enforces one rating per user per item at the database level

**Derived data:** average rating computed via `SELECT AVG(value)`, not
stored as a manually-synced column.

### 7.5 API Endpoints

| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| POST | `/albums/{id}/ratings` | Required | `{ "value": 8 }` | Created/updated rating + new average |
| POST | `/songs/{id}/ratings` | Required | `{ "value": 7 }` | Created/updated rating + new average |
| GET | `/albums/{id}/ratings/me` | Required | — | Current user's rating, or `404` |

### 7.6 Business Logic & Edge Cases
- Value outside 1–10 → `400`
- Rating a non-existent album/song → `404`
- Guest attempts to rate → `401`
- Rating an already-rated item → upsert (update in place), not duplicate
- Zero ratings → average is `null`, not `0`

### 7.7 Dependencies
- Requires Auth, Albums, Songs

### 7.8 Alternatives Considered
- Single `ratings` table with nullable FKs (chosen) vs. two separate
  `album_ratings`/`song_ratings` tables. Single-table is simpler to query
  across; two-table avoids nullable FKs. Both defensible — kept single-table
  for MVP simplicity.

### 7.9 Open Questions
- Whether to hide averages until a minimum rating count is reached (e.g.
  3+) — a reasonable post-MVP improvement, not required now.

### 7.10 Testing Plan
- Valid rating submission → saved, average updates
- Duplicate rating by same user → updates existing row
- Out-of-range value → `400`
- Rate while logged out → `401`
- Rate non-existent item → `404`
- Zero-rating item → average is `null`

---

# Cross-Feature Notes

- **Genres** are shared infrastructure (section 3.4) reused by both
  Artists and Albums via separate join tables — don't create two separate
  genre tables.
- **Pagination**: any endpoint returning a list (`/artists`, `/albums`,
  Search results, a user's ratings list) should use simple
  `limit`/`offset` query params at MVP — no need for cursor-based
  pagination at this scale.
- **`null` vs `0` for averages** is a rule repeated across Albums, Songs,
  and Ratings — worth extracting into one shared backend helper function
  rather than reimplementing the "no ratings yet" check three times.
