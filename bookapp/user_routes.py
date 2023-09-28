import json,requests,random,string
from functools import wraps
from flask import render_template,request,abort,redirect,flash,make_response,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash

#followed by local importation
from bookapp import app,csrf,mail,Message
from bookapp.models import db,Book,User,Category,State,Lga,Reviews,Donation
from bookapp.forms import *

@app.after_request #solve the issue of user going back to a protected page
def after_request(response):
    response.headers['Cache-Control']='no-cache, no-store, must-revalidate'
    return response

def generate_string(howmany):
    x=random.sample(string.digits,howmany)
    return ''.join(x)

def login_required(f): #must always be placed aboved any route that needs autentication
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get('userloggedin') !=None:
            return f(*args,**kwargs)
        else:
            flash('Access Denied')
            return redirect('/login')
    return login_check
    
@app.route('/favourite')
def favorite_topic():
    bootcamp={'name':'olusegun','topic':['html','css','python']}
    # category=[]
    
    # for c in cats: 
    #     category.append(c.cat_name)
    cats=db.session.query(Category).all()
    category=[c.cat_name for c in cats]
    return json.dumps(category)

@app.route('/contact/')
def ajax_contact():
    data='This data can be gotten from anywhere'
    return render_template('user/ajax_test.html',data=data)

@app.route('/sendmail/')
def send_mail():
    file=open('requirement.txt')
    msg = Message(subject="Adding headers",sender='From BookWorm',recipients=['natvark1@gmail.com'],body="Thank you for contacting us")
    msg.html="""<h1 class='text-center'>Thank you For Contacting us</h1> </div>"""
    msg.attach('save_as.txt','application/text',file.read())
    mail.send(msg)
    return'done'

@app.route('/submission/',methods=['post','get'])
def ajax_submission():
    user=request.form.get('fullname')
    if user !='' or user !=None:
        return f'Thank you {user} for completing form'
    else:
        return 'Kindly fill the form'

@app.route('/ajaxopt/',methods=['post','get'])
def ajax_options():
    cform=ContactForm()
    if request.method=='GET':
        return render_template('user/ajax_option.html',cform=cform)
    else:
        email=request.form.get('email')
        return f'Thank you, your email {email} has been added'

@app.route('/dependent')
def dependent_dropdown():
    states=db.session.query(State).all()
    return render_template('user/show_states.html',states=states)

@app.route('/lga/<stateid>')
def load_lgas(stateid):
    records=db.session.query(Lga).filter(Lga.state_id==stateid).all()
    str2return='<select class="form-control" name="lga">'
    for r in records:
        optstr=f"<option value='{r.lga_id}'>"+r.lga_name+"</option>"
        str2return = str2return + optstr
    str2return=str2return +'</select>'
    return str2return

@app.route('/checkusername/',methods=['post','get'])
def checkusername():
    mail=request.form.get('mail')
    usermail=db.session.query(User).filter(User.user_email==mail).first()
    if usermail:
        return 'Name is not available'
    else:
        return 'Name is available for use'


@app.route('/')
def home_page():
    books=db.session.query(Book).filter(Book.book_status=='1').limit(4).all()
    #connect to end point http://127.0.0.1:5000/api/v1.0/listall to collect data of books and display on template
    try:
        response= requests.get('http://127.0.0.1:5000/api/v1.0/listall/')
        rsp=json.loads(response.text)
    except:
        rsp=None #comes here when server is unreachable
    return render_template('user/home_page.html',books=books,rsp=rsp)

@app.route('/books/details/<int:id>')
def book_details(id):
    book=db.session.query(Book).get_or_404(id)
    return render_template('user/reviews.html',book=book)

@app.route('/register/',methods=['post','get'])
def register():
    regform=RegForm()
    if request.method=='GET':
        return render_template('user/signup.html',regform=regform)
    else:
        if regform.validate_on_submit():
            usermail=request.form.get('usermail')
            pwd=request.form.get('pwd')
            fullname=request.form.get('fullname')
            hashed_pwd=generate_password_hash(pwd)
            user=User(user_email=usermail,user_pwd=hashed_pwd,user_fullname=fullname)
            db.session.add(user)
            db.session.commit()
            flash('Account has been created. please login')
            return redirect('/login')
        else:
            return render_template('user/sign.html',regform=regform)
        
        
@app.route('/login',methods=['post','get'])
def login():
    if request.method=='GET':
        return render_template('user/loginpage.html')
    else:
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        deets=db.session.query(User).filter(User.user_email==email).first()
        if deets != None:
            hashed_pwd=deets.user_pwd
            if check_password_hash(hashed_pwd,pwd)==True:
                session['userloggedin']=deets.user_id
                return redirect('/dashboard')
            else:
                flash('Invalid Credentials,try Again')
                return redirect('/login')
        else:
            flash('Invalid Credentials,try again')
            return redirect('/login')
        
        
@app.route('/dashboard')
def dashboard():
    if session.get('userloggedin')!=None:
        id=session.get('userloggedin')
        userdeets=User.query.get(id)
        return render_template('user/dashboard.html',userdeets=userdeets)
    else:
        flash('you need to be logged in')
        return redirect('/login')
    
@app.route('/logout')
def logout():
    if session.get('userloggedin')!=None:
        session.pop('userloggedin',None)
    return redirect('/')

@app.route('/viewall/')
def viewall():
    books=db.session.query(Book).filter(Book.book_status=='1').all()
    return render_template('user/viewall.html',books=books)

@app.route('/changedp/' , methods=['post','get'])
@login_required
def changedp():
    id=session.get('userloggedin')
    userdeets=db.session.query(User).get(id)
    dpform=DpForm()
    if request.method=='GET':
        return render_template('user/changedp.html',dpform=dpform,userdeets=userdeets)
    else:
        if dpform.validate_on_submit():
            pix=request.files.get('dp')
            filename=pix.filename
            pix.save(app.config['USER_PROFILE_PATH']+filename) #setting the path in config make path available
            userdeets.user_pix=filename
            db.session.commit()
            flash('Profile picture Uploaded')
            return redirect(url_for('dashboard'))
        else:
            return render_template('user/changedp.html',dpform=dpform,userdeets=userdeets)
            
@app.route('/profile',methods=['post','get'])
@login_required  
def edit_profile():
    id=session.get('userloggedin')
    pform=ProfileForm()
    userdeets=db.session.query(User).get(id)
    if request.method=='GET':
        return render_template('user/edit_profile.html',pform=pform,userdeets=userdeets)
    else:
        if pform.validate_on_submit():
            fullname=request.form.get('fullname')
            userdeets.user_fullname=fullname
            db.session.commit()
            flash('profile Updated')
            return redirect('/dashboard')
        else:
            return render_template('user/edit_profile.html',pform=pform,userdeets=userdeets)   

@app.route('/donate/',methods=['post','get'])
@login_required
def donate():
    if request.method=="GET":
        deets=db.session.query(User).get(session['userloggedin'])
        return render_template('user/donate.html',deets=deets)
    else:
        fname=request.form.get('fullname')
        email=request.form.get('email')
        amount=float(request.form.get('amt')) * 100
        ref='BW'+str(generate_string(8))
        donation=Donation(don_amt=amount,don_email=email,don_fullname=fname,don_userid=session['userloggedin'],don_status='pending',don_refno=ref)
        db.session.add(donation)
        db.session.commit()
        session['trxno']=ref #to save refrence no in session
        return redirect('/confirm_donation')
    
@app.route('/confirm_donation/')
@login_required
def confirm_donation():
    '''We want to display transaction saved from previous page'''
    deets=db.session.query(User).get(session['userloggedin'])
    if session.get('trxno')==None: #when visited directly
        flash('please complete the form', category='error')
        return redirect('/donate')
    else:
        donation_deets=Donation.query.filter(Donation.don_refno==session['trxno']).first()
        return render_template('user/donation_confirmation.html',donation_deets=donation_deets,deets=deets)


@app.route('/landing')
@login_required
def landing_page():
    refno=session.get('trxno')
    transaction_deets=db.session.query(Donation).filter(Donation.don_refno==refno).first()
    url='https://api.paystack.co/transaction/verify/'+transaction_deets.don_refno
    headers={"Content-Type": "application/json","Authorization": "Bearer sk_test_2473b2cdabb44925d750849f4a658f47f03f5ef7"}
    response=requests.get(url,headers=headers)
    rspjson=json.loads(response.text)
    if rspjson['status']==True:
        paystatus=rspjson['data']['gateway_response']
        transaction_deets.don_status='Paid'
        db.session.commit()
        return redirect('/dashboard')
    else:
        flash('Payment failed')
        return redirect('/reports')


@app.route('/initialize/paystack/')
@login_required
def initialize_paystack():
    deets=User.query.get(session['userloggedin'])
    refno=session.get('trxno')
    transaction_deets=db.session.query(Donation).filter(Donation.don_refno==refno).first()
    url="https://api.paystack.co/transaction/initialize"
    headers={"Content-Type": "application/json","Authorization": "Bearer sk_test_2473b2cdabb44925d750849f4a658f47f03f5ef7"}
    data={ "email": deets.user_email, "amount":transaction_deets.don_amt, "reference":refno}
    response=requests.post(url,headers=headers,data=json.dumps(data))
    rspjson=response.json()
    # return rspjson
    if rspjson['status']==True:
        redirectURL=rspjson['data']['authorization_url']
        return redirect(redirectURL) #paystack payment page will load
    else:
        flash('please complete the form again')
        return redirect('/donate')
    

@app.route('/submit_review/',methods=['post'])
@login_required
def submit_review():
    title=request.form.get('title')
    content=request.form.get('content')
    userid=session['userloggedin']
    bookid=request.form.get('bookid')
    rev=Reviews(rev_title=title,rev_text=content,rev_userid=userid,rev_bookid=bookid)
    db.session.add(rev)
    db.session.commit()
    
    stre=f'''<article class="blog-post">
      <h5 class="blog-post-title">{title}</h5>
      <p class="blog-post-meta">Reviewed just now by <a href="#">{rev.reviewby.user_fullname}</a></p>

      <p>{content}</p>
      <hr> 
    </article>'''
    return stre

@app.route('/myreviews')
@login_required
def myreviews():
    id=session['userloggedin']
    userdeets=db.session.query(User).get(id)
    return render_template('user/myreviews.html',userdeets=userdeets)