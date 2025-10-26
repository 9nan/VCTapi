import json
from .scrapers import vlr_rankings, vlr_live_score, get_match_details

class Vlr:
    @staticmethod
    def vlr_rankings(region):
        """Get rankings for a region"""
        try:
            result = vlr_rankings(region)
            # Ensure the result is a dictionary with a 'data' key
            if isinstance(result, dict):
                return result
            return {"status": "success", "data": result if result is not None else []}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def get_match_details(match_id):
        """Get detailed information about a specific match by its ID"""
        try:
            result = get_match_details(match_id)
            if not result or result.get('status') == 'error':
                return {"status": "error", "message": result.get('message', 'Failed to fetch match details')}
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def vlr_live_score():
        """Get current live matches"""
        try:
            result = vlr_live_score(1)  # Just get first page by default
            # Ensure the result is a list or can be parsed into a list
            if isinstance(result, list):
                return {"status": "success", "data": result}
            elif isinstance(result, str):
                # Try to parse string as JSON
                try:
                    parsed = json.loads(result)
                    return {"status": "success", "data": parsed if isinstance(parsed, list) else [parsed]}
                except json.JSONDecodeError:
                    return {"status": "success", "data": [result] if result else []}
            return {"status": "success", "data": [result] if result else []}
        except Exception as e:
            return {"status": "error", "message": str(e)}
