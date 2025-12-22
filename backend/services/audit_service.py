"""Audit logging service"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models import AuditLog


class AuditService:
    """Service for creating audit log entries"""
    
    @staticmethod
    def log(
        db: Session,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_user_id: Optional[str] = None,
        before_json: Optional[Dict[str, Any]] = None,
        after_json: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            entity_type: Type of entity (claim, user, plan, etc.)
            entity_id: ID of the entity
            action: Action performed (create, update, delete, status_change, etc.)
            actor_user_id: ID of user who performed the action
            before_json: State before the change
            after_json: State after the change
            ip_address: IP address of the request
            user_agent: User agent string
            metadata: Additional metadata
            
        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_user_id=actor_user_id,
            before_json=before_json,
            after_json=after_json,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=metadata
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def log_status_change(
        db: Session,
        claim_id: str,
        old_status: str,
        new_status: str,
        actor_user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> AuditLog:
        """Convenience method for logging claim status changes"""
        return AuditService.log(
            db=db,
            entity_type="claim",
            entity_id=claim_id,
            action="status_change",
            actor_user_id=actor_user_id,
            before_json={"status": old_status},
            after_json={"status": new_status},
            metadata={"notes": notes} if notes else None
        )

