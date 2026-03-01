#!/usr/bin/env python3
"""
Agmarknet MCP Server
Provides market price data from Agmarknet and local CSV
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import logging
from pathlib import Path
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agmarknet MCP Server",
    description="Market price data for URE MVP",
    version="1.0.0"
)

# Load Agmarknet CSV data
DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "mandi_prices" / "Agriculture_price_dataset.csv"
price_data = None

try:
    if DATA_PATH.exists():
        price_data = pd.read_csv(DATA_PATH)
        logger.info(f"Loaded {len(price_data)} price records from CSV")
    else:
        logger.warning(f"Price data not found at {DATA_PATH}")
except Exception as e:
    logger.error(f"Failed to load price data: {e}")


# Request models
class MandiPriceRequest(BaseModel):
    crop: str
    district: str
    state: str


class NearbyMandisRequest(BaseModel):
    district: str
    radius_km: Optional[int] = 50


# Response models
class MandiPriceResponse(BaseModel):
    success: bool
    crop: str
    district: str
    state: str
    prices: List[Dict[str, Any]]
    message: Optional[str] = None


class NearbyMandisResponse(BaseModel):
    success: bool
    district: str
    mandis: List[Dict[str, Any]]
    message: Optional[str] = None


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "Agmarknet MCP Server",
        "status": "running",
        "version": "1.0.0",
        "data_loaded": price_data is not None
    }


@app.post("/get_mandi_prices", response_model=MandiPriceResponse)
def get_mandi_prices(request: MandiPriceRequest):
    """
    Get current market prices for a crop in a specific district
    """
    try:
        if price_data is None:
            return MandiPriceResponse(
                success=False,
                crop=request.crop,
                district=request.district,
                state=request.state,
                prices=[],
                message="Price data not available"
            )
        
        # Filter data by crop, district, and state (case-insensitive)
        filtered = price_data[
            (price_data['Commodity'].str.lower() == request.crop.lower()) &
            (price_data['District Name'].str.lower() == request.district.lower()) &
            (price_data['STATE'].str.lower() == request.state.lower())
        ]
        
        if filtered.empty:
            # Try just crop and state if district not found
            filtered = price_data[
                (price_data['Commodity'].str.lower() == request.crop.lower()) &
                (price_data['STATE'].str.lower() == request.state.lower())
            ]
        
        if filtered.empty:
            return MandiPriceResponse(
                success=False,
                crop=request.crop,
                district=request.district,
                state=request.state,
                prices=[],
                message=f"No price data found for {request.crop} in {request.district}, {request.state}"
            )
        
        # Get latest prices (sort by date if available)
        prices = []
        for _, row in filtered.head(5).iterrows():
            prices.append({
                "market": row.get('Market Name', 'Unknown'),
                "min_price": float(row.get('Min_Price', 0)),
                "max_price": float(row.get('Max_Price', 0)),
                "modal_price": float(row.get('Modal_Price', 0)),
                "date": str(row.get('Price Date', 'N/A')),
                "variety": str(row.get('Variety', 'General'))
            })
        
        return MandiPriceResponse(
            success=True,
            crop=request.crop,
            district=request.district,
            state=request.state,
            prices=prices,
            message=f"Found {len(prices)} price records"
        )
    
    except Exception as e:
        logger.error(f"Error getting mandi prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_nearby_mandis", response_model=NearbyMandisResponse)
def get_nearby_mandis(request: NearbyMandisRequest):
    """
    Get list of nearby mandis in a district
    """
    try:
        if price_data is None:
            return NearbyMandisResponse(
                success=False,
                district=request.district,
                mandis=[],
                message="Price data not available"
            )
        
        # Filter by district
        filtered = price_data[
            price_data['District Name'].str.lower() == request.district.lower()
        ]
        
        if filtered.empty:
            return NearbyMandisResponse(
                success=False,
                district=request.district,
                mandis=[],
                message=f"No mandis found in {request.district}"
            )
        
        # Get unique markets
        unique_markets = filtered['Market Name'].unique()
        
        mandis = []
        for market in unique_markets[:10]:  # Limit to 10 mandis
            market_data = filtered[filtered['Market Name'] == market].iloc[0]
            mandis.append({
                "name": market,
                "district": str(market_data.get('District Name', '')),
                "state": str(market_data.get('STATE', '')),
                "commodities_count": len(filtered[filtered['Market Name'] == market]['Commodity'].unique())
            })
        
        return NearbyMandisResponse(
            success=True,
            district=request.district,
            mandis=mandis,
            message=f"Found {len(mandis)} mandis"
        )
    
    except Exception as e:
        logger.error(f"Error getting nearby mandis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("Starting Agmarknet MCP Server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
