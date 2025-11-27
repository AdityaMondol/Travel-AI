#!/usr/bin/env python
"""Leonore AI CLI management tool"""
import click
import asyncio
from datetime import datetime
from app.core.database import init_db, SessionLocal, Session, Message, Memory
from app.memory.memory_system import MemorySystem
from app.core.logger import setup_logger

logger = setup_logger(__name__)

@click.group()
def cli():
    """Leonore AI Management CLI"""
    pass

@cli.command()
def init_database():
    """Initialize database"""
    click.echo("Initializing database...")
    try:
        init_db()
        click.echo("✓ Database initialized successfully")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)

@cli.command()
def cleanup_sessions():
    """Clean up old sessions"""
    click.echo("Cleaning up old sessions...")
    try:
        db = SessionLocal()
        
        # Delete sessions older than 30 days
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        deleted = db.query(Session).filter(Session.created_at < cutoff).delete()
        db.commit()
        
        click.echo(f"✓ Deleted {deleted} old sessions")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
    finally:
        db.close()

@cli.command()
def cleanup_memory():
    """Clean up old memory entries"""
    click.echo("Cleaning up old memory entries...")
    try:
        db = SessionLocal()
        
        # Delete memories older than 90 days
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=90)
        
        deleted = db.query(Memory).filter(Memory.created_at < cutoff).delete()
        db.commit()
        
        click.echo(f"✓ Deleted {deleted} old memory entries")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
    finally:
        db.close()

@cli.command()
def stats():
    """Show system statistics"""
    try:
        db = SessionLocal()
        
        sessions = db.query(Session).count()
        messages = db.query(Message).count()
        memories = db.query(Memory).count()
        
        click.echo("\n=== Leonore AI Statistics ===")
        click.echo(f"Sessions: {sessions}")
        click.echo(f"Messages: {messages}")
        click.echo(f"Memory Entries: {memories}")
        
        # Memory by type
        memory_system = MemorySystem()
        stats = memory_system.get_stats()
        
        click.echo("\nMemory by Type:")
        for mem_type, count in stats.get("by_type", {}).items():
            click.echo(f"  {mem_type}: {count}")
        
        db.close()
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)

@cli.command()
@click.option('--session-id', help='Session ID to export')
@click.option('--output', default='export.json', help='Output file')
def export_session(session_id, output):
    """Export session data"""
    try:
        import json
        db = SessionLocal()
        
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            click.echo(f"✗ Session {session_id} not found", err=True)
            return
        
        messages = db.query(Message).filter(Message.session_id == session_id).all()
        
        data = {
            "session": {
                "id": session.id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            },
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ]
        }
        
        with open(output, 'w') as f:
            json.dump(data, f, indent=2)
        
        click.echo(f"✓ Exported to {output}")
        db.close()
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)

@cli.command()
def test_api():
    """Test API connectivity"""
    click.echo("Testing API...")
    try:
        import requests
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            click.echo(f"✓ API is healthy")
            click.echo(f"  Status: {data.get('status')}")
            click.echo(f"  Service: {data.get('service')}")
            click.echo(f"  Version: {data.get('version')}")
        else:
            click.echo(f"✗ API returned status {response.status_code}", err=True)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)

@cli.command()
def reset_database():
    """Reset database (WARNING: deletes all data)"""
    if click.confirm("⚠️  This will delete all data. Continue?"):
        try:
            from app.core.database import Base, engine
            
            click.echo("Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            
            click.echo("Creating new tables...")
            init_db()
            
            click.echo("✓ Database reset successfully")
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
    else:
        click.echo("Cancelled")

if __name__ == '__main__':
    cli()
