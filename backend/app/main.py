from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
import os

from app.core.config import settings
from app.core.database import get_db
from app.modules.athletes.models import AthleteProfile, PrivacyLevel

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Setup Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Ensure handlers are registered
import app.modules.downloads.handlers as _downloads_handlers
import app.modules.athletes.handlers as _athletes_handlers

# Routers
from app.modules.auth.router import router as auth_router
from app.modules.competitions.router import router as events_router
from app.modules.storage.router import router as storage_router
from app.modules.face_recognition.router import router as face_recognition_router
from app.modules.payments.router import router as payments_router
from app.modules.subscriptions.router import router as subscriptions_router
from app.modules.favorites.router import router as favorites_router
from app.modules.downloads.router import router as downloads_router
from app.modules.archives.router import router as archives_router
from app.modules.athletes.router import router as athletes_router
from app.modules.public.router import router as public_router

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(storage_router)
app.include_router(face_recognition_router)
app.include_router(payments_router)
app.include_router(subscriptions_router)
app.include_router(favorites_router)
app.include_router(downloads_router)
app.include_router(archives_router)
app.include_router(athletes_router, prefix="/api/v1/athletes")
app.include_router(public_router, prefix="/api/v1/public")

# SSR Route for Public Profiles
@app.get("/@{slug}", response_class=HTMLResponse, tags=["SSR"])
async def render_public_profile(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AthleteProfile).filter(AthleteProfile.slug == slug))
    profile = result.scalar_one_or_none()

    # Si le profil n'existe pas ou est privé, on renvoie une structure de base pour que React s'affiche et gère l'erreur 404
    if not profile or profile.is_public == PrivacyLevel.PRIVATE:
        return templates.TemplateResponse(
            "public_profile.html", 
            {
                "request": request, 
                "title": "Profil Introuvable | ZoPic", 
                "description": "Ce profil n'existe pas ou est privé.",
                "og_image": "https://zopic.studio/default-share.jpg",
                "url": str(request.url),
                "json_ld": ""
            }
        )

    title = f"{profile.bio or 'Profil Sportif'} | @{profile.slug} - ZoPic"
    description = f"Découvrez les photos et la carrière sportive de @{profile.slug}."
    if profile.club:
        description += f" Club: {profile.club}."
    
    # Stratégie og:image: Dernière photo achetée (MVP = cover) -> photo profil -> generic
    og_image = profile.cover_photo_url or profile.profile_photo_url or "https://zopic.studio/default-share.jpg"

    json_ld_data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": slug,
        "description": description,
        "image": og_image,
        "url": str(request.url)
    }

    return templates.TemplateResponse(
        "public_profile.html",
        {
            "request": request,
            "title": title,
            "description": description,
            "og_image": og_image,
            "url": str(request.url),
            "json_ld": json.dumps(json_ld_data)
        }
    )
