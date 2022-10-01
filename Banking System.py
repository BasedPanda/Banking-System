import mysql.connector
import pandas as pd
import os
import datetime

if not os.path.exists("DATE.txt"):
    f=open("DATE.txt",'w')
    date=datetime.datetime.now()
    m=str(date.month)
    y=str(date.year)
    if date.month<10:
        m='0'+m
    d=y+'-'+m+'-01'
    f.write(d)
    f.close()

if not os.path.exists("MYSQL_DETAILS.txt"):
    print("Please enter the following details for your MySQL server.")
    host_var=input("Enter host name: ")
    user_var=input("Enter user name: ")
    pwd_var=input("Enter password: ")
    f=open("MYSQL_DETAILS.txt",'w')
    f.write(host_var+"\n"+user_var+"\n"+pwd_var)
    f.close()


f=open("MYSQL_DETAILS.txt",'r')
x=f.readlines()
host_var=x[0].rstrip("\n")
user_var=x[1].rstrip("\n")
pwd_var=x[2].rstrip("\n")
f.close()


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def get_date():                         #returns the current date
    curr_date=""
    f=open("DATE.txt","r")
    curr_date=f.read()
    f.close()
    return curr_date


def get_end_date(start_date,t):             #returns the end date when provided a start date and a time period
    date_l= start_date.split("-")
    for i in range(3):
        date_l[i]=int(date_l[i])
    date_l[1]+=t
    end_date=""
    while date_l[1]>12:
        date_l[1]-=12
        date_l[0]+=1
    while date_l[1]<1:
        date_l[1]+=12
        date_l[0]-=1
    end_date=str(date_l[0])+"-"+str(date_l[1])+"-"+str(date_l[2])
    return end_date


def setup():                                #setting up the database and tables for the first time the program is being used
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='mysql')
    mycur=conn.cursor()
    mycur.execute("Create database Banking_System;")
    conn.close()

    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    f=open("SETUP_FILE.txt","r")
    x=f.readlines()
    for i in x:
        mycur.execute(i.rstrip("\n"))
    conn.close()
    print("Database and tables successfully setup.")


def create_user():                              #create a user profile
    customer_id=""
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    name=input("Enter name: ")
    ph=input("Enter phone number: ")
    while len(ph)!=10 or ph.isdigit()==False:
        print("Entered phone number is either of incorrect length or has characters which are not digits.\nPlease try again.")
        ph=input("Enter phone number: ")
    mon_inc=int(input("Enter monthly income: "))
    if mon_inc<=10000:
        cred_sc=500
    elif mon_inc<=50000:
        cred_sc=650
    elif mon_inc<=100000:
        cred_sc=700
    else:
        cred_sc=800
    mycur.execute("Select Count(*) from Customer_Info;")
    conn.commit()
    if mycur.fetchone()[0]==0:
        customer_id="10000"
    else:
        mycur.execute("Select max(Customer_Id) from Customer_Info;")
        conn.commit()
        customer_id=str(int(mycur.fetchone()[0])+1)
    query= "insert into Customer_Info values (%s,%s,%s,%s,%s)"
    record=(customer_id,name,ph,mon_inc,cred_sc)
    mycur.execute(query,record)
    conn.commit()
    print("  USER DETAILS:")
    query="select * from customer_info where customer_id="+customer_id
    cus_det=pd.read_sql_query(query,conn)
    print(cus_det)
    print(90*"*")
    conn.close()
    

def create_account():                   #create different types of accounts: Savings, Current and Fixed Depaosit
    acc_no=""
    amt=0
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    c_id=input("Enter Customer ID: ")
    query="Select Name from Customer_Info where Customer_Id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    name=mycur.fetchone()
    if name ==(None):
        print("No such customer found. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    c_name=name[0]
    while True:
        ch=""
        acc_type=int(input("Which type of account do you want to open?\n1. Savings Account\n2. Current Account\n3. Fixed Deposit Account\nEnter choice: "))
        if acc_type==1:                     #create Savings account
            mycur.execute("Select Count(*) from Savings;")
            conn.commit()
            if mycur.fetchone()[0]==0:
                acc_no="100000"
            else:
                mycur.execute("Select max(Account_Number) from Savings;")
                conn.commit()
                acc_no=str(int(mycur.fetchone()[0])+1)
            int_rate=3.5
            while amt<10000 and (ch!='x' or ch!="X"):
                amt=int(input("Enter the amount you want to enter in your new account. Min. value: Rs.10000: "))
                if amt<10000:
                    print("The amount entered is less than the minimum value. Enter new amount or return to main menu using 'x'")
                    ch=input("Do you want to continue to enter new amount? Enter any key to continue. Enter 'x' to return to main menu.")
                    if ch=='x' or ch=='X':
                        print(90*"*")
                        conn.close()
                        return
                
            query1= "insert into Savings values (%s,%s,%s,%s,%s)"
            record1=(acc_no,c_id,c_name,amt,int_rate)
            mycur.execute(query1,record1)
            conn.commit()
            print("  SAVINGS ACCOUNT DETAILS:")
            query="select * from savings where account_number="+acc_no
            sav_det=pd.read_sql_query(query,conn)
            print(sav_det)
            print(90*"*")
            create_transaction(acc_no,c_id,c_name,"Savings Account",amt)
            conn.close()
            break
        if acc_type==2:                     #create current account
            mycur.execute("Select Count(*) from Current;")
            conn.commit()
            if mycur.fetchone()[0]==0:
                acc_no="300000"
            else:
                mycur.execute("Select max(Account_Number) from Current;")
                conn.commit()
                acc_no=str(int(mycur.fetchone()[0])+1)
            while amt<30000 and (ch!='x' or ch!="X"):
                amt=int(input("Enter the amount you want to enter in your new account. Min. value: Rs.30000: "))
                if amt<30000:
                    print("The amount entered is less than the minimum value. Enter new amount or return to main menu using 'x'")
                    ch=input("Do you want to continue to enter new amount? Enter any key to continue. Enter 'x' to return to main menu.")
                    if ch=='x' or ch=='X':
                        print(90*"*")
                        conn.close()
                        return
                
            query1= "insert into Current values (%s,%s,%s,%s)"
            record1=(acc_no,c_id,c_name,amt)
            mycur.execute(query1,record1)
            conn.commit()
            print("  CURRENT ACCOUNT DETAILS:")
            query="select * from current where account_number="+acc_no
            cur_det=pd.read_sql_query(query,conn)
            print(cur_det)
            print(90*"*")
            create_transaction(acc_no,c_id,c_name,"Current Account",amt)
            conn.close()
            break
        if acc_type==3:                     #create fixed deposit account
            t=0
            mycur.execute("select count(*) from savings where customer_id=%s;",(c_id,))
            c=mycur.fetchone()[0]
            if c==0:
                print(c_name+" has to create a savings account first. Returning to main menu.")
                print(90*"*")
                conn.close()
                return
            mycur.execute("Select Count(*) from Fixed_Deposit;")
            conn.commit()
            if mycur.fetchone()[0]==0:
                acc_no="500000"
            else:
                mycur.execute("Select max(Account_Number) from Fixed_Deposit;")
                conn.commit()
                acc_no=str(int(mycur.fetchone()[0])+1)
            int_rate=6.5
            while amt<5000 and (ch!='x' or ch!="X"):
                amt=int(input("Enter the amount you want to enter in your new account. Min. value: Rs.5000: "))
                if amt<5000:
                    print("The amount entered is less than the minimum value. Enter new amount or return to main menu using 'x'")
                    ch=input("Do you want to continue to enter new amount? Enter any key to continue. Enter 'x' to return to main menu.")
                    if ch=='x' or ch=='X':
                        print(90*"*")
                        conn.close()
                        return
            print("Time period:\n1. 1 month\n2. 3 months\n3. 6 months\n4. 1 year\n5. 3 years")
            while True:
                x=int(input("Enter choice: "))
                if x in [1,2,3,4,5]:
                    if x==1:
                        t=1
                    elif x==2:
                        t=3
                    elif x==3:
                        t=6
                    elif x==4:
                        t=12
                    elif x==5:
                        t=36
                    break
                else:
                    print("Incorrect option entered. Try again")
            start_date=get_date()
            end_date=get_end_date(start_date, t)
            query2="insert into Fixed_Deposit values (%s,%s,%s,%s,%s,%s,%s,%s)"
            record2=(acc_no,c_id,c_name,amt,start_date,t,end_date,int_rate)
            mycur.execute(query2,record2)
            conn.commit()
            print("  FIXED DEPOSIT ACCOUNT DETAILS:")
            query="select * from fixed_deposit where account_number="+acc_no
            fd_det=pd.read_sql_query(query,conn)
            print(fd_det)
            print(90*"*")
            create_transaction(acc_no,c_id,c_name,"Fixed Deposit",amt)
            conn.close()
            break



def take_loan():                            #for taking home and education loans
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    x=''
    print("   MENU\n1. Home Loan\n2. Education Loan")
    while True:
        ch=int(input("Enter your choice: "))
        if ch==1:
            name=""
            c_id=input("Enter Customer Id: ")
            query="Select Name from Customer_Info where Customer_Id=%s;"
            record=(c_id,)
            mycur.execute(query,record)
            conn.commit()
            name=mycur.fetchone()
            if name ==(None):
                print("No such customer found. Returning to main menu.")
                print(90*"*")
                conn.close()
                return
            c_name=name[0]
            query="select count(*) from home_loan where customer_id=%s;"
            mycur.execute(query,record)
            conn.commit()
            count=mycur.fetchone()[0]
            if count>0:
                print(c_name+" already has one home loan. No one is allowed to take more than one home loan at a time.\nReturning to main menu.")
                print(90*"*")
                conn.close()
                return
            max_loan1=0
            max_loan2=0
            query="select credit_score from customer_info where customer_id=%s;"
            record=(c_id,)
            mycur.execute(query,record)
            conn.commit()
            cred_score=mycur.fetchone()[0]
            mycur.execute("Select Count(*) from Home_Loan;")
            conn.commit()
            if mycur.fetchone()[0]==0:
                acc_no="700000"
            else:
                mycur.execute("Select max(Account_Number) from Home_Loan;")
                conn.commit()
                acc_no=str(int(mycur.fetchone()[0])+1)
            if cred_score<500:
                max_loan1=500000
            elif cred_score<600:
                max_loan1=1500000
            elif cred_score<700:
                max_loan1=3000000
            else:
                max_loan1=5000000
            print("Time period:\n1. 1 year\n2. 3 years\n3. 5 years\n4. 10 years")
            t=0
            while True:
                x=int(input("Enter choice: "))
                if x in [1,2,3,4,5]:
                    if x==1:
                        t=12
                    elif x==2:
                        t=36
                    elif x==3:
                        t=60
                    elif x==4:
                        t=120
                    break
                else:
                    print("Incorrect option entered. Try again.")
            query="select monthly_income from customer_info where customer_id=%s;"
            record=(c_id,)
            mycur.execute(query,record)
            conn.commit()
            mon_inc=mycur.fetchone()[0]
            int_rate=7.0
            max_loan2=round((0.3*mon_inc*t)/((1+(int_rate/(100*12)))**t),-3)      #finding the principal amount for which EMI would be less than 30% of monthly income rounded to nearest thousand
            max_loan=int(min(max_loan1,max_loan2))
            print("With your current income and credit score, the maximum loan you can take is: Rs."+str(max_loan))
            amt=int(input("Enter loan amount: "))
            while amt>max_loan and (x!='x' or x!='X'):
                print("The amount entered is more than the maximum value. Enter new amount or return to main menu using 'x'")
                x=input("Do you want to continue to enter new amount? Enter any key to continue. Enter 'x' to return to main menu.")
                if x=='x' or x=='X':
                    print(90*"*")
                    conn.close()
                    return
                else:
                    amt=int(input("Enter loan amount: "))
            start_date=get_date()
            end_date=get_end_date(start_date,t)
            repayable_amt=round((amt*(1+(int_rate/(100*12)))**t)/t)*t
            emi=repayable_amt/t
            print("You will be required to pay a total of Rs."+str(repayable_amt)+" with a monthly EMI of Rs."+str(emi)+" for a period of",t,"months")
            y=""
            while True:
                y=input("Enter 'c' to continue or 'x' to return to main menu: ")
                if y=='x' or y=='X':
                    print(90*"*")
                    conn.close()
                    return
                elif y=='c' or y=='C':
                    break
                print("Incorrect input. Please enter again.")
            balance=repayable_amt
            query2="insert into Home_Loan values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            record2=(acc_no,c_id,c_name,amt,int_rate,start_date,end_date,emi,balance,"YES")
            mycur.execute(query2,record2)
            conn.commit()
            query="select * from home_loan where account_number="+acc_no
            details=pd.read_sql_query(query,conn)
            print("  HOME LOAN DETAILS:")
            print(details)
            print(90*"*")
            create_transaction(acc_no,c_id,c_name,"Home Loan",amt)
            conn.close()
            return
        elif ch==2:
            name=""
            c_id=input("Enter Customer Id: ")
            query="Select Name from Customer_Info where Customer_Id=%s;"
            record=(c_id,)
            mycur.execute(query,record)
            conn.commit()
            name=mycur.fetchone()
            if name ==(None):
                print("No such customer found. Returning to main menu.")
                print(90*"*")
                conn.close()
                return
            c_name=name[0]
            query="select count(*) from education_loan where customer_id=%s"
            mycur.execute(query,record)
            conn.commit()
            count=mycur.fetchone()[0]
            if count>0:
                print(c_name+" already has one education loan. No one is allowed to take more than one education loan at a time.\nReturning to main menu.")
                print(90*"*")
                conn.close()
                return
            max_loan1=0
            max_loan2=0
            query="select credit_score from customer_info where customer_id=%s;"
            record=(c_id,)
            mycur.execute(query,record)
            conn.commit()
            cred_score=mycur.fetchone()[0]
            mycur.execute("Select Count(*) from Education_Loan;")
            conn.commit()
            if mycur.fetchone()[0]==0:
                acc_no="900000"
            else:
                mycur.execute("Select max(Account_Number) from Education_Loan;")
                conn.commit()
                acc_no=str(int(mycur.fetchone()[0])+1)
            if cred_score<500:
                max_loan1=100000
            elif cred_score<600:
                max_loan1=500000
            elif cred_score<700:
                max_loan1=1000000
            else:
                max_loan1=2500000
            print("Time period:\n1. 1 year\n2. 3 years\n3. 5 years\n4. 7 years")
            t=0
            while True:
                x=int(input("Enter choice: "))
                if x in [1,2,3,4,5]:
                    if x==1:
                        t=12
                    elif x==2:
                        t=36
                    elif x==3:
                        t=60
                    elif x==4:
                        t=84
                    break
                else:
                    print("Incorrect option entered. Try again.")
            edu_time=int(input("Enter education period in years: "))
            t+=(edu_time*12)
            query="select monthly_income from customer_info where customer_id=%s;"
            record=(c_id,)
            mycur.execute(query,record)
            conn.commit()
            mon_inc=mycur.fetchone()[0]
            int_rate=10.0
            max_loan2=round((0.3*mon_inc*(t-edu_time*12))/((1+(int_rate/(100*12)))**t),-3)      #finding the principal amount for which EMI would be less than 30% of monthly income rounded to nearest thousand
            max_loan=int(min(max_loan1,max_loan2))
            print("With your current income and credit score, the maximum loan you can take is: Rs."+str(max_loan))
            amt=int(input("Enter loan amount: "))
            while amt>max_loan and (x!='x' or x!='X'):
                print("The amount entered is more than the maximum value. Enter new amount or return to main menu using 'x'")
                x=input("Do you want to continue to enter new amount? Enter any key to continue. Enter 'x' to return to main menu.")
                if x=='x' or x=='X':
                    print(90*"*")
                    conn.close()
                    return
                else:
                    amt=int(input("Enter loan amount: "))
            start_date=get_end_date(get_date(),edu_time*12)
            end_date=get_end_date(get_date(),t)
            repayable_amt=round((amt*(1+(int_rate/(100*12)))**t)/(t-edu_time*12))*(t-edu_time*12)
            emi=repayable_amt/(t-(edu_time*12))
            print("You will be required to pay a total of Rs."+str(repayable_amt)+" with a monthly EMI of Rs."+str(emi)+" for a period of",t-(edu_time*12),"months \nstarting from "+start_date)
            y=""
            while True:
                y=input("Enter 'c' to continue or 'x' to return to main menu: ")
                if y=='x' or y=='X':
                    print(90*"*")
                    conn.close()
                    return
                elif y=='c' or y=='C':
                    break
                print("Incorrect input. Please enter again.")
            balance=repayable_amt
            query2="insert into Education_Loan values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            record2=(acc_no,c_id,c_name,amt,int_rate,edu_time*12,start_date,end_date,emi,balance,"YES")
            mycur.execute(query2,record2)
            conn.commit()
            query="select Account_Number,Customer_ID,Customer_Name,Loan_Amount, Interest_Rate,Start_Date,End_Date, EMI, Balance, Paid_this_month from education_loan where account_number="+acc_no
            details=pd.read_sql_query(query,conn)
            print("  EDUCATION LOAN DETAILS:")
            print(details)
            print(90*"*")
            create_transaction(acc_no,c_id,c_name,"Education Loan",amt)
            conn.close()
            return()



def pay_emi():                          #for paying the EMI on loans
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    c_id=input("Enter Customer Id: ")
    query="Select Name from Customer_Info where Customer_Id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    name=mycur.fetchone()
    if name ==(None):
        print("No such customer found. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    c_name=name[0]
    ch=int(input("Enter which type of loan you want to pay back EMI for:\n1. Home Loan\n2. Education Loan\nEnter choice: "))
    if ch==1:
        query1="select account_number from home_loan where customer_id=%s"
        mycur.execute(query1,record)
        conn.commit()
        acc_num=mycur.fetchone()
        if acc_num==(None):
            print(c_name,"has not taken any home loan. Returning to main menu.")
            print(90*"*")
            conn.close()
            return
        query3="select balance,emi,paid_this_month from home_loan where customer_id=%s"
        mycur.execute(query3,(c_id,))
        conn.commit()
        rec=mycur.fetchone()
        paid=rec[2]
        balance=rec[0]
        emi=rec[1]
        if paid=="YES":
            print("EMI already paid for this month.")
            print(90*"*")
            conn.close()
            return
        else:
            acc_no=acc_num[0]
            query2="select * from home_loan where account_number="+acc_no
            details=pd.read_sql_query(query2,conn)
            print("  LOAN DETAILS:")
            print(details)
            while True:
                c=input("EMI: Rs."+str(emi)+". Pay the EMI for this month?. Enter choice (y/n): ")
                if c=='n' or c=='N':
                    print("Have not paid the EMI for this month. Returning to main menu.")
                    print(90*"*")
                    conn.close()
                    return
                elif c=='y' or c=='Y':
                    break
                print("Incorrect value provided. Try again.")
            print("EMI paid for this month.")
            query="update home_loan set paid_this_month=%s, balance=%s where customer_id=%s;"
            record=("YES",balance-emi,c_id)
            mycur.execute(query,record)
            conn.commit()
            print(90*"*")
            print("  UPDATED LOAN DETAILS:")
            details=pd.read_sql_query(query2,conn)
            print(details)
            create_transaction(acc_no,c_id,c_name,"Home Loan EMI",(-1*emi))
            query="update customer_info set credit_score=credit_score+0.5 where credit_score<900 && customer_id=%s;"
            mycur.execute(query,(c_id,))
            conn.commit()
            print(90*"*")
            conn.close()
            return
    elif ch==2:
        query1="select account_number from education_loan where customer_id=%s"
        mycur.execute(query1,record)
        conn.commit()
        acc_num=mycur.fetchone()
        if acc_num==(None):
            print(c_name,"has not taken any education loan. Returning to main menu.")
            print(90*"*")
            conn.close()
            return
        acc_no=acc_num[0]
        query1="select start_date from education_loan where account_number=%s"
        mycur.execute(query1,(acc_no,))
        conn.commit()
        start_date=mycur.fetchone()[0]
        curr_date=""
        curr_date=get_date()
        if str(start_date)>curr_date:
            print(c_name+"'s repayment period has not begun yet. Returning to main menu")
            print(90*"*")
            conn.close()
            return
        query2="select Account_Number,Customer_ID,Customer_Name,Loan_Amount, Interest_Rate,Start_Date,End_Date, EMI, Balance, Paid_this_month from education_loan where account_number="+acc_no
        details=pd.read_sql_query(query2,conn)
        print("  LOAN DETAILS:")
        print(details)
        query3="select balance,emi,paid_this_month from education_loan where customer_id=%s"
        mycur.execute(query3,(c_id,))
        conn.commit()
        rec=mycur.fetchone()
        paid=rec[2]
        balance=rec[0]
        emi=rec[1]
        if paid=="YES":
            print("EMI already paid for this month.")
            print(90*"*")
            conn.close()
            return
        else:
            while True:
                c=input("EMI: Rs."+str(emi)+". Pay the EMI for this month?. Enter choice (y/n): ")
                if c=='n' or c=='N':
                    print("Have not paid the EMI for this month. Returning to main menu.")
                    print(90*"*")
                    conn.close()
                    return
                elif c=='y' or c=='Y':
                    break
                print("Incorrect value provided. Try again.")
            print("EMI paid for this month.")
            query="update education_loan set paid_this_month=%s, balance=%s where customer_id=%s;"
            record=("YES",balance-emi,c_id)
            mycur.execute(query,record)
            conn.commit()
            create_transaction(acc_no,c_id,c_name,"Education Loan EMI",(-1*emi))
            query="update customer_info set credit_score=credit_score+0.5 where credit_score<900 && customer_id=%s;"
            mycur.execute(query,(c_id,))
            conn.commit()
            print(90*"*")
            print("  UPDATED LOAN DETAILS:")
            details=pd.read_sql_query(query2,conn)
            print(details)
            print(90*"*")
            conn.close()
            return

        
def pay_fine():
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    c_id=input("Enter Customer Id: ")
    query="Select Name from Customer_Info where Customer_Id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    name=mycur.fetchone()
    if name ==(None):
        print("No such customer found. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    c_name=name[0]
    query="Select count(*) from Fine where Customer_Id=%s;"
    mycur.execute(query,record)
    conn.commit()
    f_no=mycur.fetchone()[0]
    if f_no ==0:
        print("No fine registered under this customer. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    query1="select * from fine where customer_id="+c_id
    fine_details=pd.read_sql_query(query1,conn)
    print("  FINE DETAILS:")
    print(fine_details)
    query="select default_id,fine_value,account_number,loan_type from fine where customer_id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    rec=mycur.fetchall()
    l=len(rec)
    for i in range (l):
        def_id=rec[i][0]
        f_val=rec[i][1]
        acc_no=rec[i][2]
        l_type=rec[i][3]
        a_type=l_type+" Fine"
        while True:
            ch=input("Pay Rs."+str(f_val)+" to pay off fine of default id "+def_id+"?(y/n)")
            if ch=="y":
                query="delete from fine where default_id= %s;"
                record=(def_id,)
                mycur.execute(query,record)
                conn.commit()
                print("Fine of default id "+def_id+" has been repaid")
                create_transaction(acc_no,c_id,c_name,a_type,-1*f_val)
                if i==l-1:
                    break
                print("  UPDATED FINE DETAILS:")
                fine_details=pd.read_sql_query(query1,conn)
                print(fine_details)
                break
            elif ch=="n":
                print("Fine has not been repaid.")
                print(90*"*")
                conn.close()
                return
            else:
                print("Incorrect input. Try again")
        if i<(l-1):
            while True:
                ch=input("Do you want to continue to pay the next fine?(y/n)")
                if ch=="y":
                    break
                elif ch=="n":
                    print(90*"*")
                    conn.close()
                    return
                else:
                    print("Incorrect input. Try again.")
    print(90*"*")
    conn.close()
    return
    
    
    
    
    




    
def loan():               #for taking loans
    print("   MENU\n1. Take a loan\n2. Pay EMI\n3. Pay fine")
    while True:
        ch=int(input("What do you want to do? Enter choice: "))
        if ch==1:
            take_loan()
            break
        elif ch==2:
            pay_emi()
            break
        elif ch==3:
            pay_fine()
            break
        else:
            print("Incorrect choice provided. Try again.")


def deposit_withdraw():
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    c_id=input("Enter Customer Id: ")
    query="Select Name from Customer_Info where Customer_Id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    name=mycur.fetchone()
    if name ==(None):
        print("No such customer found. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    c_name=name[0]
    print("  MENU\n1. Deposit money\n2. Withdraw money")
    while True:
        ch=int(input("Enter choice: "))
        if ch==1:
            a=1
            print("Which type of account do you want to deposit to?\n1. Savings Account\n2. Current Account")
            while True:
                c=int(input("Enter choice: "))
                if c==1:
                    query="select * from savings where customer_id="+c_id
                    det=pd.read_sql_query(query,conn)
                    if det.empty:
                        print(c_name+" does not have a Savings account. Returning to main menu.")
                        print(90*"*")
                        conn.close()
                        return
                    print(det)
                    while True:
                        acc_no=input("Enter the account number where you want to deposit:")
                        mycur.execute("select count(*) from savings where account_number=%s",(acc_no,))
                        conn.commit()
                        count=mycur.fetchone()[0]
                        if count==0:
                            print("Account not found. Re-enter account number.")
                            continue
                        mycur.execute("select customer_id from savings where account_number=%s",(acc_no,))
                        conn.commit()
                        cust_id=mycur.fetchone()[0]
                        if c_id!=cust_id:
                            print("That account does not belong to "+c_name+". Re-enter account number.")
                            continue
                        break            
                    amt=int(input("Enter the amount you want to deposit:"))
                    mycur.execute("update savings set Amount=Amount+%s where account_number=%s;",((amt*a),acc_no))
                    conn.commit()
                    create_transaction(acc_no,c_id,c_name,"Savings Deposit",amt)
                    print("Deposit in Savings account successful.")
                    print(90*"*")
                    conn.close()
                    return
                elif c==2:
                    query="select * from current where customer_id="+c_id
                    det=pd.read_sql_query(query,conn)
                    if det.empty:
                        print(c_name+ " does not have a Current Account. Returning to main menu.")
                        print(90*"*")
                        conn.close()
                        return
                    print(det)
                    while True:
                        acc_no=input("Enter the account number where you want to deposit:")
                        mycur.execute("select count(*) from current where account_number=%s",(acc_no,))
                        conn.commit()
                        count=mycur.fetchone()[0]
                        if count==0:
                            print("Account not found. Re-enter account number.")
                            continue
                        mycur.execute("select customer_id from current where account_number=%s",(acc_no,))
                        conn.commit()
                        cust_id=mycur.fetchone()[0]
                        if c_id!=cust_id:
                            print("That account does not belong to "+c_name+". Re-enter account number.")
                            continue
                        break            
                    amt=int(input("Enter the amount you want to deposit:"))
                    mycur.execute("update current set Amount=Amount+%s where account_number=%s;",((amt*a),acc_no))
                    conn.commit()
                    create_transaction(acc_no,c_id,c_name,"Current Deposit",amt)
                    print("Deposit in Current account successful.")
                    print(90*"*")
                    conn.close()
                    return
                else:
                    print("Incorrect input. Try again")
        elif ch==2:
            a=-1
            print("Which type of account do you want to deposit to?\n1. Savings Account\n2. Current Account")
            while True:
                c=int(input("Enter choice: "))
                if c==1:
                    query="select * from savings where customer_id="+c_id
                    det=pd.read_sql_query(query,conn)
                    if det.empty:
                        print(c_name+" does not have a Savings account. Returning to main menu.")
                        print(90*"*")
                        conn.close()
                        return
                    print(det)
                    while True:
                        acc_no=input("Enter the account number where you want to withdraw:")
                        mycur.execute("select count(*) from savings where account_number=%s",(acc_no,))
                        conn.commit()
                        count=mycur.fetchone()[0]
                        if count==0:
                            print("Account not found. Re-enter account number.")
                            continue
                        mycur.execute("select customer_id from savings where account_number=%s",(acc_no,))
                        conn.commit()
                        cust_id=mycur.fetchone()[0]
                        if c_id!=cust_id:
                            print("That account does not belong to "+c_name+". Re-enter account number.")
                            continue
                        break
                    while True:
                        amt=int(input("Enter the amount you want to withdraw:"))
                        mycur.execute("select amount from savings where account_number=%s;",(acc_no,))
                        conn.commit()
                        amount_available=mycur.fetchone()[0]
                        if amt>amount_available:
                            print("Amount attempted to be withdrawn is more than the funds available in Savings Account.")
                            print("Try again.")
                            continue
                        break
                    mycur.execute("update savings set Amount=Amount+%s where account_number=%s;",((amt*a),acc_no))
                    conn.commit()
                    create_transaction(acc_no,c_id,c_name,"Savings Withdrawal",amt)
                    print("Withdrawal in Savings account successful.")
                    print(90*"*")
                    conn.close()
                    return
                elif c==2:
                    query="select * from current where customer_id="+c_id
                    det=pd.read_sql_query(query,conn)
                    if det.empty:
                        print(c_name+ " does not have a Current Account. Returning to main menu.")
                        print(90*"*")
                        conn.close()
                        return
                    print(det)
                    while True:
                        acc_no=input("Enter the account number where you want to withdraw:")
                        mycur.execute("select count(*) from current where account_number=%s",(acc_no,))
                        conn.commit()
                        count=mycur.fetchone()[0]
                        if count==0:
                            print("Account not found. Re-enter account number.")
                            continue
                        mycur.execute("select customer_id from current where account_number=%s",(acc_no,))
                        conn.commit()
                        cust_id=mycur.fetchone()[0]
                        if c_id!=cust_id:
                            print("That account does not belong to "+c_name+". Re-enter account number.")
                            continue
                        break            
                    while True:
                        amt=int(input("Enter the amount you want to withdraw:"))
                        mycur.execute("select amount from current where account_number=%s;",(acc_no,))
                        conn.commit()
                        amount_available=mycur.fetchone()[0]
                        if amt>amount_available:
                            print("Amount attempted to be withdrawn is more than the funds available in Current Account.")
                            print("Try again.")
                            continue
                        break
                    mycur.execute("update current set Amount=Amount+%s where account_number=%s;",((amt*a),acc_no))
                    conn.commit()
                    create_transaction(acc_no,c_id,c_name,"Current Withdrawal",amt)
                    print("Withdrawal in Current account successful.")
                    print(90*"*")
                    conn.close()
                    return
                else:
                    print("Incorrect input. Try again")
        else:
            print("Incorrect input. Try again")




def parameterised_deposit_withdraw(acc_no,amt):
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    acc_type=""
    if acc_no[0]=='1':
        acc_type="Savings"
        mycur.execute("select count(*) from Savings where account_number=%s;",(acc_no,))
        conn.commit()
    elif acc_no[0]=='3':
        acc_type="Current"
        mycur.execute("select count(*) from Current where account_number=%s;",(acc_no,))
        conn.commit()
    c=mycur.fetchone()[0]
    if c==0:
        print("Account does not exist. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    if acc_type=="Savings":
        mycur.execute("update Savings set amount=amount+%s where account_number=%s;",(amt,acc_no))
    elif acc_type=="Current":
        mycur.execute("update Current set amount=amount+%s where account_number=%s;",(amt,acc_no))
    conn.commit()
    print(90*"*")
    conn.close()
    return
                
            
    




def change_month():                                     #increase month by one
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    curr_date=get_date()
    year=int(curr_date.split("-")[0])
    month=int(curr_date.split("-")[1])
    day=int(curr_date.split("-")[2])
    n_year,n_month,n_day=0,0,0
    if month==12:
        n_year=str(year+1)
        n_month="01"
        n_day=str(day)
    else:
        n_year=str(year)
        if month<9:
            n_month="0"+str(month+1)
        else:
            n_month=str(month+1)
        n_day=str(day)
    n_date=n_year+"-"+n_month+"-0"+n_day
    f=open("DATE.txt","w")
    f.write(n_date)
    f.close()
    mycur.execute("update fine set fine_value=1.1*fine_value;")
    conn.commit()
    query="select account_number,customer_id,customer_name,emi from Home_Loan where Paid_this_Month=%s;"
    record=("NO",)
    mycur.execute(query,record)
    conn.commit()
    fine_rec=mycur.fetchall()
    for i in fine_rec:
        acc_no=i[0]
        c_id=i[1]
        c_name=i[2]
        emi=i[3]
        query="update customer_info set credit_score=credit_score-2.5 where credit_score>302 && customer_id=%s;"
        mycur.execute(query,(c_id,))
        conn.commit()
        query="update home_loan set balance=balance-emi;"
        mycur.execute(query)
        conn.commit()
        query="select max(Default_Number) from Fine where customer_id=%s;"
        mycur.execute(query,(c_id,))
        conn.commit()
        ret=mycur.fetchone()
        if ret==(None,):
            def_no=1
        else:
            def_no=ret[0]+1
        loan_type="Home Loan"
        f_value=emi*(1+0.1*def_no)
        mycur.execute("Select Count(*) from Fine;")
        conn.commit()
        if mycur.fetchone()[0]==0:
            def_id="10000000"
        else:
            mycur.execute("Select max(Default_Id) from Fine;")
            conn.commit()
            def_id=str(int(mycur.fetchone()[0])+1)
        query="insert into Fine values(%s,%s,%s,%s,%s,%s,%s,%s);"
        record=(def_id,c_id,c_name,acc_no,loan_type,f_value,def_no,get_date())
        mycur.execute(query,record)
        conn.commit()
    query="select account_number,customer_id,customer_name,emi from Education_Loan where Paid_this_Month=%s;"
    record=("NO",)
    mycur.execute(query,record)
    conn.commit()
    fine_rec=mycur.fetchall()
    for i in fine_rec:
        acc_no=i[0]
        c_id=i[1]
        c_name=i[2]
        emi=i[3]
        query="update customer_info set credit_score=credit_score-2.5 where credit_score>302 && customer_id=%s;"
        mycur.execute(query,(c_id,))
        conn.commit()
        query="update education_loan set balance=balance-emi;"
        mycur.execute(query)
        conn.commit()
        query="select max(Default_Number) from Fine where customer_id=%s;"
        mycur.execute(query,(c_id,))
        conn.commit()
        ret=mycur.fetchone()
        if ret==(None,):
            def_no=1
        else:
            def_no=ret[0]+1
        loan_type="Education Loan"
        f_value=emi*(1+0.1*def_no)
        mycur.execute("Select Count(*) from Fine;")
        conn.commit()
        if mycur.fetchone()[0]==0:
            def_id="10000000"
        else:
            mycur.execute("Select max(Default_Id) from Fine;")
            conn.commit()
            def_id=str(int(mycur.fetchone()[0])+1)
        query="insert into Fine values(%s,%s,%s,%s,%s,%s,%s,%s);"
        record=(def_id,c_id,c_name,acc_no,loan_type,f_value,def_no,get_date())
        mycur.execute(query,record)
        conn.commit()
    query="update home_loan set paid_this_month=%s;"
    record=("NO",)
    mycur.execute(query,record)
    conn.commit()
    query="update education_loan set paid_this_month=%s where %s>=start_date;"
    record=("NO",n_date)
    mycur.execute(query,record)
    conn.commit()
    query="select * from home_loan;"
    rec=pd.read_sql_query(query,conn)
    cond=rec["End_Date"].astype(str).str.lstrip("#")<=get_date()
    rec.where(cond,inplace=True)
    rec.dropna(inplace=True)
    if rec.empty==False:
        print("The following home loan(s) will be deleted because the end date has been reached.")
        print(rec)
    mycur.execute("delete from home_loan where end_date<=%s;",(get_date(),))
    conn.commit()
    query="select Account_Number,Customer_ID,Customer_Name,Loan_Amount, Interest_Rate,Start_Date,End_Date, EMI, Balance, Paid_this_month from education_loan;"
    rec=pd.read_sql_query(query,conn)
    cond=rec["End_Date"].astype(str).str.lstrip("#")<=get_date()
    rec.where(cond,inplace=True)
    rec.dropna(inplace=True)
    if rec.empty==False:
        print("The following education loan(s) will be deleted because the end date has been reached.")
        print(rec)
    mycur.execute("delete from education_loan where end_date<=%s;",(get_date(),))
    conn.commit()
    query="select * from home_loan"
    h_loan=pd.read_sql_query(query,conn)
    if h_loan.empty:
        print("No home loans to be paid this month")
    else:
        print("Home loans to be paid this month:")
        print(h_loan)
    query="select Account_Number,Customer_ID,Customer_Name,Loan_Amount,Interest_rate,Start_Date,End_Date,EMI,Balance,Paid_this_month from education_loan"
    e_loan=pd.read_sql_query(query,conn)
    filter=e_loan["Paid_this_month"]=="NO"
    e_loan.where(filter,inplace=True)
    e_loan.dropna(inplace=True)
    if e_loan.empty:
        print("No education loans to be paid this month")
    else:
        print("Education loans to be paid this month:")
        print(e_loan)
    query="select * from fine;"
    fine_details=pd.read_sql_query(query,conn)
    if fine_details.empty == False:
        print("Fines to be paid this month:")
        print(fine_details)
    mycur.execute("select avg(Interest_Rate) from Savings;")
    conn.commit()
    interest=mycur.fetchone()[0]
    if interest==None:
        interest=0
    query="select account_number,customer_id,customer_name,amount from Savings;"
    mycur.execute(query)
    conn.commit()
    rec=mycur.fetchall()
    mycur.execute("select count(*) from savings;")
    conn.commit()
    length=mycur.fetchone()[0]
    for i in range (length):
        acc_no=rec[i][0]
        c_id=rec[i][1]
        c_name=rec[i][2]
        amt=rec[i][3]
        create_transaction(acc_no,c_id,c_name,"Savings Interest",amt*(interest/100))
    query="update savings set amount=amount+%s*amount;"
    record=((interest/100),)
    mycur.execute(query,record)
    conn.commit()
    mycur.execute("select avg(Interest_Rate) from Fixed_Deposit;")
    conn.commit()
    interest=mycur.fetchone()[0]
    if interest!=0 and interest!=None:
        query="select account_number,customer_id,customer_name,amount from Fixed_Deposit;"
        mycur.execute(query)
        conn.commit()
        record=mycur.fetchall()
        mycur.execute("select count(*) from Fixed_Deposit;")
        conn.commit()
        length=mycur.fetchone()[0]
        for i in range (length):
            acc_no=record[i][0]
            c_id=record[i][1]
            c_name=record[i][2]
            amt=record[i][3]
            create_transaction(acc_no,c_id,c_name,"Fixed Deposit Interest",amt*(interest/100))
        query="update fixed_deposit set amount=amount+%s*amount;"
        record=((interest/100),)
        mycur.execute(query,record)
        date=get_date()
        query="select account_number,customer_id,customer_name,amount from Fixed_Deposit where %s=End_Date;"
        mycur.execute(query,(date,))
        conn.commit()
        record=mycur.fetchall()
        for i in record:
            c_id=i[1]
            query="select account_number from savings where customer_id=%s;"
            mycur.execute(query,(c_id,))
            conn.commit()
            sav_acc=mycur.fetchone()[0]
            amt=i[3]
            parameterised_deposit_withdraw(sav_acc,amt)
            create_transaction(i[0],c_id,i[2],"FD to Savings",-1*amt)
            create_transaction(sav_acc,c_id,i[2],"FD to Savings",amt)            
            print("All amount in "+i[2]+"'s fixed deposit account of Acc. No.: "+i[0]+" has been transferred to the Savings Account of Acc. No. "+sav_acc+"\ndue to the end of time period of fixed deposit account.")
        query="delete from fixed_deposit where %s=End_Date;"
        record=(date,)
        mycur.execute(query,record)
        conn.commit()
    print(90*"*")
    
    
    
    
    
    



def create_transaction(acc_no,cust_id,cust_name,acc_type,amount):
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    mycur.execute("Select Count(*) from Transactions;")
    conn.commit()
    if mycur.fetchone()[0]==0:
        transaction_id="1000000"
    else:
        mycur.execute("Select max(Transaction_Id) from Transactions;")
        conn.commit()
        transaction_id=str(int(mycur.fetchone()[0])+1)
    date=get_date()
    query="Insert into transactions values(%s,%s,%s,%s,%s,%s,%s);"
    record=(transaction_id,acc_no,cust_id,cust_name,acc_type,amount,date)
    mycur.execute(query,record)
    conn.commit()



def customer_details():
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    c_id=input("Enter Customer ID: ")
    query="Select Name from Customer_Info where Customer_Id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    name=mycur.fetchone()
    if name ==(None):
        print("No such customer found. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    c_name=name[0]
    print("   MENU\n1. View personal details\n2. View account details\n3. View loan details\n4. View fines\n5. View transactions")
    ch=int(input("Enter choice: "))
    if ch==1:
        query="select * from customer_info where customer_id="+c_id
        per_det=pd.read_sql_query(query,conn)
        print(per_det)
    elif ch==2:
        query="select * from savings where customer_id="+c_id
        sav_det=pd.read_sql_query(query,conn)
        if sav_det.empty == False:
            print("Savings Account:")
            print(sav_det)
        query="select * from current where customer_id="+c_id
        cur_det=pd.read_sql_query(query,conn)
        if cur_det.empty == False:
            print("Current Account:")
            print(cur_det)
        query="select * from fixed_deposit where customer_id="+c_id
        fd_det=pd.read_sql_query(query,conn)
        if fd_det.empty == False:
            print("Fixed Deposit Account:")
            print(fd_det)
        if sav_det.empty and cur_det.empty and fd_det.empty:
            print(c_name+" does not have any account.")
    elif ch==3:
        query="select * from home_loan where customer_id="+c_id
        home_det=pd.read_sql_query(query,conn)
        if home_det.empty == False:
            print("Home Loan:")
            print(home_det)
        query="select Account_Number,Customer_ID,Customer_Name,Loan_Amount,Interest_rate,Start_Date,End_Date,EMI,Balance,Paid_this_month from education_loan where customer_id="+c_id
        edu_det=pd.read_sql_query(query,conn)
        if edu_det.empty == False:
            print("Education Loan:")
            print(edu_det)
        if home_det.empty and edu_det.empty:
            print(c_name+" has not taken any loan.")
    elif ch==4:
        query="select * from fine where customer_id="+c_id
        fin_det=pd.read_sql_query(query,conn)
        if fin_det.empty == False:
            print("Fines:")
            print(fin_det)
        else:
            print("No fines accumulated by "+c_name)
    elif ch==5:
        cur_date=get_date()
        print("   TRANSACTIONS FOR WHICH TIME PERIOD?\n1. This month\n2. Last 3 months\n3. Last 6 months\n4. Last year\n5. Last 5 years\n6. All time")
        c=int(input("Enter choice: "))
        if c==1:
            query="select * from transactions where date='"+cur_date+"' and customer_id="+c_id
            tr_det=pd.read_sql_query(query,conn)
            if tr_det.empty == False:
                print("Transactions this month:")
                print(tr_det)
            else:
                print("No transactions by "+c_name+" this month")
        elif c==2:
            end_date=get_end_date(cur_date,-2)             #not -3 because it also includes this month
            query="select * from transactions where date>='"+end_date+"' and customer_id="+c_id
            tr_det=pd.read_sql_query(query,conn)
            if tr_det.empty == False:
                print("Transactions in last 3 months:")
                print(tr_det)
            else:
                print("No transactions by "+c_name+" in last 3 months")
        elif c==3:
            end_date=get_end_date(cur_date,-5)             #not -5 because it also includes this month
            query="select * from transactions where date>='"+end_date+"' and customer_id="+c_id
            tr_det=pd.read_sql_query(query,conn)
            if tr_det.empty == False:
                print("Transactions in last 5 months:")
                print(tr_det)
            else:
                print("No transactions by "+c_name+" in last 6 months")
        elif c==4:
            end_date=get_end_date(cur_date,-11)             #not -11 because it also includes this month
            query="select * from transactions where date>='"+end_date+"' and customer_id="+c_id
            tr_det=pd.read_sql_query(query,conn)
            if tr_det.empty == False:
                print("Transactions in last year:")
                print(tr_det)
            else:
                print("No transactions by "+c_name+" in last year")
        elif c==5:
            end_date=get_end_date(cur_date,-59)             #not -59 because it also includes this month
            query="select * from transactions where date>='"+end_date+"' and customer_id="+c_id
            tr_det=pd.read_sql_query(query,conn)
            if tr_det.empty == False:
                print("Transactions in last 5 years:")
                print(tr_det)
            else:
                print("No transactions by "+c_name+" in last 5 years")
        elif c==6:
            query="select * from transactions where customer_id="+c_id
            tr_det=pd.read_sql_query(query,conn)
            if tr_det.empty == False:
                print("Transaction by "+c_name+":")
                print(tr_det)
            else:
                print("No transactions by "+c_name)
    
    print(90*"*")
    conn.close()
    return
    
def change_customer_details():
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    c_id=input("Enter Customer ID: ")
    query="Select count(*) from Customer_Info where Customer_Id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    count=mycur.fetchone()[0]
    if count ==0:
        print("No such customer found. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    print("  MENU\n1. Change Name\n2. Change Phone Number\n3. Change Monthly Income")
    while True:
        ch=int(input("Enter choice: "))
        if ch==1:
            name=input("Enter new name: ")
            query="update customer_info set Name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            query="update savings set customer_name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            query="update current set customer_name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            query="update fixed_deposit set customer_name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            query="update home_loan set customer_name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            query="update education_loan set customer_name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            query="update transactions set customer_name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            query="update fine set customer_name=%s where customer_id=%s;"
            record=(name,c_id)
            mycur.execute(query,record)
            conn.commit()
            print("Name successfully updated.")
            break
        elif ch==2:
            ph_no=input("Enter new phone number: ")
            while len(ph_no)!=10 or ph_no.isdigit()==False:
                print("Entered phone number is either of incorrect length or has characters which are not digits.\nPlease try again.")
                ph_no=input("Enter newphone number: ")
            query="update customer_info set Phone_Number=%s where customer_id=%s;"
            record=(ph_no,c_id)
            mycur.execute(query,record)
            conn.commit()
            print("Phone Number successfully updated.")
            break
        elif ch==3:
            query="select monthly_income,credit_score from customer_info where customer_id=%s;"
            mycur.execute(query,(c_id,))
            conn.commit()
            rec=mycur.fetchone()
            cur_inc=rec[0]
            cur_cr=rec[1]
            if cur_inc<=10000:
                i_cred_sc=500
            elif cur_inc<=50000:
                i_cred_sc=650
            elif cur_inc<=100000:
                i_cred_sc=700
            else:
                i_cred_sc=800
            d_cr=cur_cr-i_cred_sc
            mon_inc=int(input("Enter new monthly income in Rs: "))
            query="update customer_info set Monthly_Income=%s where customer_id=%s;"
            record=(mon_inc,c_id)
            mycur.execute(query,record)
            conn.commit()
            if mon_inc<=10000:
                cred_sc=500
            elif mon_inc<=50000:
                cred_sc=650
            elif mon_inc<=100000:
                cred_sc=700
            else:
                cred_sc=800
            cred_sc+=d_cr
            query="update customer_info set Credit_Score=%s where customer_id=%s;"
            record=(cred_sc,c_id)
            mycur.execute(query,record)
            conn.commit()
            print("Monthly income successfully updated")
            break
        else:
            print("Incorrect input. Try again.")
    print(90*"*")
    conn.close()
    return
        
def forgot_customerID():
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    name=input("Enter name of customer: ")
    ph_no=input("Enter phone number of customer: ")
    query="select customer_id from customer_info where Name=%s and Phone_Number=%s;"
    record=(name,ph_no)
    mycur.execute(query,record)
    conn.commit()
    rec=mycur.fetchone()
    if rec==None:
        print("Details do not match. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    c_id=rec[0]
    print("Customer ID of "+name+": "+c_id)
    print(90*"*")
    conn.close()
    return


def forgot_account_details():
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    c_id=input("Enter Customer ID: ")
    query="Select count(*) from Customer_Info where Customer_Id=%s;"
    record=(c_id,)
    mycur.execute(query,record)
    conn.commit()
    count=mycur.fetchone()[0]
    if count ==0:
        print("No such customer found. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    print("   ACCOUNT NUMBER FOR WHICH TYPE OF ACCOUNT DO YOU WANT TO RETRIEVE?\n1. Savings Account\n2. Current Account\n3. Fixed Deposit Account\n4. Home Loan Account\n5. Education Loan Account")
    while True:
        ch=int(input("Enter choice: "))
        if ch==1:
            query="select account_number from savings where customer_id=%s;"
            mycur.execute(query,(c_id,))
            break
        elif ch==2:
            query="select account_number from current where customer_id=%s;"
            mycur.execute(query,(c_id,))
            break
        elif ch==3:
            query="select account_number from fixed_deposit where customer_id=%s;"
            mycur.execute(query,(c_id,))
            break
        elif ch==4:
            query="select account_number from home_loan where customer_id=%s;"
            mycur.execute(query,(c_id,))
            break
        elif ch==5:
            query="select account_number from education_loan where customer_id=%s;"
            mycur.execute(query,(c_id,))
            break
        else:
            print("Incorrect input. Try again.")
    acc_no=mycur.fetchall()
    if acc_no==[]:
        print("No such account exists. Returning to main menu.")
        print(90*"*")
        conn.close()
        return
    print("Requested accounts of customer:")
    for i in acc_no:
        print(i[0])
    print(90*"*")
    conn.close()
    return


def restart_database():
    conn = mysql.connector.connect(host=host_var,user=user_var,password=pwd_var,database='Banking_System')
    mycur=conn.cursor(buffered=True)
    while True:
        c=input("Are you sure you want to drop the database? All data currently entered in the database will be lost.(y/n)")
        if c=='y':
            break
        elif c=="n":
            print("Database not dropped.")
            print(90*"*")
            conn.close()
            return
        else:
            print("Incorrect input. Try again.")
    mycur.execute("drop database banking_system;")
    conn.commit()
    print(90*"*")
    conn.close()
    os.remove("DATE.txt")
    os.remove("MYSQL_DETAILS.txt")
    print("Database and ancillary files deleted.")
    return







    

def main():                     #used to call all functions
    conn=mysql.connector.connect(host=host_var, user=user_var, password=pwd_var, database='mysql')
    mycur=conn.cursor(buffered=True)
    mycur.execute("show databases;")
    conn.commit()
    dbs=mycur.fetchall()
    conn.close()
    s=0
    for i in dbs:
        if i[0]=="banking_system":
            s=1
            break
    if s==0:
        setup()
        
    while True:
        print("Current date: "+get_date())
        print("   MENU\n1. Create New User\n2. Create New Account\n3. Loans/Fine\n4. Deposit/Withdraw Money\n5. Customer Transaction and Account Details\n6. Change Customer Personal Details\n7. Forgot Customer ID\n8. Forgot Account Details\n9. Change Month\n10. Exit\n11. Restart Database")
        ch=input("Enter choice: ")
        if ch.isdigit():
            c=int(ch)
        else:
            print("Incorrect input. Try again")
            continue
        if c==1:
            create_user()
        elif c==2:
            create_account()
        elif c==3:
            loan()
        elif c==4:
            deposit_withdraw()
        elif c==5:
            customer_details()
        elif c==6:
            change_customer_details()
        elif c==7:
            forgot_customerID()
        elif c==8:
            forgot_account_details()
        elif c==9:
            change_month()
        elif c==10:
            print("Thank you for using this system.")
            print(90*"*")
            break
        elif c==11:
            restart_database()
            break
        else:
            print("Incorrect input. Try again")
            continue
        
main()
