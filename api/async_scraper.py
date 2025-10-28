import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import re

logger = logging.getLogger(__name__)

class AsyncVlrScraper:
    """Async VLR scraper with optimized performance"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_live_matches_optimized(self) -> Dict[str, Any]:
        """Optimized live matches scraper with concurrent processing"""
        try:
            url = "https://www.vlr.gg"
            html_content = await self.client._make_request(url)
            if not html_content:
                return {"status": "error", "message": "Failed to fetch live matches"}
            
            from selectolax.parser import HTMLParser
            html = HTMLParser(html_content)
            
            matches = html.css(".js-home-matches-upcoming a.wf-module-item")
            live_matches = [match for match in matches if match.css_first(".h-match-eta.mod-live")]
            
            if not live_matches:
                # Return a single match object with "no game is live" message
                no_game_match = {
                    "team1": "",
                    "team2": "",
                    "flag1": "",
                    "flag2": "",
                    "score1": "",
                    "score2": "",
                    "team1_round_ct": "",
                    "team1_round_t": "",
                    "team2_round_ct": "",
                    "team2_round_t": "",
                    "time_until_match": "",
                    "match_event": "",
                    "match_series": "",
                    "unix_timestamp": "",
                    "match_page": "",
                    "team1_logo": "",
                    "team2_logo": "",
                    "map_number": "",
                    "current_map": "",
                    "klurgecustom": "no game is live"
                }
                return {"status": "success", "data": [no_game_match]}
            
            # Process all live matches concurrently
            tasks = [self._process_live_match_optimized(match) for match in live_matches]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and empty results
            valid_results = [r for r in results if isinstance(r, dict) and r]

            # Add custom tags dynamically for all matches
            for idx, match in enumerate(valid_results):
                key_name = f"klurgecustom{idx + 1}" if idx > 0 else "klurgecustom"
                match[key_name] = f"{match['team1']} {match['score1']} : {match['team2']} {match['score2']}"
            
            return {"status": "success", "data": valid_results}
            
        except Exception as e:
            logger.error(f"Error in get_live_matches_optimized: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_live_match_optimized(self, match_element) -> Dict[str, Any]:
        """Optimized live match processing"""
        try:
            # Extract basic match info
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
            
            # Extract match metadata
            match_event = match_element.css_first(".h-match-preview-event").text().strip()
            match_series = match_element.css_first(".h-match-preview-series").text().strip()
            timestamp = datetime.fromtimestamp(
                int(match_element.css_first(".moment-tz-convert").attributes["data-utc-ts"]),
                tz=timezone.utc,
            ).strftime("%Y-%m-%d %H:%M:%S")
            url_path = "https://www.vlr.gg/" + match_element.attributes["href"]
            
            # Create base match data
            match_data = {
                "team1": teams[0],
                "team2": teams[1],
                "flag1": flags[0],
                "flag2": flags[1],
                "score1": scores[0],
                "score2": scores[1],
                "team1_round_ct": round_texts[0]["ct"] if len(round_texts) > 0 else "N/A",
                "team1_round_t": round_texts[0]["t"] if len(round_texts) > 0 else "N/A",
                "team2_round_ct": round_texts[1]["ct"] if len(round_texts) > 1 else "N/A",
                "team2_round_t": round_texts[1]["t"] if len(round_texts) > 1 else "N/A",
                "time_until_match": "LIVE",
                "match_event": match_event,
                "match_series": match_series,
                "unix_timestamp": timestamp,
                "match_page": url_path,
                "team1_logo": "",
                "team2_logo": "",
                "map_number": "Unknown",
                "current_map": "Unknown"
            }
            
            # Fetch additional details asynchronously (non-blocking)
            try:
                team_logos, current_map, map_number = await self.client._get_match_details(url_path)
                match_data.update({
                    "team1_logo": team_logos[0] if len(team_logos) > 0 else "",
                    "team2_logo": team_logos[1] if len(team_logos) > 1 else "",
                    "map_number": map_number,
                    "current_map": current_map
                })
            except Exception as e:
                logger.warning(f"Failed to fetch additional details for {url_path}: {e}")
                # Continue with basic data if additional details fail
            
            return match_data
            
        except Exception as e:
            logger.error(f"Error processing live match: {e}")
            return {}
    
    async def get_match_by_id_optimized(self, match_id: str) -> Dict[str, Any]:
        """Optimized match lookup by ID"""
        try:
            # First check live matches cache
            live_matches = await self.client.get_live_matches()
            if live_matches.get('status') == 'success':
                for match in live_matches.get('data', []):
                    if match_id in match.get('match_page', ''):
                        return {
                            "status": "success",
                            "data": match
                        }
            
            # If not in live matches, try direct lookup
            return await self._get_match_directly(match_id)
            
        except Exception as e:
            logger.error(f"Error in get_match_by_id_optimized: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _get_match_directly(self, match_id: str) -> Dict[str, Any]:
        """Get match data directly from match page"""
        try:
            url = f"https://www.vlr.gg/{match_id}"
            html_content = await self.client._make_request(url)
            if not html_content:
                return {"status": "error", "message": f"Match {match_id} not found"}
            
            from selectolax.parser import HTMLParser
            html = HTMLParser(html_content)
            
            # Extract match data from the specific match page
            # This is a simplified version - you may need to adjust selectors
            match_data = {
                "team1": "Unknown",
                "team2": "Unknown",
                "flag1": "",
                "flag2": "",
                "score1": "0",
                "score2": "0",
                "team1_logo": "",
                "team2_logo": "",
                "team1_round_ct": "N/A",
                "team1_round_t": "N/A",
                "team2_round_ct": "N/A",
                "team2_round_t": "N/A",
                "map_number": "Unknown",
                "current_map": "Unknown",
                "time_until_match": "Unknown",
                "match_event": "Unknown",
                "match_series": "Unknown",
                "unix_timestamp": "",
                "match_page": url
            }
            
            # Try to extract team names and scores
            try:
                team_elements = html.css(".match-header-vs .team-name")
                if len(team_elements) >= 2:
                    match_data["team1"] = team_elements[0].text().strip()
                    match_data["team2"] = team_elements[1].text().strip()
                
                score_elements = html.css(".match-header-vs .score")
                if len(score_elements) >= 2:
                    match_data["score1"] = score_elements[0].text().strip()
                    match_data["score2"] = score_elements[1].text().strip()
                
                # Extract team logos
                logo_elements = html.css(".match-header-vs img")
                if len(logo_elements) >= 2:
                    match_data["team1_logo"] = "https:" + logo_elements[0].attributes.get("src", "")
                    match_data["team2_logo"] = "https:" + logo_elements[1].attributes.get("src", "")
                
            except Exception as e:
                logger.warning(f"Failed to extract detailed match data: {e}")
            
            return {
                "status": "success",
                "data": match_data
            }
            
        except Exception as e:
            logger.error(f"Error in _get_match_directly: {e}")
            return {"status": "error", "message": str(e)}
