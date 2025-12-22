"""
Seed script to create initial data for development and testing.
Run with: python -m backend.scripts.seed_data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from backend.database.config import SessionLocal, init_db
from backend.database.models import (
    User, Role, UserRole, InsuranceCompany, Plan, 
    MemberPolicy, Claim, ValidationRule,
    RoleType, ClaimStatus, ClaimCategory, PolicyStatus
)
from backend.auth.service import AuthService


def seed_roles(db):
    """Create default roles"""
    print("Creating roles...")
    AuthService.init_default_roles(db)
    print("  ✓ Roles created")


def seed_users(db):
    """Create test users"""
    print("Creating users...")
    
    users_data = [
        {
            "email": "admin@example.com",
            "password": "password123",
            "first_name": "Admin",
            "last_name": "User",
            "roles": [RoleType.ADMIN, RoleType.AGENT, RoleType.USER]
        },
        {
            "email": "agent@example.com",
            "password": "password123",
            "first_name": "Agent",
            "last_name": "Smith",
            "roles": [RoleType.AGENT]
        },
        {
            "email": "user@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "roles": [RoleType.USER]
        },
        {
            "email": "jane@example.com",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Doe",
            "roles": [RoleType.USER]
        }
    ]
    
    created_users = {}
    for user_data in users_data:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            print(f"  → User {user_data['email']} already exists")
            created_users[user_data["email"]] = existing
            continue
        
        user = AuthService.create_user(
            db=db,
            email=user_data["email"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            roles=user_data["roles"]
        )
        created_users[user_data["email"]] = user
        print(f"  ✓ Created {user_data['email']}")
    
    return created_users


def seed_insurance_companies(db):
    """Create sample insurance companies"""
    print("Creating insurance companies...")
    
    companies_data = [
        {"name": "HealthFirst Insurance", "code": "HFI"},
        {"name": "BlueCross BlueShield", "code": "BCBS"},
        {"name": "United Healthcare", "code": "UHC"},
    ]
    
    created = {}
    for company_data in companies_data:
        existing = db.query(InsuranceCompany).filter(
            InsuranceCompany.name == company_data["name"]
        ).first()
        if existing:
            print(f"  → Company {company_data['name']} already exists")
            created[company_data["name"]] = existing
            continue
        
        company = InsuranceCompany(**company_data)
        db.add(company)
        db.flush()
        created[company_data["name"]] = company
        print(f"  ✓ Created {company_data['name']}")
    
    db.commit()
    return created


def seed_plans(db, companies):
    """Create sample plans"""
    print("Creating plans...")
    
    plans_data = [
        {
            "insurance_company_id": companies["HealthFirst Insurance"].id,
            "name": "Gold PPO Plan",
            "code": "GOLD-PPO",
            "auto_approve_enabled": True,
            "auto_approve_amount_cap": 500.0,
            "min_ocr_quality_score": 0.75,
            "min_confidence_score": 0.80,
            "max_duplicate_score": 0.4,
            "max_fraud_risk_score": 0.3,
        },
        {
            "insurance_company_id": companies["HealthFirst Insurance"].id,
            "name": "Silver HMO Plan",
            "code": "SILVER-HMO",
            "auto_approve_enabled": True,
            "auto_approve_amount_cap": 250.0,
        },
        {
            "insurance_company_id": companies["BlueCross BlueShield"].id,
            "name": "Premium Care",
            "code": "PREM-CARE",
            "auto_approve_enabled": False,
        },
    ]
    
    created = {}
    for plan_data in plans_data:
        existing = db.query(Plan).filter(Plan.code == plan_data["code"]).first()
        if existing:
            print(f"  → Plan {plan_data['name']} already exists")
            created[plan_data["name"]] = existing
            continue
        
        plan = Plan(**plan_data)
        db.add(plan)
        db.flush()
        created[plan_data["name"]] = plan
        print(f"  ✓ Created {plan_data['name']}")
    
    db.commit()
    return created


def seed_policies(db, users, plans):
    """Create member policies for test users"""
    print("Creating member policies...")
    
    policies_data = [
        {
            "user_id": users["user@example.com"].id,
            "plan_id": plans["Gold PPO Plan"].id,
            "member_id": "MEM-001-2024",
            "start_date": datetime.now() - timedelta(days=365),
            "status": PolicyStatus.ACTIVE,
        },
        {
            "user_id": users["jane@example.com"].id,
            "plan_id": plans["Silver HMO Plan"].id,
            "member_id": "MEM-002-2024",
            "start_date": datetime.now() - timedelta(days=180),
            "status": PolicyStatus.ACTIVE,
        },
    ]
    
    for policy_data in policies_data:
        existing = db.query(MemberPolicy).filter(
            MemberPolicy.member_id == policy_data["member_id"]
        ).first()
        if existing:
            print(f"  → Policy {policy_data['member_id']} already exists")
            continue
        
        policy = MemberPolicy(**policy_data)
        db.add(policy)
        print(f"  ✓ Created policy {policy_data['member_id']}")
    
    db.commit()


def seed_validation_rules(db, plans):
    """Create sample validation rules"""
    print("Creating validation rules...")
    
    rules_data = [
        # Global rules (plan_id = None)
        {
            "plan_id": None,
            "name": "Maximum Claim Age",
            "rule_type": "date_range",
            "condition_json": {"max_days_past": 365, "max_days_future": 0},
            "error_message": "Service date must be within the last 365 days",
            "severity": "error",
            "order": 1,
        },
        {
            "plan_id": None,
            "name": "Required Provider Name",
            "rule_type": "required_fields",
            "condition_json": {"fields": ["provider_name"]},
            "error_message": "Provider name is required",
            "severity": "warning",
            "order": 2,
        },
        # Plan-specific rules
        {
            "plan_id": plans["Gold PPO Plan"].id,
            "name": "Gold Plan Amount Limit",
            "rule_type": "amount_limit",
            "condition_json": {"max_amount": 50000, "min_amount": 1},
            "error_message": "Claim amount exceeds plan limit",
            "severity": "error",
            "order": 10,
        },
        {
            "plan_id": plans["Silver HMO Plan"].id,
            "name": "Silver Plan Amount Limit",
            "rule_type": "amount_limit",
            "condition_json": {"max_amount": 25000, "min_amount": 1},
            "error_message": "Claim amount exceeds plan limit",
            "severity": "error",
            "order": 10,
        },
    ]
    
    for rule_data in rules_data:
        existing = db.query(ValidationRule).filter(
            ValidationRule.name == rule_data["name"]
        ).first()
        if existing:
            print(f"  → Rule {rule_data['name']} already exists")
            continue
        
        rule = ValidationRule(**rule_data)
        db.add(rule)
        print(f"  ✓ Created rule {rule_data['name']}")
    
    db.commit()


def seed_sample_claims(db, users, plans):
    """Create sample claims for testing"""
    print("Creating sample claims...")
    
    claims_data = [
        {
            "user_id": users["user@example.com"].id,
            "plan_id": plans["Gold PPO Plan"].id,
            "category": ClaimCategory.MEDICAL,
            "status": ClaimStatus.APPROVED,
            "total_amount": 250.00,
            "approved_amount": 250.00,
            "provider_name": "City Medical Center",
            "service_date": datetime.now() - timedelta(days=30),
            "description": "Annual physical exam",
        },
        {
            "user_id": users["user@example.com"].id,
            "plan_id": plans["Gold PPO Plan"].id,
            "category": ClaimCategory.PHARMACY,
            "status": ClaimStatus.PENDING_REVIEW,
            "total_amount": 125.50,
            "provider_name": "CVS Pharmacy",
            "service_date": datetime.now() - timedelta(days=7),
            "description": "Prescription medication",
        },
        {
            "user_id": users["jane@example.com"].id,
            "plan_id": plans["Silver HMO Plan"].id,
            "category": ClaimCategory.DENTAL,
            "status": ClaimStatus.SUBMITTED,
            "total_amount": 450.00,
            "provider_name": "Smile Dental Clinic",
            "service_date": datetime.now() - timedelta(days=14),
            "description": "Dental cleaning and x-rays",
        },
    ]
    
    from backend.services.claim_service import ClaimService
    
    for i, claim_data in enumerate(claims_data):
        claim_number = ClaimService.generate_claim_number()
        
        claim = Claim(
            claim_number=claim_number,
            submitted_at=datetime.now() - timedelta(days=claim_data.get("days_ago", i * 7)),
            **claim_data
        )
        db.add(claim)
        print(f"  ✓ Created claim {claim_number}")
    
    db.commit()


def main():
    """Run all seed functions"""
    print("\n" + "=" * 50)
    print("ClaimSphere AI - Database Seeding")
    print("=" * 50 + "\n")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print("  ✓ Database initialized\n")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_roles(db)
        users = seed_users(db)
        companies = seed_insurance_companies(db)
        plans = seed_plans(db, companies)
        seed_policies(db, users, plans)
        seed_validation_rules(db, plans)
        seed_sample_claims(db, users, plans)
        
        print("\n" + "=" * 50)
        print("✅ Seeding complete!")
        print("=" * 50)
        print("\nTest credentials:")
        print("  Admin: admin@example.com / password123")
        print("  Agent: agent@example.com / password123")
        print("  User:  user@example.com / password123")
        print("")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

