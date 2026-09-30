# URL Shortener

A simple URL Shortener built using Django and Django REST Framework.

The application converts long URLs into short links using Base62 encoding. It also supports custom aliases, URL expiration, click tracking, analytics, Redis caching, authentication, pagination, rate limiting, and Celery background tasks.

---

## Features

* Shorten long URLs
* Generate short codes using Base62 encoding
* Create custom URL aliases
* Set URL expiration date
* Enable or disable URLs
* Redirect users from short URLs
* Track URL clicks
* Track device and browser information
* Track unique visitors using hashed IP addresses
* View URL analytics
* User authentication
* User-specific URL management
* Redis caching
* API rate limiting
* Pagination
* Celery background task for analytics
* Django admin panel
* Responsive web interface

---

## Technologies Used

* Python
* Django
* Django REST Framework
* SQLite
* Redis
* Celery
* HTML
* CSS
* JavaScript
* User Agents

---

## Project Structure

```text
url_shortener/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── __init__.py
│
├── shortener/
│   ├── migrations/
│   ├── templates/
│   │   └── shortener/
│   │       └── index.html
│   │
│   ├── static/
│   │   └── shortener/
│   │       ├── style.css
│   │       └── script.js
│   │
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## How the Project Works

The basic flow is:

```text
Enter Long URL
       ↓
Validate URL
       ↓
Generate Short Code
       ↓
Save URL in Database
       ↓
Store URL ID in Redis Cache
       ↓
User Opens Short URL
       ↓
Find Original URL
       ↓
Track Click
       ↓
Redirect to Original URL
```

---

## Base62 Encoding

The project uses Base62 encoding to generate short codes.

Base62 uses:

```text
0-9
a-z
A-Z
```

For example:

```text
1  → 1
61 → Z
62 → 10
```

The URL database ID is converted into a Base62 value and used as the short code.

If the user provides a custom alias, the custom alias is used instead.

Example:

```text
Original URL:
https://www.google.com

Short URL:
http://127.0.0.1:8000/6
```

Custom alias example:

```text
Original URL:
https://www.nagpuruniversity.ac.in/

Custom Alias:
rtmnu

Short URL:
http://127.0.0.1:8000/rtmnu
```

---

## Database Models

### URL

Stores the main URL information.

Important fields:

* `original_url`
* `short_code`
* `custom_alias`
* `expires_at`
* `status`
* `created_at`
* `user`

### ClickEvent

Stores information about each click.

It stores:

* URL
* Timestamp
* Referrer
* Device
* Browser
* Country
* Hashed IP address

The IP address is stored as a SHA-256 hash instead of storing the original IP directly.

### Analytics

Stores aggregated analytics information such as:

* Date
* Total clicks
* Unique visitors
* Aggregated metrics

---

## Authentication

The project uses Django's built-in user authentication system.

Only logged-in users can create and manage their URLs.

Users can access:

```text
/api-auth/login/
```

The API also checks URL ownership before allowing users to view, update, or delete their URLs.

---

## API Endpoints

### Create URL

```text
POST /api/urls
```

Example:

```json
{
    "original_url": "https://www.google.com"
}
```

---

### List My URLs

```text
GET /api/urls
```

Returns the URLs created by the logged-in user.

The response uses pagination.

---

### Get URL Details

```text
GET /api/urls/{id}
```

---

### Update URL

```text
PUT /api/urls/{id}
```

---

### Delete URL

```text
DELETE /api/urls/{id}
```

---

### URL Analytics

```text
GET /api/urls/{id}/analytics
```

Returns information such as:

* Total clicks
* Clicks over time
* Unique visitors
* Referrers
* Devices
* Browsers

---

### Redirect

```text
GET /{short_code}
```

Example:

```text
GET /rtmnu
```

The application finds the original URL and redirects the user.

---

## Redis Caching

Redis is used to make URL redirection faster.

When a short URL is requested:

```text
Short Code
    ↓
Check Redis Cache
    ↓
If found → Get URL ID
    ↓
If not found → Get URL from Database
    ↓
Save URL ID in Redis
```

The cache is configured using Redis database 1.

Celery uses Redis database 0 as its message broker.

---

## Celery

Celery is used for background analytics processing.

The analytics task:

```text
update_analytics
```

calculates daily:

* Click count
* Unique visitors

The task is processed by a Celery worker instead of doing all the work during the API request.

---

## Rate Limiting

Django REST Framework throttling is used to limit API requests.

Current limits:

```text
Anonymous users: 10 requests/minute
Authenticated users: 30 requests/minute
```

This helps prevent excessive API requests.

---

## Pagination

The URL list API uses pagination.

Current page size:

```text
10 URLs per page
```

Example:

```text
GET /api/urls
```

The API returns:

```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": []
}
```

---

## Frontend

The project includes a simple responsive frontend.

The frontend provides:

* Dashboard
* Create Short URL form
* Custom alias
* Expiry date
* My URLs section
* Copy short URL
* Responsive layout
* Sidebar navigation

Frontend files:

```text
shortener/templates/shortener/index.html
shortener/static/shortener/style.css
shortener/static/shortener/script.js
```

---

## Admin Panel

Django Admin is used to manage application data.

Open:

```text
http://127.0.0.1:8000/admin/
```

The admin panel provides management for:

* URLs
* Click events
* Analytics

---

## Installation

### 1. Clone the project

```bash
git clone <your-github-repository-url>
```

Go to the project folder:

```bash
cd url_shortener
```

---

### 2. Create virtual environment

```bash
python -m venv my_env
```

Activate it on Windows:

```bash
my_env\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run migrations

```bash
python manage.py migrate
```

---

### 5. Create admin user

```bash
python manage.py createsuperuser
```

Follow the instructions and create a username and password.

---

## Redis Setup

Make sure Redis/Memurai is running.

Test Redis with:

```bash
memurai-cli ping
```

Expected:

```text
PONG
```

---

## Start Celery Worker

Open another terminal and activate the virtual environment.

Then run:

```bash
celery -A config worker --loglevel=info --pool=solo
```

---

## Run Django Server

Open another terminal:

```bash
my_env\Scripts\activate
```

Then:

```bash
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000/
```

---

## Testing

The project includes tests for:

* Base62 encoding
* URL creation
* URL listing
* URL redirection
* Invalid short URLs
* Click tracking

Run tests using:

```bash
python manage.py test shortener
```

Current test result:

```text
Found 9 test(s).

Ran 9 tests

OK
```

---

## Example

### Input

```text
Original URL:
https://www.google.com
```

### Generated Short URL

```text
http://127.0.0.1:8000/6
```

When the user opens the short URL, the application redirects to:

```text
https://www.google.com
```

A click event is also created for analytics.

---

## Security

The project includes:

* Django authentication
* Password hashing through Django
* URL ownership checks
* API rate limiting
* URL validation
* Hashed IP address storage
* Redis caching
* Expiration checking

---

## Future Improvements

Possible future improvements include:

* QR code generation
* Custom domains
* Password-protected links
* Bulk URL creation
* API keys
* Advanced analytics charts
* CSV export
* Monitoring and deployment
