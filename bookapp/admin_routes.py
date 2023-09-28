import random,os,string
from flask import render_template,request,abort,redirect,flash,make_response,url_for,session


#followed by local importation
from bookapp import app,csrf
from bookapp.models import db,Admin,Book,Category
from bookapp.forms import *

allowed=['jpg','png']
def generate_string(howmany):
    x=random.sample(string.ascii_lowercase,howmany)
    return ''.join(x)

@app.after_request #solve the issue of user going back to a protected page
def after_request(response):
    response.headers['Cache-Control']='no-cache, no-store, must-revalidate'
    return response

@app.route('/admin')
def admin_page():
    if session.get('adminuser') ==None or session.get('role')!='admin':
        return render_template('admin/login.html') 
    else:
        return redirect(url_for('admin_dashboard'))



@app.route('/admin/login/', methods=['post','get'])
def admin_login():
    if request.method=='GET':
        return render_template('admin/login.html')
    else:
        username=request.form.get('username')
        pwd=request.form.get('pwd')
        check=db.session.query(Admin).filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first()
        if check:
            session['adminuser']=check.admin_id
            session['role']='admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Login',category='danger')
            return redirect(url_for('admin_login'))
        
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('adminuser') ==None or session.get('role')!='admin':
        return redirect(url_for('admin_login'))
    else:
        return render_template('admin/dashboard.html')
    
@app.route('/admin/logout')
def admin_logout():
    if session.get('adminuser')!=None:
        session.pop('adminuser',None)
        session.pop('role',None)
        flash('You are logged out',category='info')
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/books')
def all_books():
    if session.get('adminuser')==None or session.get('role')!='admin':
        return redirect(url_for('admin_login'))
    else:
        books=db.session.query(Book).all()
        return render_template('admin/allbooks.html',books=books)

@app.route('/admin/addbook',methods=['post','get'])
def addbook():
    if session.get('adminuser')==None or session.get('role')!='admin':
        return redirect(url_for('admin_login'))
    else:
        if request.method=='GET':
            cats=db.session.query(Category).all()
            return render_template('admin/addbook.html',cats=cats)
        else:
            filesobj=request.files['cover']
            filename=filesobj.filename
            newname='default.png'
            if filename=='':
                flash('Book Cover not include',category='danger')
            else:
                pieces=filename.split('.')
                ext=pieces[-1].lower()
                if ext in allowed:
                    newname=str(int(random.random()*10000000000))+filename #to make file name unique
                    filesobj.save('bookapp/static/uploads/'+newname)
                else:
                    flash('File format is not allowed,format was not uploaded',category='danger')
            title=request.form.get('title')
            category=request.form.get('category')
            status=request.form.get('status')
            description=request.form.get('description')
            yearpub=request.form.get('yearpub')
            bk=Book(book_title=title,book_desc=description,book_publication=yearpub,book_catid=category,book_status=status,book_cover=newname)
            db.session.add(bk)
            db.session.commit()
            if bk.book_id:
                flash('book has been added')

            else:
                flash('please try again')
            return redirect(url_for('all_books'))
        

@app.route('/admin/delete/<id>/')
def book_delete(id):
    book=db.session.query(Book).get_or_404(id)
    filename=book.book_cover #file should be deleted before deleting the book
    if filename !=None and filename !='dafault.png' and os.path.isfile('bookapp/static/uploads/'+filename):#check if the file exists
        os.remove('bookapp/static/uploads/'+filename)
    db.session.delete(book)
    db.session.commit()
    flash('Book has been deleted')
    return redirect(url_for('all_books'))

@app.route('/admin/edit/book/<int:id>/',methods=['post','get'])
def edit_book(id):
    if session.get('adminuser')==None or session.get('role')!='admin':
        return redirect(url_for('admin_login'))
    else:
        if request.method=="GET":
            cats=db.session.query(Category).all()
            edit=db.session.query(Book).get_or_404(id)
            return render_template('admin/editbook.html',deets=edit,cats=cats)
        else:
            #retrieve data here
            book_2update=Book.query.get(id)
            current_filename=book_2update.book_cover
            
            book_2update.book_title=request.form.get('title')
            book_2update.book_catid=request.form.get('category')
            book_2update.book_status=request.form.get('status')
            book_2update.book_desc=request.form.get('description')
            book_2update.book_publication=request.form.get('yearpub')
            cover=request.files.get('cover')
            #check if a file was selected for upload
            if cover.filename !='':
                name,ext=os.path.splitext(cover.filename)
                if ext.lower()in ['.jpg','.png','.jpeg']:
                    newfilename=generate_string(10) + ext
                    cover.save('bookapp/static/uploads/'+newfilename)
                    #db.session.delete(current_filename)
                    book_2update.book_cover=newfilename
                else:
                    flash('book cover was not uploaded, check extension allowed ')
            db.session.commit()
            flash('Book details was uploaded')
            return redirect('/admin/books')