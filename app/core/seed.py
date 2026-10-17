from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.auth.models import User, UserRole
from app.core.security import hash_password
from app.businesses.models import Business, Product
from app.workforce.models import WorkerProfile, Job, JobStatus
from app.work_records.models import WorkRecord, VerificationStatus

def run_seed():
    db = SessionLocal()
    try:
        # Cek apakah seed sudah pernah dijalankan
        existing_user = db.query(User).filter(User.email == "employer@nusa.test").first()
        if existing_user:
            print("Seed data sudah ada di database.")
            return

        # 1. Buat User Employer
        employer = User(
            email="employer@nusa.test",
            password_hash=hash_password("Password123!"),
            role=UserRole.EMPLOYER
        )
        db.add(employer)
        
        # 2. Buat User Worker
        worker = User(
            email="worker@nusa.test",
            password_hash=hash_password("Password123!"),
            role=UserRole.WORKER
        )
        db.add(worker)
        db.commit()
        db.refresh(employer)
        db.refresh(worker)

        # 3. Buat Profil Bisnis
        business = Business(
            name="Kopi Senja Nusantara",
            category="F&B",
            location="Malang",
            owner_user_id=employer.id
        )
        db.add(business)
        db.commit()
        db.refresh(business)

        # 4. Buat Produk Contoh
        product = Product(
            business_id=business.id,
            name="Kopi Susu Gula Aren",
            price=18000.00,
            is_active=1
        )
        db.add(product)

        # 5. Buat Profil Pekerja
        worker_profile = WorkerProfile(
            user_id=worker.id,
            display_name="Ahmad Barista",
            summary="Berpengalaman dalam meracik kopi dan melayani pelanggan UMKM.",
            location="Malang",
            availability="Full-time"
        )
        db.add(worker_profile)

        # 6. Buat Lowongan Kerja (Job Posting)
        job = Job(
            business_id=business.id,
            title="Barista Full-Time",
            description="Mencari barista berpengalaman untuk kedai kopi.",
            location="Malang",
            employment_type="Full-time",
            requirements="Pengalaman min. 1 tahun di bidang F&B, ramah, dan jujur.",
            status=JobStatus.OPEN
        )
        db.add(job)

        # 7. Buat Work Record (Contoh Rekam Kerja)
        work_record = WorkRecord(
            business_id=business.id,
            worker_user_id=worker.id,
            title="Barista Utama",
            tasks="Meracik minuman, menjaga kebersihan kedai, dan mengelola stok bahan baku.",
            skills="Pembuatan Kopi, Manajemen Stok, Pelayanan Pelanggan",
            start_date="2025-01-01",
            end_date="2025-12-31",
            verification_status=VerificationStatus.VERIFIED
        )
        db.add(work_record)

        db.commit()
        print("Seed data demo berhasil dimasukkan ke database!")
    except Exception as e:
        db.rollback()
        print(f"Gagal melakukan seeding data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()