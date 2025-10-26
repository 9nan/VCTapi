# VLR.GG API

An Unofficial REST API for [vlr.gg](https://www.vlr.gg/), providing real-time access to Valorant Esports match data and news coverage. Modified and maintained by [9nan](https://github.com/9nan).


http://45.137.70.90:2592/

## Features

- **Live Match Tracking**: Real-time updates for ongoing Valorant matches
- **Match Details**: Comprehensive match information including scores, maps, and team details
- **High Performance**: Optimized async operations with connection pooling and caching
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Dark Theme UI**: Modern dark theme for the Swagger documentation interface
- **API Performance Monitoring**: Built-in performance tracking for API endpoints

## Installation

1. Clone the repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. Run the server using the provided batch file:
   ```bash
   start.bat
   ```
   Or manually with:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 3001
   ```

2. Access the API documentation at: http://127.0.0.1:3001

## API Endpoints

### GET /matches/live
Retrieve all currently live Valorant matches.

**Response Example:**
```json
{
    "status": "success",
    "data": [
        {
            "team1": "Team A",
            "team2": "Team B",
            "score1": "13",
            "score2": "7",
            "map_number": "1",
            "current_map": "Haven",
            "match_event": "Tournament Name",
            "match_series": "Quarter Finals"
        }
    ]
}
```

### GET /matches/{match_id}
Get detailed information about a specific match by its ID.

**Parameters:**
- `match_id`: The VLR match ID (e.g., '551847' from the match URL)

## Features

### High Performance
- Asynchronous operations using `aiohttp` and `asyncio`
- Connection pooling for optimal resource usage
- Caching system with configurable TTL
- Rate limiting protection

### Dark Theme
The API documentation interface features a modern dark theme for better readability and reduced eye strain. The theme includes:
- Dark background colors
- Proper contrast for text and elements
- Highlighted code blocks
- Custom styling for API method types (GET, POST, etc.)

## Error Handling

The API uses standard HTTP status codes:
- 200: Successful request
- 404: Resource not found
- 429: Too many requests (rate limit exceeded)
- 500: Internal server error

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [vlr.gg](https://www.vlr.gg/) for providing Valorant esports coverage
- Maintained by: [9nan](https://github.com/9nan)
