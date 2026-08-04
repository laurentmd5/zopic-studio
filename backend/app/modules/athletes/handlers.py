import logging
from sqlalchemy.future import select
from app.core.events import event_bus
from app.modules.payments.events import PaymentCompletedEvent
from app.modules.athletes.models import AthleteStatistics
from app.modules.payments.models import OrderItem
from app.modules.competitions.models import Photo, Epreuve, Competition
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def update_athlete_statistics(event: PaymentCompletedEvent):
    """
    Incrémente les statistiques de l'athlète de manière asynchrone après un paiement.
    """
    logger.info(f"Updating AthleteStatistics for Order {event.order_id}")
    
    # Guest cannot have persistent statistics until they create an account and merge
    if not event.user_id:
        return
        
    async with AsyncSessionLocal() as db:
        try:
            # Récupérer les infos sur la commande
            # On veut savoir combien de photos, de quelles compétitions, etc.
            query = (
                select(
                    Photo.id,
                    Competition.id.label("competition_id"),
                    Competition.settings
                )
                .join(OrderItem, OrderItem.photo_id == Photo.id)
                .join(Epreuve, Epreuve.id == Photo.epreuve_id)
                .join(Competition, Competition.id == Epreuve.competition_id)
                .filter(OrderItem.order_id == event.order_id)
            )
            result = await db.execute(query)
            rows = result.all()
            
            if not rows:
                return
                
            photos_count = len(rows)
            competition_ids = set()
            sports = set()
            
            for row in rows:
                competition_ids.add(row.competition_id)
                sport = row.settings.get("sport", "Autres") if row.settings else "Autres"
                sports.add(sport)
                
            # Update stats
            from sqlalchemy import update
            
            stats_result = await db.execute(select(AthleteStatistics).filter(AthleteStatistics.user_id == event.user_id))
            stats = stats_result.scalar_one_or_none()
            
            if not stats:
                stats = AthleteStatistics(
                    user_id=event.user_id,
                    competitions=len(competition_ids),
                    photos=photos_count,
                    disciplines=len(sports),
                    albums=0,
                    photographers=0,
                    active_since_year=None
                )
                db.add(stats)
                await db.commit()
            else:
                stmt = (
                    update(AthleteStatistics)
                    .where(AthleteStatistics.user_id == event.user_id)
                    .values(
                        photos=AthleteStatistics.photos + photos_count,
                        competitions=AthleteStatistics.competitions + len(competition_ids),
                        disciplines=AthleteStatistics.disciplines + len(sports)
                    )
                )
                await db.execute(stmt)
                await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update AthleteStatistics for Order {event.order_id}: {e}")

# Register handler
event_bus.subscribe(PaymentCompletedEvent, update_athlete_statistics)
