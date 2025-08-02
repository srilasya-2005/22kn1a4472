# URL Shortener Backend

A robust Flask-based URL shortening service with comprehensive logging, analytics, and MongoDB integration. This backend provides RESTful APIs for creating short URLs, tracking usage statistics, and managing URL validity periods.

## 🚀 Features

- **URL Shortening**: Convert long URLs to short, manageable codes
- **Custom Short Codes**: Support for custom short codes (optional)
- **URL Validation**: Automatic validation of input URLs
- **Expiration Management**: Set custom expiration times for URLs
- **Analytics & Statistics**: Track URL usage and access statistics
- **Comprehensive Logging**: Integrated logging system with evaluation service
- **Health Monitoring**: Built-in health check endpoint
- **CORS Support**: Cross-origin resource sharing enabled
- **MongoDB Integration**: Persistent storage with indexing
- **Background Tasks**: Automatic cleanup of expired URLs

## 🛠️ Tech Stack

- **Framework**: Flask 2.0.3
- **Database**: MongoDB with PyMongo
- **URL Validation**: Validators library
- **CORS**: Flask-CORS
- **Environment**: Python-dotenv
- **Scheduling**: APScheduler for background tasks
- **Logging**: Custom logging middleware with external service integration

## 📋 Prerequisites

- Python 3.7+
- MongoDB instance (local or cloud)
- Internet connection for external logging service

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the backend directory with the following variables:

```env
MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here
```

### 4. Database Setup
Ensure MongoDB is running and accessible. The application will automatically create the necessary collections and indexes.

### 5. Run the Application
```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Create Short URL
**POST** `/api/shorten`

Creates a shortened URL from a long URL.

**Request Body:**
```json
{
    "url": "https://example.com/very-long-url",
    "validity": 24,
    "custom_code": "optional-custom-code"
}
```

**Response:**
```json
{
    "short_code": "abc123",
    "original_url": "https://example.com/very-long-url",
    "short_url": "http://localhost:5000/abc123",
    "expires_at": "2024-01-01T12:00:00Z"
}
```

#### 2. Redirect to Original URL
**GET** `/{short_code}`

Redirects to the original URL using the short code.

#### 3. Get Original URL Info
**GET** `/api/url/{short_code}`

Returns information about a shortened URL.

**Response:**
```json
{
    "original_url": "https://example.com/very-long-url",
    "short_code": "abc123",
    "created_at": "2024-01-01T10:00:00Z",
    "expires_at": "2024-01-01T12:00:00Z",
    "is_expired": false
}
```

#### 4. Get URL Statistics
**GET** `/api/stats/{short_code}`

Returns usage statistics for a shortened URL.

**Response:**
```json
{
    "short_code": "abc123",
    "total_clicks": 150,
    "last_accessed": "2024-01-01T11:30:00Z",
    "created_at": "2024-01-01T10:00:00Z"
}
```

#### 5. Get Recent URLs
**GET** `/api/recent`

Returns recently created URLs.

**Response:**
```json
{
    "recent_urls": [
        {
            "short_code": "abc123",
            "original_url": "https://example.com",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ]
}
```

#### 6. Check Code Availability
**GET** `/api/check-code/{short_code}`

Checks if a custom short code is available.

**Response:**
```json
{
    "available": true,
    "message": "Code is available"
}
```

#### 7. Health Check
**GET** `/health`

Returns the health status of the application.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `SECRET_KEY` | Flask secret key | Auto-generated |

### MongoDB Collections

- **urls**: Stores URL shortening data
- **Indexes**: 
  - `short_code` (unique)
  - `original_url`
  - `expires_at`

## 📊 Logging

The application includes comprehensive logging with:

- **Request/Response Logging**: All API calls are logged
- **Error Tracking**: Detailed error logging with stack traces
- **Performance Monitoring**: Request duration tracking
- **External Service Integration**: Logs sent to evaluation service

### Log Levels
- `INFO`: General application flow
- `DEBUG`: Detailed debugging information
- `ERROR`: Error conditions and exceptions

## 🧪 Testing

### Postman Collection
A Postman collection is included in `backend_tests/postman_collection/` for testing all endpoints.

### Manual Testing
```bash
# Test URL shortening
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com", "validity": 24}'

# Test redirect
curl -L http://localhost:5000/abc123

# Test health check
curl http://localhost:5000/health
```

## 🔄 Background Tasks

The application runs a background scheduler that:
- Cleans up expired URLs automatically
- Maintains database performance
- Runs every hour by default

## 🚨 Error Handling

The application handles various error scenarios:
- Invalid URLs
- Duplicate short codes
- Expired URLs
- Database connection issues
- External service failures

## 📁 Project Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── logging/
│   ├── middleware.py     # Logging middleware
│   └── decorators.py     # Route logging decorators
├── logging-middleware/
│   └── middleware.py     # Additional middleware
└── backend_tests/
    └── postman_collection/
        └── url_shortner.postman_collection.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Srilasya Pasumarthi**
- Email: srilasyapasumarthi@gmail.com
- GitHub: [srilasya-2005](https://github.com/srilasya-2005)
- Roll No: 22kn1a4472

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact: srilasyapasumarthi@gmail.com

---

**Note**: This backend is designed to work with an evaluation service for logging. Ensure the evaluation service is accessible for full functionality. 
