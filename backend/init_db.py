"""
Database Initialization Script
Creates tables and initializes with default data (users, sample alumni)
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import db, User, Alumni, Engagement, Donation, AuditLog
from app import create_app


def init_database():
    """Initialize database with tables and seed data"""
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("  Alumni ML Platform - Database Initialization")
        print("=" * 70)
        print()
        
        # Drop all tables (WARNING: This deletes all data!)
        print("[1/5] Dropping existing tables...")
        db.drop_all()
        print("      ✓ Tables dropped")
        
        # Create all tables
        print("[2/5] Creating database tables...")
        db.create_all()
        print("      ✓ Tables created:")
        print("        - users")
        print("        - alumni")
        print("        - engagements")
        print("        - donations")
        print("        - audit_logs")
        
        # Create default users
        print("[3/5] Creating default users...")
        
        users_data = [
            {
                'id': 'user_admin_001',
                'email': 'admin@alumni.edu',
                'name': 'Admin User',
                'password': 'admin123',
                'role': 'admin'
            },
            {
                'id': 'user_001',
                'email': 'user@alumni.edu',
                'name': 'Regular User',
                'password': 'user123',
                'role': 'user'
            },
            {
                'id': 'user_002',
                'email': 'coordinator@alumni.edu',
                'name': 'Alumni Coordinator',
                'password': 'coord123',
                'role': 'user'
            }
        ]
        
        for user_data in users_data:
            user = User(
                id=user_data['id'],
                email=user_data['email'],
                name=user_data['name'],
                role=user_data['role'],
                is_active=True
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"      ✓ Created user: {user_data['email']} (role: {user_data['role']})")
        
        db.session.commit()
        
        # Create sample alumni
        print("[4/5] Creating sample alumni...")
        
        alumni_data = [
            {
                'id': 'ALUM001',
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'graduation_year': 2015,
                'department': 'Computer Science',
                'phone': '555-1001',
                'current_position': 'Senior Software Engineer',
                'current_company': 'Tech Corp',
                'linkedin_url': 'https://linkedin.com/in/johndoe',
                'engagement_score': 0.75,
                'donation_score': 0.85,
                'engagement_level': 'high',
                'total_donations': 5000.00,
                'donation_count': 3,
                'engagement_count': 12
            },
            {
                'id': 'ALUM002',
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'graduation_year': 2018,
                'department': 'Business Administration',
                'phone': '555-1002',
                'current_position': 'Product Manager',
                'current_company': 'Startup Inc',
                'linkedin_url': 'https://linkedin.com/in/janesmith',
                'engagement_score': 0.60,
                'donation_score': 0.55,
                'engagement_level': 'medium',
                'total_donations': 2500.00,
                'donation_count': 2,
                'engagement_count': 8
            },
            {
                'id': 'ALUM003',
                'name': 'Robert Johnson',
                'email': 'robert.johnson@example.com',
                'graduation_year': 2010,
                'department': 'Computer Science',
                'phone': '555-1003',
                'current_position': 'VP of Engineering',
                'current_company': 'Global Tech Solutions',
                'linkedin_url': 'https://linkedin.com/in/robertjohnson',
                'engagement_score': 0.88,
                'donation_score': 0.95,
                'engagement_level': 'high',
                'total_donations': 25000.00,
                'donation_count': 8,
                'engagement_count': 25
            },
            {
                'id': 'ALUM004',
                'name': 'Sarah Williams',
                'email': 'sarah.williams@example.com',
                'graduation_year': 2022,
                'department': 'Engineering',
                'phone': '555-1004',
                'current_position': 'Junior Engineer',
                'current_company': 'Engineering Firm',
                'linkedin_url': 'https://linkedin.com/in/sarahwilliams',
                'engagement_score': 0.45,
                'donation_score': 0.20,
                'engagement_level': 'low',
                'total_donations': 500.00,
                'donation_count': 1,
                'engagement_count': 3
            },
            {
                'id': 'ALUM005',
                'name': 'Michael Brown',
                'email': 'michael.brown@example.com',
                'graduation_year': 2012,
                'department': 'Finance',
                'phone': '555-1005',
                'current_position': 'Financial Manager',
                'current_company': 'Finance Corp',
                'linkedin_url': 'https://linkedin.com/in/michaelbrown',
                'engagement_score': 0.70,
                'donation_score': 0.75,
                'engagement_level': 'high',
                'total_donations': 10000.00,
                'donation_count': 5,
                'engagement_count': 16
            }
        ]
        
        for alum_data in alumni_data:
            alumni = Alumni(
                id=alum_data['id'],
                name=alum_data['name'],
                email=alum_data['email'],
                graduation_year=alum_data['graduation_year'],
                department=alum_data['department'],
                phone=alum_data['phone'],
                current_position=alum_data['current_position'],
                current_company=alum_data['current_company'],
                linkedin_url=alum_data['linkedin_url'],
                engagement_score=alum_data['engagement_score'],
                donation_score=alum_data['donation_score'],
                engagement_level=alum_data['engagement_level'],
                total_donations=alum_data['total_donations'],
                donation_count=alum_data['donation_count'],
                engagement_count=alum_data['engagement_count'],
                last_engagement=datetime.utcnow()
            )
            db.session.add(alumni)
            print(f"      ✓ Created alumni: {alum_data['name']} (ID: {alum_data['id']})")
        
        db.session.commit()
        
        # Create sample engagements
        print("[5/5] Creating sample engagement records...")
        
        engagement_data = [
            {'alumni_id': 'ALUM001', 'event_type': 'attendance', 'description': 'Attended alumni networking event'},
            {'alumni_id': 'ALUM001', 'event_type': 'newsletter', 'description': 'Opened newsletter'},
            {'alumni_id': 'ALUM002', 'event_type': 'email', 'description': 'Responded to survey'},
            {'alumni_id': 'ALUM003', 'event_type': 'mentorship', 'description': 'Mentored current student'},
            {'alumni_id': 'ALUM003', 'event_type': 'attendance', 'description': 'Attended annual gala'},
        ]
        
        for eng_data in engagement_data:
            engagement = Engagement(
                alumni_id=eng_data['alumni_id'],
                event_type=eng_data['event_type'],
                description=eng_data['description'],
                recorded_by_id='user_001',
                source='web'
            )
            db.session.add(engagement)
            print(f"      ✓ Created engagement: {eng_data['alumni_id']} - {eng_data['event_type']}")
        
        db.session.commit()
        
        # Create sample donations
        print("      Creating sample donation records...")
        
        donation_data = [
            {'alumni_id': 'ALUM001', 'amount': 2500, 'fund_type': 'general', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM001', 'amount': 1500, 'fund_type': 'scholarship', 'payment_method': 'bank_transfer'},
            {'alumni_id': 'ALUM001', 'amount': 1000, 'fund_type': 'infrastructure', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM002', 'amount': 2000, 'fund_type': 'scholarship', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM002', 'amount': 500, 'fund_type': 'general', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM003', 'amount': 10000, 'fund_type': 'infrastructure', 'payment_method': 'bank_transfer'},
            {'alumni_id': 'ALUM003', 'amount': 7500, 'fund_type': 'general', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM003', 'amount': 5000, 'fund_type': 'research', 'payment_method': 'bank_transfer'},
            {'alumni_id': 'ALUM003', 'amount': 2500, 'fund_type': 'scholarship', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM004', 'amount': 500, 'fund_type': 'general', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM005', 'amount': 4000, 'fund_type': 'scholarship', 'payment_method': 'bank_transfer'},
            {'alumni_id': 'ALUM005', 'amount': 3000, 'fund_type': 'infrastructure', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM005', 'amount': 2000, 'fund_type': 'research', 'payment_method': 'credit_card'},
            {'alumni_id': 'ALUM005', 'amount': 1000, 'fund_type': 'general', 'payment_method': 'credit_card'},
        ]
        
        admin_user = User.query.filter_by(email='admin@alumni.edu').first()
        for idx, don_data in enumerate(donation_data):
            donation = Donation(
                alumni_id=don_data['alumni_id'],
                amount=don_data['amount'],
                fund_type=don_data['fund_type'],
                payment_method=don_data['payment_method'],
                recorded_by_id=admin_user.id if admin_user else None,
                status='completed',
                currency='USD',
                transaction_id=f"TXN-{don_data['alumni_id']}-{idx:04d}",
                reference_id=f"DONATE-{don_data['alumni_id']}-{idx:04d}"
            )
            db.session.add(donation)
            print(f"      ✓ Created donation: {don_data['alumni_id']} - ${don_data['amount']} ({don_data['fund_type']})")
        
        db.session.commit()
        
        # Import CSV alumni data
        print("      Importing alumni from CSV...")
        try:
            import pandas as pd
            csv_path = os.path.join(os.path.dirname(__file__), 'dataset', 'alumni_people_from_departmant.csv')
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                csv_count = 0
                for idx, row in df.iterrows():
                    # Create unique ID for CSV alumni
                    alumni_id = f"ALUM{str(idx+100).zfill(3)}"  # ALUM100, ALUM101, etc.
                    
                    # Check if already exists
                    if Alumni.query.get(alumni_id):
                        continue
                    
                    # Extract data from CSV
                    name = str(row.get('name', f'Alumni {idx}')).strip()
                    email = str(row.get('email', f'alumni{idx}@alumni.edu')).strip()
                    department = str(row.get('department', 'Unknown')).strip() if 'department' in row else 'Unknown'
                    
                    alumni = Alumni(
                        id=alumni_id,
                        name=name,
                        email=email if '@' in email else f'{name.lower().replace(" ", ".")}@alumni.edu',
                        department=department,
                        graduation_year=int(row.get('graduation_year', 2020)) if 'graduation_year' in row and pd.notna(row.get('graduation_year')) else 2020,
                        phone='',
                        current_position='',
                        current_company='',
                        engagement_score=0.0,
                        donation_score=0.0,
                        engagement_level='low',
                        total_donations=0.0,
                        donation_count=0,
                        engagement_count=0
                    )
                    db.session.add(alumni)
                    csv_count += 1
                    
                    # Print progress every 50 alumni
                    if csv_count % 50 == 0:
                        print(f"      ✓ Imported {csv_count} alumni from CSV...")
                
                db.session.commit()
                print(f"      ✓ Imported {csv_count} alumni from CSV file")
            else:
                print(f"      ⚠ CSV file not found at {csv_path}")
        except ImportError:
            print("      ⚠ pandas not installed, skipping CSV import")
        except Exception as csv_err:
            print(f"      ⚠ Error importing CSV: {str(csv_err)}")
        
        print()
        print("=" * 70)
        print("  ✅ Database initialization complete!")
        print("=" * 70)
        print()
        print("📊 Database Statistics:")
        print(f"   Users: {User.query.count()}")
        print(f"   Alumni: {Alumni.query.count()}")
        print(f"   Engagements: {Engagement.query.count()}")
        print(f"   Donations: {Donation.query.count()}")
        print()
        print("🔐 Test Credentials:")
        print("   Admin:")
        print("     Email: admin@alumni.edu")
        print("     Password: admin123")
        print()
        print("   User:")
        print("     Email: user@alumni.edu")
        print("     Password: user123")
        print()
        print("💾 Database location: alumni.db")
        print()


if __name__ == '__main__':
    init_database()
