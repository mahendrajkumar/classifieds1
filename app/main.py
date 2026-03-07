from fastapi import FastAPI, Request, Query, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import Optional
import duckdb
from datetime import datetime

app = FastAPI(title="Classifieds Website")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CATEGORIES = ["Electronics", "Vehicles", "Real Estate", "Services"]

# Initialize DB on startup
from app.database import init_db
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
async def read_root(request: Request):
    conn = duckdb.connect("classifieds.db")
    try:
        listings_data = conn.execute("SELECT * FROM listings ORDER BY created_at DESC LIMIT 6").fetchall()
        cols = [d[0] for d in conn.description]
        listings = [dict(zip(cols, row)) for row in listings_data]
    finally:
        conn.close()
        
    return templates.TemplateResponse(
        request=request, name="index.html", 
        context={
            "categories": CATEGORIES,
            "listings": listings
        }
    )

@app.get("/search")
async def search(
    request: Request,
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    conn = duckdb.connect("classifieds.db")
    try:
        query = "SELECT * FROM listings WHERE 1=1"
        params = []
        
        if q:
            query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
            params.extend([f"%{q.lower()}%", f"%{q.lower()}%"])
        if category:
            query += " AND category = ?"
            params.append(category)
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
            
        query += " ORDER BY created_at DESC"
        
        listings_data = conn.execute(query, params).fetchall()
        cols = [d[0] for d in conn.description]
        listings = [dict(zip(cols, row)) for row in listings_data]
    finally:
        conn.close()
        
    return templates.TemplateResponse(
        request=request, name="search.html", 
        context={
            "listings": listings,
            "query": q or "",
            "category": category or "",
            "min_price": min_price or "",
            "max_price": max_price or "",
            "all_categories": CATEGORIES
        }
    )

@app.get("/item/{item_id}")
async def read_item(request: Request, item_id: int):
    conn = duckdb.connect("classifieds.db")
    try:
        listing_data = conn.execute("SELECT * FROM listings WHERE id = ?", [item_id]).fetchone()
        if not listing_data:
            raise HTTPException(status_code=404, detail="Item not found")
        
        cols = [d[0] for d in conn.description]
        item = dict(zip(cols, listing_data))
    finally:
        conn.close()
        
    return templates.TemplateResponse(
        request=request, name="listing.html", 
        context={"item": item}
    )

@app.get("/post")
async def get_post_ad(request: Request):
    return templates.TemplateResponse(
        request=request, name="post_ad.html",
        context={"categories": CATEGORIES}
    )

@app.post("/post")
async def create_post_ad(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    contact_email: str = Form(...),
    image_url: str = Form(None)
):
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1513118172236-00b7cc57e1fa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" # Placeholder generic image
        
    conn = duckdb.connect("classifieds.db")
    try:
        query = """
        INSERT INTO listings (title, description, price, category, location, image_url, contact_email, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
        """
        result = conn.execute(query, [
            title, description, price, category, location, image_url, contact_email, datetime.now()
        ]).fetchone()
        
        new_item_id = result[0]
        
    finally:
        conn.close()
        
    return RedirectResponse(url=f"/item/{new_item_id}", status_code=303)
