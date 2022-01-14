import datetime
from email.policy import HTTP
import hashlib
import uuid
import smtplib
import random
import jwt
from datetime import date,datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from typing import Optional

from dal.user import UserModelDAL
from dal.transaction import TransactionModelDAL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, Header
from model.user import LoginModel, UserModel, ForgotPasswordModel, ResetPasswordModel, ChangePasswordModel, UpdateUserModel
from model.transaction import TransactionModel, SendMoneyModel, RequestMoneyModel

app = FastAPI()
user_model_dal = UserModelDAL()
transaction_model_dal = TransactionModelDAL()
hash_256 = hashlib.sha256()

token_encrypter_secret = "jopavaeiva3ser223av21r233fasdop890"

@app.get("/")
def read_root():
    return {"Message": "Welcome to Generic wallet"}

# user API's
@app.post("/user/signup")
async def sign_up_user(user: UserModel):

    # checking if user email does not already exists
    user_datas = user_model_dal.read({"email" : user.email})

    if len(user_datas) > 0:
        raise HTTPException(status_code=400, detail="user by that email already exists")

    # hash user password
    hashed_password = hashlib.sha256(str(user.password).encode('utf-8'))
    user.password = hashed_password.hexdigest()
    
    # create user id
    user.id = str(uuid.uuid4());

    # create user wallet id
    user.wallet_id = random.randint(1111111111, 9999999999)

    # create user
    await user_model_dal.create(user_model=user)
    message = "this is a welcome email from Generic wallet";
    send_email(user.email, message, "Welcome dude")
    
    return user.to_json()

@app.post("/user/login")
async def login_user(loginModel: LoginModel):
    
   # compare hash of password
    hashed_password = hashlib.sha256(str(loginModel.password).encode('utf-8')).hexdigest()

    user_query = {"email" : loginModel.email}
    users =  user_model_dal.read(query=user_query, limit=1)
    
    if len(users) == 0:
        return HTTPException(status_code=401, detail="email does not exist") 

    user = users[0] 

    if user.password != hashed_password:
        return HTTPException(status_code=401, detail="email and password do not match")
   
    
    # generate token
    after_six_months = date.today() + relativedelta(months=+6)
    
    encoded_jwt = jwt.encode({
        "id" : user.id,
        "expiration" : str(after_six_months)
    }, token_encrypter_secret, algorithm="HS256")


    return {"token" : str(encoded_jwt).replace("b'","").replace("'","")}

@app.post("/user/forgot_password")
async def forgot_password(forgotModel: ForgotPasswordModel): 
    user_email = forgotModel.email
    reset_code = random.randint(111111, 999999)
    user_query = {"email" : user_email}
    users =  user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="email does not exist") 
    user = users[0]
    user_payload = user.payload
    user_payload["resetCode"] = reset_code
    update_data = { "$set": { 'payload': user_payload} }
    # update user here
    user_model_dal.update(user_query, update_data)
    send_email(user.email, "You have requested reset code", f"Your reset code is : {reset_code}")
    return {"message" : "your reset code has been sent"}

@app.get("/user/detail")
async def get_user_detail(token:str=Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)

    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=404, detail="user not found")
    return users[0]

@app.post("/user/reset_password")
async def reset_password(resetPassword: ResetPasswordModel):
    # check if the reset code is correct
    user_query = {"email" : resetPassword.email}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=400, detail="user by email not found")

    user = users[0]
    user_payload = user.payload

    if str(user_payload["resetCode"]) != str(resetPassword.reset_code):
        return HTTPException(status_code=401, detail="reset code is not correct")

    new_hashed_password = hashlib.sha256(str(resetPassword.new_password).encode('utf-8')).hexdigest()
    update_data = {"$set" : {'password' : new_hashed_password}}
    user_model_dal.update(user_query, update_data) # password successfuly updated and hashed
    
    # send email to user
    send_email(user.email, "Your password has been changed", "Your password has been changed, if this is not you then report here.")
    return {"message" : "your password has been changed"}

@app.post("/user/change_password")
async def change_password(changePassword: ChangePasswordModel, token: str = Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)

    hashed_incomming_old_password = hashlib.sha256(str(changePassword.old_password).encode('utf-8')).hexdigest()
    user_query = {"id": user_id}

    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="user does not exist")

    user = users[0]
    if user.password != hashed_incomming_old_password:
        return HTTPException(status_code=400, detail="user old password is not correct")

    hashed_new_password = hashlib.sha256(str(changePassword.new_password).encode('utf-8')).hexdigest()
    update_data = {'password' : hashed_new_password}
    user_model_dal.update(user_query, update_data)

    send_email(user.email, "Your password has been changed", "Your password has been successfully changed")
    return {"message": "password successfully changed"}
    
@app.put("/user/update_profile")
async def update_profile(updateUser: UpdateUserModel, token: str=Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)

    user_query = {"id" : user_id}
    user_model_dal.update(user_query,updateUser.to_json())
    return {"message" : "user successfully updated"}

# transaction API's
@app.post("/transaction/send_money")
async def send_money(sendMoney: SendMoneyModel, token: str=Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)

    sender_query = {"id" : user_id}
    sender_users = user_model_dal.read(query=sender_query, limit=1)
    if len(sender_users) == 0:
        return HTTPException(status_code=401, detail="user does not exist")
    
    reciever_query = {"email" : sendMoney.to_user_email}
    recievers_users = user_model_dal.read(query=reciever_query, limit=1)
    if len(recievers_users) == 0:
        return HTTPException(status_code=401, detail="no reciever by email found")

    sender = sender_users[0]
    reciever = recievers_users[0]

    if sender.available_balance < sendMoney.amount: # user does not have enough credit
        return HTTPException(status_code=400, detail="User does not have enough balance")

    transaction_data = TransactionModel(
        id=str(uuid.uuid4()),
        amount=sendMoney.amount,
        payload=sendMoney.payload,
        from_user=sender,
        to_user=reciever,
        trn_type="transfer",
        first_modified=str(datetime.now().isoformat()),
        last_modified=str(datetime.now().isoformat())
    )

    transaction_res = await transaction_model_dal.create(transaction_data)

    transaction_query = {"_id" : transaction_res.inserted_id}
    transaction_response = transaction_model_dal.read(transaction_query)
    if len(transaction_response) > 0:
        send_email(sender.email, "Transfer is successful", "Transfer is sucessful")
        return {"message" : "transfer is successful"}

    return HTTPException(status_code=400, detail="transfer failed")
   
@app.get("/transaction/get_all")
async def get_all_transactions(token: str=Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)
    transaction_query = {"$or" : [
        {"fromUser.id" : user_id},
        {"toUser.id" : user_id}
    ]}
    transactions = transaction_model_dal.read(query=transaction_query,limit=24)
    print(transactions)
    return transactions

@app.post("/transaction/request_money")
async def request_money(requestMoney: RequestMoneyModel, token: str=Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)


    # create request transaction document
    requester_query = {"id" : user_id}
    requester_users = user_model_dal.read(query=requester_query, limit=1)
    if len(requester_users) == 0:
        return HTTPException(status_code=400, detail="user does not exist")

    requested_query = {"email" : requestMoney.to_user_email}
    requested_users = user_model_dal.read(query=requested_query, limit=1)

    if len(requested_users) == 0:
        return HTTPException(status_code=400, detail = "requested user by email not found")

    requester_user = requester_users[0]
    requested_user = requested_users[0]

    transaction_data = TransactionModel(
        id=str(uuid.uuid4()),
        amount=requestMoney.amount,
        payload=requestMoney.payload,
        from_user=requester_user,
        to_user=requested_user,
        trn_type="transfer_request",
        first_modified=str(datetime.now().isoformat()),
        last_modified=str(datetime.now().isoformat())
    )

    await transaction_model_dal.create(transaction_data)

    # send email to the person being requested
    send_email(requester_user.email, "Your request has been sent", f"Your request for {str(requestMoney.amount)} has been sent")

    # send email to the person requesting the transaction
    send_email(requested_user.email, "You have a request to transfer money", f"You have a request to transfer money to {requester_user.name} for amount {str(requestMoney.amount)} \n use the below link to complete transaction http://localhost:8000/transaction/complete_request?id={transaction_data.id}")
    
    return {"message" : "request has been sent"}
    

def validate_token_and_get_user(token):
    if token == None:
        return "no token provided"

    decoded_token_data = {}
    try:
        decoded_token_data = jwt.decode(token,token_encrypter_secret, algorithms="HS256")
    except Exception as e:
        return "token is corrupted"

    user_id = decoded_token_data["id"]
    expiration = parser.parse(decoded_token_data["expiration"])
    now = datetime.now()

    if expiration < now: # token expired
        return "token has expired"

    return user_id


def send_email(recipients, body, subject):
    try:
        message = MIMEMultipart()
        message['From'] = "nibjobs.com@gmail.com"
        message['To'] = recipients
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login("nibjobs.com@gmail.com", "nkyudfhgucciurcr") #login with mail_id and password
        text = message.as_string()
        session.sendmail("nibjobs.com@gmail.com", recipients, text)
        session.quit()

    except Exception as e:
        print(e)
        print("Error: unable to send email") 