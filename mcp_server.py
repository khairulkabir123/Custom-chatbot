import asyncio
from mcp.server.fastmcp import FastMCP
from database import SessionLocal, Experience
from sentence_transformers import SentenceTransformer

# Initialize FastMCP Server
mcp = FastMCP("Outings MCP Server")

# Load real local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

@mcp.tool()
def search_outings(query: str, max_price: float = None) -> str:
    """
    Search for outings, cafes, and experiences based on user query and optional max budget.
    """
    db = SessionLocal()
    try:
        # Convert user query to real vector
        query_vector = model.encode(query).tolist()
        
        # Base query using pgvector cosine distance
        sql_query = db.query(Experience).order_by(Experience.embedding.cosine_distance(query_vector))
        
        # Apply optional price filter
        if max_price is not None:
            sql_query = sql_query.filter(Experience.price <= max_price)
            
        results = sql_query.limit(3).all()
        
        if not results:
            return "No matching outings found."
            
        # Format results as a readable string for the AI model
        formatted = []
        for r in results:
            details = [
                f"- Name: {r.name}",
                f"  Location: {r.city}, {r.address}",
                f"  Price: ${r.price}",
                f"  Description: {r.shortDesc}",
                f"  Cancel Policy: {r.cancelPolicy}",
                f"  Guest Requirements: {r.guestRequirements}",
                f"  Rating: {r.averageRating} ({r.reviewCount} reviews)",
                f"  Max Guests: {r.maxGuest}",
                f"  Notes: {r.notes}"
            ]
            formatted.append("\n".join(details))
            
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error occurred during search: {str(e)}"
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
