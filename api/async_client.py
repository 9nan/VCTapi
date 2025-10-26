import asyncio
import logging
from typing import Dict, Any, Optional
import aiohttp
import time
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class VlrClient:
    """High-performance async VLR client with connection pooling and caching"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 30  # Cache for 30 seconds
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,  # Total timeout
            connect=10,  # Connection timeout
            sock_read=10  # Socket read timeout
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache:
            return False
        
        cache_time = self._cache[key].get('timestamp')
        if not cache_time:
            return False
            
        return datetime.now() - cache_time < timedelta(seconds=self._cache_ttl)
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            logger.debug(f"Cache hit for key: {key}")
            return self._cache[key].get('data')
        return None
    
    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Set data in cache with timestamp"""
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        logger.debug(f"Cached data for key: {key}")
    
    async def _make_request(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Make HTTP request with retry logic"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        for attempt in range(max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:  # Rate limited
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except aiohttp.ClientError as e:
                logger.warning(f"Client error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    async def get_live_matches(self) -> Dict[str, Any]:
        """Get live matches with caching"""
        cache_key = "live_matches"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            from .async_scraper import AsyncVlrScraper
            scraper = AsyncVlrScraper(self)
            result = await scraper.get_live_matches_optimized()
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_live_match(self, match_element) -> Dict[str, Any]:
        """Process a single live match element"""
        try:
            from selectolax.parser import HTMLParser
            from datetime import datetime, timezone
            import re
            
            teams = []
            flags = []
            scores = []
            round_texts = []
            
            for team in match_element.css(".h-match-team"):
                teams.append(team.css_first(".h-match-team-name").text().strip())
                flags.append(
                    team.css_first(".flag")
                    .attributes["class"]
                    .replace(" mod-", "")
                    .replace("16", "_")
                )
                scores.append(team.css_first(".h-match-team-score").text().strip())
                
                round_info_ct = team.css(".h-match-team-rounds .mod-ct")
                round_info_t = team.css(".h-match-team-rounds .mod-t")
                round_text_ct = round_info_ct[0].text().strip() if round_info_ct else "N/A"
                round_text_t = round_info_t[0].text().strip() if round_info_t else "N/A"
                round_texts.append({"ct": round_text_ct, "t": round_text_t})
            
            eta = "LIVE"
            match_event = match_element.css_first(".h-match-preview-event").text().strip()
            match_series = match_element.css_first(".h-match-preview-series").text().strip()
            timestamp = datetime.fromtimestamp(
                int(match_element.css_first(".moment-tz-convert").attributes["data-utc-ts"]),
                tz=timezone.utc,
            ).strftime("%Y-%m-%d %H:%M:%S")
            url_path = "https://www.vlr.gg/" + match_element.attributes["href"]
            
            # Fetch additional match details concurrently
            team_logos, current_map, map_number = await self._get_match_details(url_path)
            
            team1_round_ct = round_texts[0]["ct"] if len(round_texts) > 0 else "N/A"
            team1_round_t = round_texts[0]["t"] if len(round_texts) > 0 else "N/A"
            team2_round_ct = round_texts[1]["ct"] if len(round_texts) > 1 else "N/A"
            team2_round_t = round_texts[1]["t"] if len(round_texts) > 1 else "N/A"
            
            return {
                "team1": teams[0],
                "team2": teams[1],
                "flag1": flags[0],
                "flag2": flags[1],
                "team1_logo": team_logos[0] if len(team_logos) > 0 else "",
                "team2_logo": team_logos[1] if len(team_logos) > 1 else "",
                "score1": scores[0],
                "score2": scores[1],
                "team1_round_ct": team1_round_ct,
                "team1_round_t": team1_round_t,
                "team2_round_ct": team2_round_ct,
                "team2_round_t": team2_round_t,
                "map_number": map_number,
                "current_map": current_map,
                "time_until_match": eta,
                "match_event": match_event,
                "match_series": match_series,
                "unix_timestamp": timestamp,
                "match_page": url_path,
            }
            
        except Exception as e:
            logger.error(f"Error processing live match: {e}")
            return {}
    
    async def _get_match_details(self, url_path: str) -> tuple:
        """Get team logos and map details for a match"""
        try:
            html_content = await self._make_request(url_path)
            if not html_content:
                return [], "Unknown", "Unknown"
            
            from selectolax.parser import HTMLParser
            match_html = HTMLParser(html_content)
            
            team_logos = []
            for img in match_html.css(".match-header-vs img"):
                logo_url = "https:" + img.attributes.get("src", "")
                team_logos.append(logo_url)
            
            current_map_element = match_html.css_first(
                ".vm-stats-gamesnav-item.js-map-switch.mod-active.mod-live"
            )
            current_map = "Unknown"
            map_number = "Unknown"
            
            if current_map_element:
                map_text = (
                    current_map_element.css_first("div", default="Unknown")
                    .text()
                    .strip()
                    .replace("\n", "")
                    .replace("\t", "")
                )
                current_map = re.sub(r"^\d+", "", map_text)
                map_number_match = re.search(r"^\d+", map_text)
                map_number = map_number_match.group(0) if map_number_match else "Unknown"
            
            return team_logos, current_map, map_number
            
        except Exception as e:
            logger.error(f"Error getting match details for {url_path}: {e}")
            return [], "Unknown", "Unknown"
    
    async def get_match_by_id(self, match_id: str) -> Dict[str, Any]:
        """Get specific match by ID"""
        try:
            from .async_scraper import AsyncVlrScraper
            scraper = AsyncVlrScraper(self)
            return await scraper.get_match_by_id_optimized(match_id)
        except Exception as e:
            logger.error(f"Error getting match {match_id}: {e}")
            return {"status": "error", "message": str(e)}

# Global client instance
_vlr_client: Optional[VlrClient] = None

async def get_vlr_client() -> VlrClient:
    """Get or create global VLR client instance"""
    global _vlr_client
    if _vlr_client is None:
        _vlr_client = VlrClient()
    return _vlr_client
