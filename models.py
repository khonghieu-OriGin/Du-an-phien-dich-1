from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class LanguageItem(dict):
    def __init__(self, name, flag, cert, code, short_name=None):
        short = short_name or name.replace('Tiếng ', '')
        code_lower = code.lower()
        flag_svg = f"/static/flags/{code_lower}.svg"
        flag_alt = f"Quốc kỳ {short}"
        super().__init__(
            name=name,
            flag=flag,
            cert=cert,
            code=code,
            short_name=short,
            code_lower=code_lower,
            flag_svg=flag_svg,
            flag_alt=flag_alt,
        )
        self.__dict__ = self

    def __iter__(self):
        return iter((self['name'], self['flag'], self['cert']))


LANGUAGES = [
    LanguageItem('Tiếng Anh', '🇬🇧', 'IELTS / TOEIC / VSTEP', 'GB'),
    LanguageItem('Tiếng Nhật', '🇯🇵', 'JLPT N2 trở lên', 'JP'),
    LanguageItem('Tiếng Hàn', '🇰🇷', 'TOPIK 4 trở lên', 'KR'),
    LanguageItem('Tiếng Trung', '🇨🇳', 'HSK 5 trở lên', 'CN'),
    LanguageItem('Tiếng Pháp', '🇫🇷', 'DELF B2 trở lên', 'FR'),
    LanguageItem('Tiếng Đức', '🇩🇪', 'TestDaF / Goethe B2', 'DE'),
    LanguageItem('Tiếng Nga', '🇷🇺', 'ТРКИ B2 trở lên', 'RU'),
    LanguageItem('Tiếng Thái', '🇹🇭', 'Kiểm tra trực tiếp', 'TH'),
    LanguageItem('Tiếng Bồ Đào Nha', '🇵🇹', 'CELPE-Bras', 'PT'),
    LanguageItem('Tiếng Tây Ban Nha', '🇪🇸', 'DELE B2 trở lên', 'ES'),
]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)  # 'hirer', 'translator', 'admin'
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('TranslatorProfile', backref='user', uselist=False)
    jobs_posted = db.relationship('Job', backref='hirer', lazy=True)
    proposals = db.relationship('Proposal', backref='translator', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    direct_messages_sent = db.relationship('DirectMessage', foreign_keys='DirectMessage.sender_id', backref='sender', lazy=True)


class TranslatorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200))
    bio = db.Column(db.Text)
    languages = db.Column(db.String(300))
    badges = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    total_jobs = db.Column(db.Integer, default=0)
    response_time = db.Column(db.String(50), default='2 giờ')
    is_verified = db.Column(db.Boolean, default=False)

    services = db.relationship('Service', backref='profile', lazy=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('translator_profile.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    languages = db.Column(db.String(100))
    category = db.Column(db.String(100))
    basic_price = db.Column(db.Integer, nullable=False)
    standard_price = db.Column(db.Integer)
    premium_price = db.Column(db.Integer)
    basic_delivery = db.Column(db.String(50), default='3 ngày')
    standard_delivery = db.Column(db.String(50), default='2 ngày')
    premium_delivery = db.Column(db.String(50), default='1 ngày')


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hirer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    source_lang = db.Column(db.String(50))
    target_lang = db.Column(db.String(50))
    budget_type = db.Column(db.String(20))
    budget_min = db.Column(db.Integer)
    budget_max = db.Column(db.Integer)
    # Lịch và thời gian
    event_date = db.Column(db.String(100))          # Ngày diễn ra sự kiện / cần dịch
    event_time_start = db.Column(db.String(10))  # Giờ bắt đầu VD: "08:00"
    event_time_end = db.Column(db.String(10))    # Giờ kết thúc VD: "17:00"
    event_location = db.Column(db.String(200))   # Địa điểm hoặc "Online"
    deadline = db.Column(db.Date)            # Hạn nộp hồ sơ đề xuất
    status = db.Column(db.String(20), default='open')
    is_flagged = db.Column(db.Boolean, default=False)  # Admin flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    proposals = db.relationship('Proposal', backref='job', lazy=True)
    contract = db.relationship('Contract', backref='job', uselist=False)


class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    translator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time_estimate = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=True)
    hirer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    translator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agreed_price = db.Column(db.Integer, nullable=False)
    # Lịch hẹn được chốt khi tạo Contract (lưu String vì có thể là khoảng ngày)
    scheduled_date = db.Column(db.String(100))
    scheduled_time_start = db.Column(db.String(10))
    scheduled_time_end = db.Column(db.String(10))
    location = db.Column(db.String(200))
    status = db.Column(db.String(50), default='escrow_pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hirer = db.relationship('User', foreign_keys=[hirer_id], backref='contracts_as_hirer')
    translator = db.relationship('User', foreign_keys=[translator_id], backref='contracts_as_translator')
    messages = db.relationship('Message', backref='contract', lazy=True)
    deliverables = db.relationship('Deliverable', backref='contract', lazy=True)
    reviews = db.relationship('Review', backref='contract', lazy=True)
    service = db.relationship('Service', backref='contracts')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DirectMessage(db.Model):
    """Tin nhắn trực tiếp không gắn với contract - dùng khi chat hỏi thăm"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='direct_messages_received')


class Deliverable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_given')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref='reviews_received')
