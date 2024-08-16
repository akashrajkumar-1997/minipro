from flask import Flask,request,redirect,url_for,render_template,flash,session,send_file
from flask_session import Session
import mysql.connector
from otp import genotp
from cmail import sendmail
from key import secret_key
from stoken import token,dtoken
from io import BytesIO
import re
import flask_excel as excel 
app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
excel.init_excel(app)
Session(app)
mydb=mysql.connector.connect(host='localhost',user='root',password='Admin',db='spm')
app.secret_key =b')\x94<\xe5X'
@app.route('/')
def index():
    return render_template('welcome.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        print(request.form)
        stu_fname=request.form['s_fname']
        stu_lname=request.form['s_lname']
        email=request.form['email']
        ph_no=request.form['ph_no']
        address=request.form['address']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(email) from student where email=%s',[email])
        data=cursor.fetchone()[0]
        if data==0:
            otp=genotp()
            data={'otp':otp,'email':email,'stu_fname':stu_fname,'stu_lname':stu_lname,'password':password}
            subject='Verication otp for SPM Application'
            body=f'Registration otp for SPM application {otp}'
            sendmail(to=email,subject=subject,body=body)
            return redirect(url_for('verifyotp',data1=token(data=data)))
        else:
            flash('Email already existed')
            return redirect(url_for('register'))
    return render_template('register.html')
@app.route('/otp/<data1>',methods=['GET','POST'])
def verifyotp(data1):
    try:
        data1=dtoken(data=data1)
    except Exception as e:
        print(e)
        return 'time out of opt'
    else:  
        if request.method=='POST':
            uotp=request.form['otp']
            if uotp==data1['otp']:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('insert into student(email,student_fname,student_lname,password) values(%s,%s,%s,%s)',[data1['email'],data1['stu_fname'],data1['stu_lname'],data1['password']])
                mydb.commit()
                cursor.close()
                flash('Registration successfull')
                return redirect(url_for('login'))
            else:
                return f'otp invalid pls check your mail.'
    finally:
        print('done')
    return render_template('otp.html')
@app.route('/login', methods=["GET","POST"])
def login():
    if  session.get('email'):
        return redirect(url_for('login.html'))
    else:
         if request.method=='POST':
            email=request.form['email']
            password=request.form['password']
            print(password.encode('utf-8'))
            try:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('select email,password from student where email=%s',[email])
                data=cursor.fetchone()
                print(data[1])
            except Exception as e:
                  print(e)
                  return 'email wrong'
            else:
                 if data[1]==password.encode('utf-8'):
                   session['email']=email
                 if not session.get(email):
                    session[email]={}
                    return redirect(url_for('panel'))
                 else:
                      flash('invalid password')
    return render_template('login.html')
@app.route('/addnotes',methods=['GET','POST']) 
def addnotes():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            added_by=session.get('email')
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into notes(title,note_content,added_by) values(%s,%s,%s)',[title,content,added_by])
            mydb.commit()
            cursor.close()
            flash(f'notes {title} added successfully')
            return redirect(url_for('panel'))
        return render_template('notes.html') 
@app.route('/panel')
def panel():
    if not session.get('email'):
        return redirect(url_for('login'))
    return render_template('panel.html')

@app.route('/updatenotes/<nid>',methods=['GET','PUT'])
def updatenotes(nid):
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        cursor.mydb.cusror(buffered=True)
        cursor.execute('select title,note_content from notes where nid=%s',[nid])
        note_data=cursor.fetchone()
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            cursor.execute('update notes set tile=%s,content=%s where nid=%s',[title,content,nid])
            mydb.commit()
            cursor.close()
            flash(f'notes{title} updated successfully')
            return redirect(url_for('updatenotes',nid=nid))
        
        return render_template(url_for('updatenotes.html',note_data=note_data))
@app.route('/deletenotes/<nid>',methods=['DELETE'])
def deletenotes(nid):
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        cursor.mydb.cusror(buffered=True)
        cursor.execute('delete from notes where nid=%s and adde_by=%s',[nid,session.get('email')])
        mydb.commit()
        cursor.close()
        flash(f'Notes {nid} deleted successfully.')
        return redirect(url_for('panel'))
@app.route('/allnotes')
def allnotes():
            if not session.get('email')
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select nid,title,created_at from notes where  added_by=%s')
            data=cursor.fetchall()
            print(data)
            return render_template('table.html',data=data)
@app.route('/logout')
def logout():
    if session.get('email'):
       session.pop('email')
       return redirect(url_for('login'))
    else:
         return redirect(url_for('login'))
@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        cursor.mydb.cusror(buffered=True)
        cursor.execute('select title,note_content from notes where nid=%s',[nid])
        note_data=cursor.fetchone()
        return render_template('viewnotes.html',note_data=note_data)
@app.route('/fileupload',methods=['GET','POST'])
def fileupload():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        if request.method=='post':
            file=request.files['file']
            file_open=open()
            print(file_open.read())
            added_by=session.get('email')
            cursor=mydb,cursor(Buffered=True)
            cursor.execute('insert into files_data(file_name,file_data,added_by) values((%s,%s,%s))',[file_name,file_data,added_by])
            mydb.commit()
            cursor.close()
            flash(f'file{file.filename} added successfully')
            return redirect(url_for('panel'))
    return render_template('fileupload.html')   
@app.route('/viewall_files')
def viewall_files():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        added_by=session.get('email')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select f_id,file_name,created_at from files_data where added_by=%s',[added_by])
        data=cursor.fetchall()
        return render_template('allfiles.html',data=data)
@app.route('/view_file/<fid>')
def view_file(fid):
    if not session.get('email')
    return redirect(url_for('login'))
    else:
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select file_name,file_data from files_data where f_id=%s and added_by=%s',[fid,session.get('email')])
            fdata=cursor.fetchone()
            bytes_data=BytesIo(fdata)
            filename=fname
            return send_file(bytes_data,download_name=filename,as_attachment=False)
        except Exception as e:
            print(e)
            return 'file not found'
        finally:
            cursor.close()

@app.route('/download_file/<fid>')
def download_file(fid):
    if not session.get('email')
    return redirect(url_for('login'))
    else:
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select file_name,file_data from files_data where f_id=%s and added_by=%s',[fid,session.get('email')])
            fdata=cursor.fetchone()
            bytes_data=BytesIo(fdata)
            filename=fname
            return send_file(bytes_data,download_name=filename,as_attachment=True)
        except Exception as e:
            print(e)
            return 'file not found'
        finally:
            cursor.close()

@app.route('/search',methods=['GET','POST'])
def search():
    if session.get('email'):
        if request.method=='POST':
            name=request.form['sname']
            strg=['A-Za-z0-9']
            pattern=re.compile(f'^{strg}',re.IGNORECASE)
            if (pattern.match(name)):
              cursor.execute('select * from notes where added_by=%s and tile like %S',{session.get('email'),name+'%'})
              sname=cursor.fetchall()
              cursor.execute('select f_id,file_name,created_at from files_data where added_by=%s and file_name like %S',{session.get('email'),name+'%'})
              fname=cursor.fetchall()
              cursor,close()
              return render_template('panel.html',sname=sname)
        else:
            flash('result not found')
            return redirect(url_for('panel'))
    else:
        return redirect(url_for('login'))
    
@app.route('/getexcel_data')
def getexcel_data():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        user=session.get('email')
        columns=['Title','Content','Date']
        cursor.mydb.cursor(buffered=True)
        cursor.execute('select title,note_content,created_at from notes where added_by=%s',[user])
        data=cursor.fetchall()
        array=data=[list(i) for in data]
        array_data.insert(0,columns)
        return excel.make_response_from_array(array_data,'xlsx',filename='NotesData')
app.run(debug=True,use_reloader=True)