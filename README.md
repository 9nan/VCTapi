# VLR.GG API v2.0 - High Performance Edition

An Unofficial REST API for [vlr.gg](https://www.vlr.gg/), providing access to Valorant Esports match data and news coverage with **significant performance improvements**.

> **By [9nan](https://github.com/9nan)** - Original project enhanced with performance optimizations, improved error handling, and better user experience.

## Features

- Get live match scores with real-time updates
- Retrieve detailed match information
- Lightweight and fast API
- Rate limiting for fair usage
- Performance monitoring endpoints
- Health check endpoints
- Comprehensive error handling

## API Endpoints

### Live Matches
```
GET /matches/live
```
Get all currently live Valorant matches with optimized performance.

### Match Details
```
GET /matches/{match_id}
```
Get detailed information about a specific match by its ID.

### Performance Statistics
```
GET /stats/performance
```
Get API performance metrics and statistics.

### Health Check
```
GET /health
```
Check API health status.

## Installation

1. Run the server:
   ```bash
   start.bat
   ```

The API will be available at `http://localhost:3001`

## Usage

### Get Live Matches
```bash
curl http://localhost:3001/matches/live
```

### Get Match Details
```bash
curl http://localhost:3001/matches/{match_id}
```

### Check Performance Stats
```bash
curl http://localhost:3001/stats/performance
```

## Rate Limiting

The API implements intelligent rate limiting to ensure fair usage. If you exceed the rate limit, you'll receive a `429 Too Many Requests` response with retry information.

## Dependencies

- Python 3.11
- FastAPI 0.104.1
- Uvicorn 0.24.0
- aiohttp 3.9.1 (for async HTTP requests)
- selectolax 0.3.17 (for HTML parsing)
- slowapi 0.1.9 (for rate limiting)

## Architecture

### Async Client (`api/async_client.py`)
- High-performance HTTP client with connection pooling
- Intelligent caching system
- Automatic retry logic with exponential backoff
- DNS caching and keep-alive connections

### Async Scraper (`api/async_scraper.py`)
- Concurrent match processing
- Optimized HTML parsing
- Non-blocking additional data fetching
- Error resilience

### Performance Monitor (`utils/performance.py`)
- Request tracking and statistics
- Memory usage monitoring
- Response time analytics
- Cache hit/miss tracking

## Performance Tips

1. **Use Connection Pooling**: The API automatically reuses HTTP connections
2. **Leverage Caching**: Live matches are cached for 30 seconds
3. **Monitor Performance**: Use `/stats/performance` to track API health
4. **Handle Rate Limits**: Implement exponential backoff in your client
5. **Use Async Clients**: Use async HTTP clients in your applications

## Error Handling

The API includes comprehensive error handling:
- Automatic retries for network failures
- Graceful degradation when external services are unavailable
- Detailed error messages with context
- Performance impact logging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
