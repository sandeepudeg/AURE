#!/usr/bin/env python3
"""
Location Detector
Automatically detect farmer location using IP geolocation
"""

import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LocationDetector:
    """Detect user location using IP geolocation"""
    
    def __init__(self):
        """Initialize Location Detector"""
        # Free IP geolocation APIs (no API key required)
        self.apis = [
            'http://ip-api.com/json/',  # Free, no key required
            'https://ipapi.co/json/',    # Free tier available
        ]
    
    def get_location_from_ip(self) -> Optional[Dict[str, str]]:
        """
        Get location information from IP address
        
        Returns:
            Dictionary with location info or None if failed
            {
                'city': 'Nashik',
                'region': 'Maharashtra',
                'country': 'India',
                'latitude': 19.9975,
                'longitude': 73.7898,
                'timezone': 'Asia/Kolkata'
            }
        """
        # Try each API until one works
        for api_url in self.apis:
            try:
                response = requests.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response based on API
                    if 'ip-api.com' in api_url:
                        return self._parse_ipapi_response(data)
                    elif 'ipapi.co' in api_url:
                        return self._parse_ipapico_response(data)
                
            except Exception as e:
                logger.warning(f"Failed to get location from {api_url}: {e}")
                continue
        
        # If all APIs fail, return default location
        logger.warning("All geolocation APIs failed, using default location")
        return self._get_default_location()
    
    def _parse_ipapi_response(self, data: dict) -> Dict[str, str]:
        """Parse response from ip-api.com"""
        return {
            'city': data.get('city', 'Unknown'),
            'region': data.get('regionName', 'Unknown'),
            'country': data.get('country', 'India'),
            'latitude': data.get('lat', 0.0),
            'longitude': data.get('lon', 0.0),
            'timezone': data.get('timezone', 'Asia/Kolkata'),
            'district': data.get('city', 'Unknown')  # Use city as district
        }
    
    def _parse_ipapico_response(self, data: dict) -> Dict[str, str]:
        """Parse response from ipapi.co"""
        return {
            'city': data.get('city', 'Unknown'),
            'region': data.get('region', 'Unknown'),
            'country': data.get('country_name', 'India'),
            'latitude': data.get('latitude', 0.0),
            'longitude': data.get('longitude', 0.0),
            'timezone': data.get('timezone', 'Asia/Kolkata'),
            'district': data.get('city', 'Unknown')
        }
    
    def _get_default_location(self) -> Dict[str, str]:
        """Return default location (Nashik, Maharashtra)"""
        return {
            'city': 'Nashik',
            'region': 'Maharashtra',
            'country': 'India',
            'latitude': 19.9975,
            'longitude': 73.7898,
            'timezone': 'Asia/Kolkata',
            'district': 'Nashik'
        }
    
    def get_location_string(self, location: Dict[str, str]) -> str:
        """
        Format location as a readable string
        
        Args:
            location: Location dictionary
        
        Returns:
            Formatted location string
        """
        city = location.get('city', 'Unknown')
        region = location.get('region', 'Unknown')
        country = location.get('country', 'India')
        
        return f"{city}, {region}, {country}"
    
    def is_in_maharashtra(self, location: Dict[str, str]) -> bool:
        """Check if location is in Maharashtra"""
        region = location.get('region', '').lower()
        return 'maharashtra' in region
    
    def get_nearest_district(self, location: Dict[str, str]) -> str:
        """
        Get nearest Maharashtra district based on coordinates
        
        Args:
            location: Location dictionary with latitude/longitude
        
        Returns:
            Nearest district name
        """
        lat = location.get('latitude', 0.0)
        lon = location.get('longitude', 0.0)
        
        # Maharashtra districts with approximate coordinates
        districts = {
            'Nashik': (19.9975, 73.7898),
            'Pune': (18.5204, 73.8567),
            'Mumbai': (19.0760, 72.8777),
            'Ahmednagar': (19.0948, 74.7480),
            'Dhule': (20.9042, 74.7749),
            'Jalgaon': (21.0077, 75.5626),
            'Aurangabad': (19.8762, 75.3433),
            'Nagpur': (21.1458, 79.0882),
            'Solapur': (17.6599, 75.9064),
            'Kolhapur': (16.7050, 74.2433)
        }
        
        # Calculate distance to each district
        min_distance = float('inf')
        nearest_district = 'Nashik'  # Default
        
        for district, (d_lat, d_lon) in districts.items():
            # Simple Euclidean distance (good enough for rough estimation)
            distance = ((lat - d_lat) ** 2 + (lon - d_lon) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_district = district
        
        return nearest_district


# Singleton instance
_location_detector = None


def get_location_detector() -> LocationDetector:
    """Get or create LocationDetector singleton"""
    global _location_detector
    if _location_detector is None:
        _location_detector = LocationDetector()
    return _location_detector
