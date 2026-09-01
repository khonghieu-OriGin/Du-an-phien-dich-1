import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, TranslatorProfile, Service, Job, Proposal, Contract, Message, DirectMessage, Deliverable, Review, LANGUAGES
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

# ─── DECORATORS ────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user, LANGUAGES=LANGUAGES)

# ─── PUBLIC ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    top_translators = TranslatorProfile.query.filter_by(is_verified=True).order_by(
        TranslatorProfile.rating.desc()).limit(4).all()
    return render_template('index.html', top_translators=top_translators)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/payment-info')
def payment_info():
    return render_template('payment_info.html')

# ─── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.is_active and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Đăng nhập thành công!', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Email hoặc mật khẩu không đúng, hoặc tài khoản đã bị khoá.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng.', 'error')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email,
                        password_hash=generate_password_hash(password),
                        phone=phone, role=role)
        db.session.add(new_user)
        db.session.commit()

        if role == 'translator':
            profile = TranslatorProfile(user_id=new_user.id)
            db.session.add(profile)
            db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Đã đăng xuất.', 'success')
    return redirect(url_for('index'))

# ─── ACCOUNT ───────────────────────────────────────────────────────────────────

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account_profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action', 'basic')

        if action == 'basic':
            user.name = request.form.get('name', user.name).strip()
            user.phone = request.form.get('phone', user.phone or '').strip()
            db.session.commit()
            flash('Đã cập nhật thông tin cơ bản!', 'success')

        elif action == 'translator_profile' and user.role == 'translator':
            profile = user.profile
            if not profile:
                profile = TranslatorProfile(user_id=user.id)
                db.session.add(profile)
            profile.title = request.form.get('title', '').strip()
            profile.bio = request.form.get('bio', '').strip()
            profile.languages = request.form.get('languages', '').strip()
            profile.badges = request.form.get('badges', '').strip()
            profile.response_time = request.form.get('response_time', '< 1 giờ').strip()
            db.session.commit()
            flash('Đã cập nhật hồ sơ phiên dịch viên!', 'success')

        elif action == 'change_password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')
            if not check_password_hash(user.password_hash, old_pw):
                flash('Mật khẩu hiện tại không đúng.', 'error')
            elif new_pw != confirm_pw:
                flash('Mật khẩu mới không khớp.', 'error')
            elif len(new_pw) < 6:
                flash('Mật khẩu mới phải ít nhất 6 ký tự.', 'error')
            else:
                user.password_hash = generate_password_hash(new_pw)
                db.session.commit()
                flash('Đã đổi mật khẩu thành công!', 'success')

        return redirect(url_for('account_profile'))
    return render_template('account_profile.html', user=user)

@app.route('/account/history')
@login_required
def account_history():
    user = User.query.get(session['user_id'])
    if user.role == 'hirer':
        contracts = Contract.query.filter_by(hirer_id=user.id).order_by(Contract.created_at.desc()).all()
    else:
        contracts = Contract.query.filter_by(translator_id=user.id).order_by(Contract.created_at.desc()).all()
    return render_template('account_history.html', user=user, contracts=contracts)

# ─── FLOW 1: TÌM PHIÊN DỊCH VIÊN ──────────────────────────────────────────────

@app.route('/translator')
def translator_list():
    lang = request.args.get('lang', '')
    rating_filter = request.args.get('rating', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9

    query = TranslatorProfile.query
    if lang:
        query = query.filter(TranslatorProfile.languages.ilike(f'%{lang}%'))
    if rating_filter:
        query = query.filter(TranslatorProfile.rating >= float(rating_filter))

    pagination = query.order_by(TranslatorProfile.rating.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('translator_list.html', profiles=pagination.items,
                           pagination=pagination, lang_filter=lang, LANGUAGES=LANGUAGES)

@app.route('/translator/<int:profile_id>')
def translator_profile(profile_id):
    profile = TranslatorProfile.query.get_or_404(profile_id)
    # Reviews received by this translator
    reviews = Review.query.filter_by(reviewee_id=profile.user_id).order_by(Review.created_at.desc()).limit(10).all()
    return render_template('translator_profile.html', profile=profile, reviews=reviews)

# ─── DIRECT CHAT ───────────────────────────────────────────────────────────────

@app.route('/chat/<int:translator_user_id>')
@login_required
def direct_chat(translator_user_id):
    if session['user_id'] == translator_user_id:
        return redirect(url_for('index'))
    translator = User.query.get_or_404(translator_user_id)
    return render_template('chat.html', other_user=translator)

@app.route('/api/direct-messages/<int:other_user_id>')
@login_required
def get_direct_messages(other_user_id):
    me = session['user_id']
    msgs = DirectMessage.query.filter(
        db.or_(
            db.and_(DirectMessage.sender_id == me, DirectMessage.receiver_id == other_user_id),
            db.and_(DirectMessage.sender_id == other_user_id, DirectMessage.receiver_id == me)
        )
    ).order_by(DirectMessage.created_at.asc()).all()
    return jsonify([{
        'id': m.id, 'sender_id': m.sender_id, 'sender_name': m.sender.name,
        'content': m.content, 'time': m.created_at.strftime('%H:%M %d/%m')
    } for m in msgs])

@app.route('/api/direct-messages/<int:other_user_id>', methods=['POST'])
@login_required
def send_direct_message(other_user_id):
    content = request.json.get('content', '').strip()
    if content:
        msg = DirectMessage(sender_id=session['user_id'], receiver_id=other_user_id, content=content)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400

# ─── DIRECT BOOKING ────────────────────────────────────────────────────────────

@app.route('/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book_service(service_id):
    service = Service.query.get_or_404(service_id)
    tier = request.args.get('tier', 'basic')
    prices = {'basic': service.basic_price, 'standard': service.standard_price,
              'premium': service.premium_price}
    price = prices.get(tier, service.basic_price)

    if request.method == 'POST':
        contract = Contract(
            service_id=service.id,
            hirer_id=session['user_id'],
            translator_id=service.profile.user_id,
            agreed_price=int(request.form.get('price', price)),
            scheduled_date=request.form.get('scheduled_date', ''),
            scheduled_time_start=request.form.get('time_start', ''),
            scheduled_time_end=request.form.get('time_end', ''),
            location=request.form.get('location', ''),
            status='escrow_pending'
        )
        db.session.add(contract)
        db.session.commit()
        flash('Đặt dịch vụ thành công! Vui lòng thanh toán Escrow để bắt đầu.', 'success')
        return redirect(url_for('payment_mockup', contract_id=contract.id))

    # Extract fixed_days from delivery string
    delivery_str = service.basic_delivery if tier == 'basic' else (service.standard_delivery if tier == 'standard' else service.premium_delivery)
    fixed_days = None
    if delivery_str:
        s = delivery_str.lower()
        if 'nửa ngày' in s or 'trong ngày' in s:
            fixed_days = 1
        elif 'theo' not in s:  # Not "theo yêu cầu", "theo lịch"
            import re
            match = re.search(r'(\d+)', s)
            if match:
                fixed_days = int(match.group(1))

    return render_template('book_service.html', service=service, tier=tier, price=price, fixed_days=fixed_days)

# ─── FLOW 2: JOB BOARD ─────────────────────────────────────────────────────────

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if request.method == 'POST':
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None

        job = Job(
            hirer_id=session['user_id'],
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            source_lang=request.form.get('source_lang'),
            target_lang=request.form.get('target_lang'),
            budget_type=request.form.get('budget_type'),
            budget_min=int(request.form.get('budget_min') or 0),
            event_date=request.form.get('event_date', ''),
            event_time_start=request.form.get('event_time_start', ''),
            event_time_end=request.form.get('event_time_end', ''),
            event_location=request.form.get('event_location', ''),
            deadline=deadline
        )
        db.session.add(job)
        db.session.commit()
        flash('Đã đăng việc thành công!', 'success')
        return redirect(url_for('job_list'))
    return render_template('post_job.html', LANGUAGES=LANGUAGES)

@app.route('/jobs')
def job_list():
    lang = request.args.get('lang', '')
    budget = request.args.get('budget', '')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Job.query.filter_by(status='open', is_flagged=False)
    if lang:
        query = query.filter(db.or_(Job.source_lang.ilike(f'%{lang}%'), Job.target_lang.ilike(f'%{lang}%')))

    if sort == 'budget_desc':
        query = query.order_by(Job.budget_min.desc())
    else:
        query = query.order_by(Job.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('job_list.html', jobs=pagination.items, pagination=pagination,
                           lang_filter=lang, LANGUAGES=LANGUAGES)

@app.route('/job/<int:job_id>', methods=['GET', 'POST'])
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để gửi đề xuất.', 'warning')
            return redirect(url_for('login'))
        proposal = Proposal(
            job_id=job.id,
            translator_id=session['user_id'],
            cover_letter=request.form.get('cover_letter'),
            price=int(request.form.get('price') or 0),
            time_estimate=request.form.get('time_estimate')
        )
        db.session.add(proposal)
        db.session.commit()
        flash('Đề xuất của bạn đã được gửi!', 'success')
        return redirect(url_for('job_detail', job_id=job.id))
    return render_template('job_detail.html', job=job)

# ─── CONTRACT / BUSINESS PROCESS ───────────────────────────────────────────────

@app.route('/accept-proposal/<int:proposal_id>', methods=['POST'])
@login_required
def accept_proposal(proposal_id):
    proposal = Proposal.query.get_or_404(proposal_id)
    job = proposal.job
    if job.hirer_id != session['user_id']:
        flash('Không có quyền.', 'error')
        return redirect(url_for('index'))

    contract = Contract(
        job_id=job.id,
        proposal_id=proposal.id,
        hirer_id=job.hirer_id,
        translator_id=proposal.translator_id,
        agreed_price=proposal.price,
        scheduled_date=job.event_date,
        scheduled_time_start=job.event_time_start,
        scheduled_time_end=job.event_time_end,
        location=job.event_location,
        status='escrow_pending'
    )
    job.status = 'contracted'
    proposal.status = 'accepted'
    db.session.add(contract)
    db.session.commit()
    flash('Đã chấp nhận đề xuất! Vui lòng thanh toán để bắt đầu.', 'success')
    return redirect(url_for('payment_mockup', contract_id=contract.id))

@app.route('/payment-mockup/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def payment_mockup(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    platform_fee = int(contract.agreed_price * 0.10)
    translator_receives = contract.agreed_price - platform_fee
    if request.method == 'POST':
        contract.status = 'in_progress'
        db.session.commit()
        flash('Thanh toán thành công! Tiền đã được giữ trong Escrow an toàn.', 'success')
        return redirect(url_for('transaction_detail', contract_id=contract.id))
    return render_template('payment_mockup.html', contract=contract,
                           platform_fee=platform_fee, translator_receives=translator_receives)

@app.route('/transaction/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def transaction_detail(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if session['user_id'] not in [contract.hirer_id, contract.translator_id]:
        flash('Không có quyền truy cập.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST' and 'file' in request.files:
        if contract.status == 'in_progress' and session['user_id'] == contract.translator_id:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                db.session.add(Deliverable(contract_id=contract.id, filename=filename, filepath=filename))
                db.session.add(Message(contract_id=contract.id, sender_id=session['user_id'],
                                       content=f'📎 Đã gửi tệp: {filename}'))
                db.session.commit()
                flash('Đã gửi tài liệu thành công.', 'success')

    return render_template('transaction_detail.html', contract=contract)

@app.route('/approve-contract/<int:contract_id>', methods=['POST'])
@login_required
def approve_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if session['user_id'] == contract.hirer_id and contract.status == 'in_progress':
        contract.status = 'completed'
        if contract.job:
            contract.job.status = 'completed'
        prof = TranslatorProfile.query.filter_by(user_id=contract.translator_id).first()
        if prof:
            prof.total_jobs += 1
        db.session.commit()
        flash('Nghiệm thu thành công! Tiền Escrow đã được giải ngân.', 'success')
    return redirect(url_for('transaction_detail', contract_id=contract.id))

@app.route('/submit-review/<int:contract_id>', methods=['POST'])
@login_required
def submit_review(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if contract.status == 'completed':
        rating = int(request.form.get('rating', 5))
        comment = request.form.get('comment', '')
        reviewee_id = contract.translator_id if session['user_id'] == contract.hirer_id else contract.hirer_id

        existing = Review.query.filter_by(contract_id=contract.id, reviewer_id=session['user_id']).first()
        if existing:
            flash('Bạn đã đánh giá giao dịch này rồi.', 'warning')
            return redirect(url_for('transaction_detail', contract_id=contract.id))

        db.session.add(Review(contract_id=contract.id, reviewer_id=session['user_id'],
                              reviewee_id=reviewee_id, rating=rating, comment=comment))

        if session['user_id'] == contract.hirer_id:
            prof = TranslatorProfile.query.filter_by(user_id=contract.translator_id).first()
            if prof:
                total = (prof.rating * prof.total_reviews) + rating
                prof.total_reviews += 1
                prof.rating = round(total / prof.total_reviews, 1)

        db.session.commit()
        flash('Cảm ơn bạn đã đánh giá!', 'success')
    return redirect(url_for('transaction_detail', contract_id=contract.id))

# ─── CHAT API (CONTRACT) ────────────────────────────────────────────────────────

@app.route('/api/messages/<int:contract_id>')
@login_required
def get_messages(contract_id):
    msgs = Message.query.filter_by(contract_id=contract_id).order_by(Message.created_at.asc()).all()
    return jsonify([{'id': m.id, 'sender_id': m.sender_id, 'sender_name': m.sender.name,
                     'content': m.content, 'time': m.created_at.strftime('%H:%M %d/%m')} for m in msgs])

@app.route('/api/messages/<int:contract_id>', methods=['POST'])
@login_required
def send_message(contract_id):
    content = request.json.get('content', '').strip()
    if content:
        db.session.add(Message(contract_id=contract_id, sender_id=session['user_id'], content=content))
        db.session.commit()
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400

# ─── ADMIN ROUTES ───────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.filter_by(is_admin=False).count(),
        'total_translators': TranslatorProfile.query.count(),
        'pending_verify': TranslatorProfile.query.filter_by(is_verified=False).count(),
        'open_jobs': Job.query.filter_by(status='open', is_flagged=False).count(),
        'flagged_jobs': Job.query.filter_by(is_flagged=True).count(),
        'active_contracts': Contract.query.filter_by(status='in_progress').count(),
        'completed_contracts': Contract.query.filter_by(status='completed').count(),
    }
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()
    return render_template('admin_dashboard.html', stats=stats, recent_users=recent_users, recent_jobs=recent_jobs)

@app.route('/admin/jobs')
@admin_required
def admin_jobs():
    status_filter = request.args.get('status', 'all')
    query = Job.query
    if status_filter == 'flagged':
        query = query.filter_by(is_flagged=True)
    elif status_filter == 'open':
        query = query.filter_by(status='open', is_flagged=False)
    elif status_filter == 'completed':
        query = query.filter_by(status='completed')
    jobs = query.order_by(Job.created_at.desc()).all()
    return render_template('admin_jobs.html', jobs=jobs, status_filter=status_filter)

@app.route('/admin/jobs/<int:job_id>/flag', methods=['POST'])
@admin_required
def admin_flag_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_flagged = not job.is_flagged
    db.session.commit()
    action = 'Đã gỡ bỏ' if job.is_flagged else 'Đã khôi phục'
    flash(f'{action} bài đăng "{job.title}".', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
@admin_required
def admin_delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Đã xoá vĩnh viễn bài đăng.', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/users')
@admin_required
def admin_users():
    role_filter = request.args.get('role', 'all')
    query = User.query.filter_by(is_admin=False)
    if role_filter == 'hirer':
        query = query.filter_by(role='hirer')
    elif role_filter == 'translator':
        query = query.filter_by(role='translator')
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users, role_filter=role_filter)

@app.route('/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'kích hoạt' if user.is_active else 'khoá'
    flash(f'Đã {status} tài khoản {user.name}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/translators')
@admin_required
def admin_translators():
    show = request.args.get('show', 'pending')
    if show == 'verified':
        profiles = TranslatorProfile.query.filter_by(is_verified=True).all()
    else:
        profiles = TranslatorProfile.query.filter_by(is_verified=False).all()
    return render_template('admin_translators.html', profiles=profiles, show=show)

@app.route('/admin/translators/<int:profile_id>/verify', methods=['POST'])
@admin_required
def admin_verify_translator(profile_id):
    profile = TranslatorProfile.query.get_or_404(profile_id)
    action = request.form.get('action')
    profile.is_verified = (action == 'verify')
    db.session.commit()
    msg = 'Đã xác minh' if profile.is_verified else 'Đã từ chối xác minh'
    flash(f'{msg} hồ sơ {profile.user.name}.', 'success')
    return redirect(url_for('admin_translators'))

if __name__ == '__main__':
    app.run(debug=True)
