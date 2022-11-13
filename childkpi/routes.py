from flask import render_template, redirect, url_for, flash, request
from childkpi import app
from childkpi import db
from childkpi.models import User, Result
from childkpi.forms import RegisterForm, LoginForm, BinaryAnswerForm, NumberAnswerForm, SportAnswerForm, DatePicker
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date as dt, timedelta as td
import calendar


def create_empty_row(date):
    row = Result(date=date)
    db.session.add(row)
    db.session.commit()


def calculate_daily_fee(results):
    results = [0 if v is None else int(v) for v in results]
    eligible_results = [v for i, v in enumerate(results) if v >= current_threshold[i]]
    fee = round(sum([v * current_rates[i]/100 for i, v in enumerate(eligible_results)]), 2)
    return fee


def calculate_monthly_income(month):
    fees = [0.0, 0.0]

    sql1 = f'''
            select sum(amount) 
            from results 
            where 
                is_approved = True and 
                extract(month from date) = {month} and 
                extract(day from date) <= 15 
            group by 
                extract(month from date)
            '''

    sql2 = f'''
            select sum(amount) 
            from results 
            where 
                is_approved = True and 
                extract(month from date) = {month} and 
                extract(day from date) > 15 
            group by 
                extract(month from date)
            '''

    r = [v for v, in db.engine.execute(sql1)]
    if r:
        fees[0] = float(r[0])

    r = [v for v, in db.engine.execute(sql2)]
    if r:
        fees[1] = float(r[0])

    return fees



active_date = dt.today()
current_rates = [100, 100, 100, 100]
current_threshold = [100, 50, 75, 0]
cur_row = Result.query.filter_by(date=active_date).first()
if not cur_row:
    create_empty_row(active_date)


@app.route("/")
def intro_page():
    return render_template('intro.html')


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home_page():
    global active_date
    date_picker_form = DatePicker(entrydate=active_date)

    if date_picker_form.validate_on_submit():
        new_date = date_picker_form.entrydate.data
        active_date = new_date
        return redirect(url_for('home_page'))

    from_ = active_date - td(days=3)
    to_ = active_date + td(days=3)
    recent_rows = [v for v, in db.session.execute(db.select(Result).where(Result.date.between(from_, to_)).order_by(Result.date)).all()]
    cur_row = Result.query.filter_by(date=active_date).first()

    if not cur_row:
        create_empty_row(date=active_date)
        flash('No records found. Empty row is added.', category='success')
        return redirect(url_for('home_page'))

    if current_user.is_parent:
        if cur_row.is_done and not cur_row.is_approved:
            butt = 'Approve'
            but_design = 'btn btn-success btn-sm'
        elif cur_row.is_done and cur_row.is_approved:
            butt = 'Unapprove'
            but_design = 'btn btn-info btn-sm'
        else:
            butt = but_design = ''
    else:
        if not cur_row.is_done:
            butt = 'Done'
            but_design = 'btn btn-success btn-sm'
        elif cur_row.is_done and not cur_row.is_approved:
            butt = 'Undone'
            but_design = 'btn btn-info btn-sm'
        else:
            butt = but_design = ''

    if request.method == 'POST':
        if current_user.is_parent:
            cur_row.is_approved = not cur_row.is_approved
        else:
            cur_row.is_done = not cur_row.is_done
        db.session.commit()
        flash('Record updated.')
        return redirect(url_for('home_page'))

    fees = calculate_monthly_income(active_date.month)

    return render_template('home.html',
                           form=date_picker_form,
                           date=active_date,
                           items=recent_rows,
                           butt=butt,
                           but_design=but_design,
                           fees=fees,
                           thrs=current_threshold)


@app.route("/clean", methods=['GET', 'POST'])
@login_required
def clean_page():
    cur_row = Result.query.filter_by(date=active_date).first()

    if not cur_row.is_done:
        form = BinaryAnswerForm(number=0 if cur_row.clean is None else cur_row.clean,
                                comment='' if not cur_row.clean_comm else cur_row.clean_comm)

        if form.validate_on_submit():
            cur_row.clean = form.number.data
            cur_row.clean_comm = None if form.comment.data == '' else form.comment.data
            cur_row.amount = calculate_daily_fee([cur_row.clean, cur_row.sch, cur_row.sport, cur_row.other])
            try:
                db.session.commit()
                flash('Record updated')
                return redirect(url_for('home_page'))
            except:
                flash('Something was wrong', category='danger')

        return render_template('clean.html', form=form)

    else:
        flash('Daily record is completed. No changes are allowed', category='danger')
        return redirect(url_for('home_page'))


@app.route("/school", methods=['GET', 'POST'])
@login_required
def school_page():
    cur_row = Result.query.filter_by(date=active_date).first()

    if not cur_row.is_done:
        form = NumberAnswerForm(number=cur_row.sch, comment='' if not cur_row.sch_comm else cur_row.sch_comm)

        if form.validate_on_submit():
            cur_row.sch = form.number.data
            cur_row.sch_comm = None if form.comment.data == '' else form.comment.data
            cur_row.amount = calculate_daily_fee([cur_row.clean, cur_row.sch, cur_row.sport, cur_row.other])
            try:
                db.session.commit()
                flash('Record updated')
                return redirect(url_for('home_page'))
            except:
                flash('Something was wrong', category='danger')

        return render_template('school.html', form=form)

    else:
        flash('Daily record is completed. No changes are allowed', category='danger')
        return redirect(url_for('home_page'))


@app.route("/sport", methods=['GET', 'POST'])
@login_required
def sport_page():
    cur_row = Result.query.filter_by(date=active_date).first()

    if not cur_row.is_done:
        form = SportAnswerForm(number=cur_row.sport, sport=cur_row.sport_type, comment='' if not cur_row.sport_comm else cur_row.sport_comm)

        if form.validate_on_submit():
            cur_row.sport = form.number.data
            cur_row.sport_type = form.sport.data if int(form.number.data) > 0 else None
            cur_row.sport_comm = None if form.comment.data == '' else form.comment.data
            cur_row.amount = calculate_daily_fee([cur_row.clean, cur_row.sch, cur_row.sport, cur_row.other])
            try:
                db.session.commit()
                flash('Record updated')
                return redirect(url_for('home_page'))
            except:
                flash('Something was wrong', category='danger')

        return render_template('sport.html', form=form)

    else:
        flash('Daily record is completed. No changes are allowed', category='danger')
        return redirect(url_for('home_page'))


@app.route("/other", methods=['GET', 'POST'])
@login_required
def other_page():
    cur_row = Result.query.filter_by(date=active_date).first()

    if not cur_row.is_done:
        form = NumberAnswerForm(number=cur_row.other, comment='' if not cur_row.other_comm else cur_row.other_comm)

        if form.validate_on_submit():
            cur_row.other = form.number.data
            cur_row.other_comm = None if form.comment.data == '' else form.comment.data
            cur_row.amount = calculate_daily_fee([cur_row.clean, cur_row.sch, cur_row.sport, cur_row.other])
            try:
                db.session.commit()
                flash('Record updated')
                return redirect(url_for('home_page'))
            except:
                flash('Something was wrong', category='danger')

        return render_template('other.html', form=form)

    else:
        flash('Daily record is completed. No changes are allowed', category='danger')
        return redirect(url_for('home_page'))



@app.route("/register", methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              pin=form.password1.data,
                              is_parent=form.is_parent.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'User {user_to_create.username} was successfully registered', category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_pin(attempted_pin=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))

        else:
            flash('Username and/or password do not match. Please, try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out', category='info')
    return redirect(url_for('login_page'))


@app.route("/stat")
def stat_page():
    c_year = active_date.year
    c_month = active_date.month

    last_day = calendar.monthrange(c_year, c_month)[1]
    from_ = dt(c_year, c_month, 1)
    to_ = dt(c_year, c_month, last_day)

    rows = [v for v, in db.session.execute(db.select(Result).where(Result.date.between(from_, to_)).order_by(Result.date)).all()]

    av_clean = av_sch = av_sport = av_other = total = 0
    num = len(rows)

    for row in rows:
        av_clean += row.clean
        av_sch += row.sch
        av_sport += row.sport
        av_other += row.other
        total += row.amount

    av_clean /= num
    av_sch /= num
    av_sport /= num
    av_other /= num

    stat = ['Summary', round(av_clean), round(av_sch), round(av_sport), round(av_other), total]

    return render_template('stat.html', items=rows, stat=stat)