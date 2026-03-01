#!/usr/bin/env python3
"""
Tests for Location Detector
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.location_detector import LocationDetector, get_location_detector


@pytest.fixture
def location_detector():
    """Create LocationDetector instance"""
    return LocationDetector()


def test_location_detector_initialization(location_detector):
    """Test LocationDetector initialization"""
    assert location_detector is not None
    assert len(location_detector.apis) > 0


@patch('requests.get')
def test_get_location_from_ip_success(mock_get, location_detector):
    """Test successful location detection"""
    # Mock successful API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'city': 'Nashik',
        'regionName': 'Maharashtra',
        'country': 'India',
        'lat': 19.9975,
        'lon': 73.7898,
        'timezone': 'Asia/Kolkata'
    }
    mock_get.return_value = mock_response
    
    location = location_detector.get_location_from_ip()
    
    assert location is not None
    assert location['city'] == 'Nashik'
    assert location['region'] == 'Maharashtra'
    assert location['country'] == 'India'


@patch('requests.get')
def test_get_location_from_ip_failure(mock_get, location_detector):
    """Test location detection with API failure"""
    # Mock API failure
    mock_get.side_effect = Exception("API Error")
    
    location = location_detector.get_location_from_ip()
    
    # Should return default location
    assert location is not None
    assert location['city'] == 'Nashik'
    assert location['region'] == 'Maharashtra'


def test_get_default_location(location_detector):
    """Test default location"""
    location = location_detector._get_default_location()
    
    assert location['city'] == 'Nashik'
    assert location['region'] == 'Maharashtra'
    assert location['country'] == 'India'
    assert location['latitude'] == 19.9975
    assert location['longitude'] == 73.7898


def test_get_location_string(location_detector):
    """Test location string formatting"""
    location = {
        'city': 'Nashik',
        'region': 'Maharashtra',
        'country': 'India'
    }
    
    location_str = location_detector.get_location_string(location)
    
    assert location_str == "Nashik, Maharashtra, India"


def test_is_in_maharashtra(location_detector):
    """Test Maharashtra detection"""
    location_mh = {'region': 'Maharashtra'}
    location_other = {'region': 'Karnataka'}
    
    assert location_detector.is_in_maharashtra(location_mh) is True
    assert location_detector.is_in_maharashtra(location_other) is False


def test_get_nearest_district(location_detector):
    """Test nearest district calculation"""
    # Location near Nashik
    location = {
        'latitude': 20.0,
        'longitude': 73.8
    }
    
    district = location_detector.get_nearest_district(location)
    
    assert district == 'Nashik'


def test_get_nearest_district_pune(location_detector):
    """Test nearest district for Pune coordinates"""
    location = {
        'latitude': 18.5,
        'longitude': 73.9
    }
    
    district = location_detector.get_nearest_district(location)
    
    assert district == 'Pune'


def test_parse_ipapi_response(location_detector):
    """Test parsing ip-api.com response"""
    data = {
        'city': 'Mumbai',
        'regionName': 'Maharashtra',
        'country': 'India',
        'lat': 19.0760,
        'lon': 72.8777,
        'timezone': 'Asia/Kolkata'
    }
    
    location = location_detector._parse_ipapi_response(data)
    
    assert location['city'] == 'Mumbai'
    assert location['region'] == 'Maharashtra'
    assert location['latitude'] == 19.0760


def test_parse_ipapico_response(location_detector):
    """Test parsing ipapi.co response"""
    data = {
        'city': 'Pune',
        'region': 'Maharashtra',
        'country_name': 'India',
        'latitude': 18.5204,
        'longitude': 73.8567,
        'timezone': 'Asia/Kolkata'
    }
    
    location = location_detector._parse_ipapico_response(data)
    
    assert location['city'] == 'Pune'
    assert location['region'] == 'Maharashtra'
    assert location['latitude'] == 18.5204


def test_singleton_pattern():
    """Test get_location_detector singleton"""
    detector1 = get_location_detector()
    detector2 = get_location_detector()
    
    # Should return same instance
    assert detector1 is detector2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
