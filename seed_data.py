from app import app, db
from models import User, TranslatorProfile, Service, Job
from werkzeug.security import generate_password_hash
from datetime import date

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # === USERS ===
        admin = User(name='Admin VietTranslate', email='admin@vt.com',
                     password_hash=generate_password_hash('admin123'),
                     role='admin', is_admin=True)
        hirer1 = User(name='Nguyễn Văn A', email='hirer@test.com',
                      password_hash=generate_password_hash('123456'), role='hirer')
        hirer2 = User(name='Công ty ABC Ltd', email='hirer2@test.com',
                      password_hash=generate_password_hash('123456'), role='hirer')
        trans1 = User(name='Trần Thị Bích', email='trans1@test.com',
                      password_hash=generate_password_hash('123456'), role='translator')
        trans2 = User(name='Lê Văn Cường', email='trans2@test.com',
                      password_hash=generate_password_hash('123456'), role='translator')
        trans3 = User(name='Phạm Thị Dung', email='trans3@test.com',
                      password_hash=generate_password_hash('123456'), role='translator')
        trans4 = User(name='Hoàng Minh Đức', email='trans4@test.com',
                      password_hash=generate_password_hash('123456'), role='translator')

        db.session.add_all([admin, hirer1, hirer2, trans1, trans2, trans3, trans4])
        db.session.commit()

        # === TRANSLATOR PROFILES ===
        prof1 = TranslatorProfile(
            user_id=trans1.id,
            title='Chuyên gia phiên dịch tiếng Nhật (JLPT N1)',
            bio='Tôi có 7 năm kinh nghiệm phiên dịch cabin và tháp tùng cho các tập đoàn Nhật Bản tại Việt Nam. Từng phiên dịch cho Toyota, Honda, Fujitsu.',
            languages='Tiếng Nhật, Tiếng Anh',
            badges='Rising Star, Local Champion',
            rating=4.8, total_reviews=25, total_jobs=30, is_verified=True
        )
        prof2 = TranslatorProfile(
            user_id=trans2.id,
            title='Biên/Phiên dịch viên tiếng Anh - Pháp chuyên ngành pháp lý',
            bio='Thạc sĩ Luật quốc tế, có 5 năm dịch hợp đồng, tài liệu pháp lý và phiên dịch hội thảo cho các tổ chức quốc tế.',
            languages='Tiếng Anh, Tiếng Pháp',
            badges='Rehire Badge',
            rating=4.6, total_reviews=18, total_jobs=22, is_verified=True
        )
        prof3 = TranslatorProfile(
            user_id=trans3.id,
            title='Phiên dịch viên tiếng Hàn (TOPIK 6) - Chuyên ngành kỹ thuật',
            bio='6 năm làm việc tại Hàn Quốc, chuyên dịch hội nghị kỹ thuật, nhà máy sản xuất Samsung, LG.',
            languages='Tiếng Hàn, Tiếng Anh',
            badges='Local Champion',
            rating=4.9, total_reviews=42, total_jobs=55, is_verified=True
        )
        prof4 = TranslatorProfile(
            user_id=trans4.id,
            title='Phiên dịch tiếng Trung - Tiếng Đức đa lĩnh vực',
            bio='Tốt nghiệp HSK 6 và tiếng Đức C1. Có kinh nghiệm dịch thương mại và du lịch.',
            languages='Tiếng Trung, Tiếng Đức',
            badges='Rising Star',
            rating=4.3, total_reviews=8, total_jobs=10, is_verified=False
        )

        db.session.add_all([prof1, prof2, prof3, prof4])
        db.session.commit()

        # === SERVICES ===
        services = [
            Service(profile_id=prof1.id, name='Phiên dịch tháp tùng tiếng Nhật',
                    description='Đi cùng đoàn khách Nhật tại sự kiện, hội nghị, thăm quan nhà máy.',
                    category='Tháp tùng', languages='Việt ↔ Nhật',
                    basic_price=1500000, standard_price=2500000, premium_price=4000000,
                    basic_delivery='1 ngày', standard_delivery='Nửa ngày', premium_delivery='Theo yêu cầu'),
            Service(profile_id=prof1.id, name='Biên dịch tài liệu tiếng Nhật',
                    description='Dịch hợp đồng, email, tài liệu kỹ thuật Nhật-Việt.',
                    category='Dịch viết', languages='Việt ↔ Nhật',
                    basic_price=300000, standard_price=500000, premium_price=900000,
                    basic_delivery='3 ngày', standard_delivery='2 ngày', premium_delivery='Trong ngày'),
            Service(profile_id=prof2.id, name='Phiên dịch cabin hội thảo tiếng Anh',
                    description='Dịch cabin đồng thời trong hội nghị quốc tế, đảm bảo tốc độ và chính xác.',
                    category='Cabin', languages='Việt ↔ Anh',
                    basic_price=3000000, standard_price=4500000, premium_price=7000000,
                    basic_delivery='Theo lịch', standard_delivery='Theo lịch', premium_delivery='Theo lịch'),
            Service(profile_id=prof3.id, name='Phiên dịch hội nghị tiếng Hàn',
                    description='Dịch hội nghị kỹ thuật, đào tạo nội bộ, meeting doanh nghiệp Hàn Quốc.',
                    category='Hội nghị', languages='Việt ↔ Hàn',
                    basic_price=2000000, standard_price=3200000, premium_price=5000000,
                    basic_delivery='Theo lịch', standard_delivery='Theo lịch', premium_delivery='Theo lịch'),
            Service(profile_id=prof4.id, name='Biên dịch tiếng Trung chuyên ngành thương mại',
                    description='Dịch hợp đồng thương mại, catalogue sản phẩm, email kinh doanh.',
                    category='Dịch viết', languages='Việt ↔ Trung',
                    basic_price=250000, standard_price=400000, premium_price=700000,
                    basic_delivery='3 ngày', standard_delivery='2 ngày', premium_delivery='Trong ngày'),
        ]
        db.session.add_all(services)
        db.session.commit()

        # === JOBS ===
        jobs = [
            Job(hirer_id=hirer1.id,
                title='Cần phiên dịch hội thảo IT Tiếng Nhật (1 ngày)',
                description='Hội thảo giới thiệu sản phẩm phần mềm tại Q1 HCM. Yêu cầu JLPT N2 trở lên, có hiểu biết IT.',
                category='Hội thảo', source_lang='Tiếng Việt', target_lang='Tiếng Nhật',
                budget_type='range', budget_min=2000000, budget_max=4000000,
                event_date=date(2026, 9, 15), event_time_start='08:00', event_time_end='17:00',
                event_location='FPT Tower, Quận 7, TP.HCM',
                deadline=date(2026, 9, 10)),
            Job(hirer_id=hirer1.id,
                title='Dịch 15 trang hợp đồng mua bán Tiếng Anh',
                description='Hợp đồng mua bán thiết bị điện tử giữa công ty VN và đối tác Mỹ. Cần dịch chuyên nghiệp, có bảo mật NDA.',
                category='Dịch viết', source_lang='Tiếng Anh', target_lang='Tiếng Việt',
                budget_type='fixed', budget_min=700000,
                event_date=None, deadline=date(2026, 9, 8)),
            Job(hirer_id=hirer2.id,
                title='Phiên dịch tháp tùng đoàn khách Hàn Quốc (3 ngày)',
                description='Đoàn 8 người từ Samsung Hàn Quốc thăm quan nhà máy tại Bình Dương. Cần phiên dịch chuyên nghiệp, có kinh nghiệm kỹ thuật sản xuất.',
                category='Tháp tùng', source_lang='Tiếng Hàn', target_lang='Tiếng Việt',
                budget_type='range', budget_min=5000000, budget_max=9000000,
                event_date=date(2026, 9, 20), event_time_start='07:30', event_time_end='18:00',
                event_location='KCN VSIP, Bình Dương',
                deadline=date(2026, 9, 12)),
        ]
        db.session.add_all(jobs)
        db.session.commit()


if __name__ == '__main__':
    seed_data()
    print('Seeded successfully!')
