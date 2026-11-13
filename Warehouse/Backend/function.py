#Authentication means verifying the identity of a user.
#Authorization checks the user's permissions after their identity has been verified.
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime, timedelta, timezone

import jwt #json web token. When someone logs in with a valid username and password, your application generates a token.
           #That token is sent with requests to protected endpoints.
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError          

ph = PasswordHasher()

# Database connection
DB_PATH = "warehouse.db" 
engine = create_engine(f"sqlite:///{DB_PATH}")


USERNAME="Monica"
PASSWORD="333"

ACCESS_TOKEN_EXPIRY= 15 #mins
REFRESH_TOKEN_EXPIRY = 7 * 24 *60 #mins
SECRET_KEY ="SECRET123"
ALGORITHM = "HS256"

# Create base class
Base = declarative_base()


# Dispatch Batch Table
class DispatchBatch(Base):
    __tablename__ = "dispatch_batches"

    id = Column(Integer, primary_key=True)
    batch_name = Column(String)
    destination = Column(String)
    vehicle_number = Column(String)
    dispatch_date = Column(String)
    status = Column(String, default="Prepared")


# Package Table
class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)
    package_name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(String)
    status = Column(String, default="Pending")
    dispatch_batch_id = Column(Integer, ForeignKey("dispatch_batches.id"))
    
class User(Base):
    __tablename__ = "Users"
    user_id = Column[int](Integer, primary_key = True)
    user_name = Column[str](String)
    password = Column[str](String)
    


# Create database tables
Base.metadata.create_all(engine)

def add_package(package_name, destination, weight, arrival_date):

    session = Session(engine)

    package = Package(
        package_name=package_name,
        destination=destination,
        weight=weight,
        arrival_date=arrival_date
    )

    session.add(package)
    session.commit()

    response = {
        "id": package.id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }

    session.close()

    return response


# Endpoint 2: GET /packages/{package_id}
# Purpose: Get package details using package ID

def get_package_by_id(package_id):

    session = Session(engine)
    package = session.get(Package, package_id)

    if package is None:
        session.close()
        return None

    response = {
        "id": package.id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }

    session.close()
    return response

# Endpoint 3: PATCH /packages/{package_id}
# Purpose: Update package details

def update_package(package_id, package_name=None, destination=None, weight=None, arrival_date=None, status=None):

    session = Session(engine)
    package = session.get(Package, package_id)

    if package is None:
        session.close()
        return None

    if package_name is not None:
        package.package_name = package_name

    if destination is not None:
        package.destination = destination

    if weight is not None:
        package.weight = weight

    if arrival_date is not None:
        package.arrival_date = arrival_date
        
    if status is not None:

       if status not in ["Pending", "Assigned", "Dispatched"]:
        session.close()
        return "invalid_status"

    package.status = status   

    session.commit()

    response = {
        "id": package.id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }

    session.close()
    return response

# Endpoint 4: DELETE /packages/{package_id}
# Purpose: Delete a package if it is not dispatched

def delete_package(package_id):

    session = Session(engine)

    package = session.get(Package, package_id)

    if package is None:
        session.close()
        return None

    if package.status == "Dispatched":
        session.close()
        return "dispatched"

    session.query(Package).filter(Package.id == package_id).delete()
    session.commit()

    session.close()
    return {"message": "Package deleted successfully"}

# Endpoint 5: GET /packages
# Purpose: Get all packages with optional filters

def get_all_packages(destination=None, status=None, arrival_date=None):

    session = Session(engine)
    packages = session.query(Package)

    if destination:
        packages = packages.filter(Package.destination == destination)

    if status:
        packages = packages.filter(Package.status == status)

    if arrival_date:
        packages = packages.filter(Package.arrival_date == arrival_date)

    packages = packages.all()

    response = []

    for package in packages:
        temp_package = {
            "id": package.id,
            "package_name": package.package_name,
            "destination": package.destination,
            "weight": package.weight,
            "arrival_date": package.arrival_date,
            "status": package.status
        }

        response.append(temp_package)

    session.close()
    return response

# Endpoint 6: GET /dispatch-batches
# Purpose: Get all dispatch batches with optional filters

def get_all_dispatch_batches(destination=None, vehicle_number=None, status=None):

    session = Session(engine)
    batches = session.query(DispatchBatch)

    if destination:
        batches = batches.filter(DispatchBatch.destination == destination)

    if vehicle_number:
        batches = batches.filter(DispatchBatch.vehicle_number == vehicle_number)

    if status:
        batches = batches.filter(DispatchBatch.status == status)

    batches = batches.all()

    response = []

    for batch in batches:
        temp_batch = {
            "id": batch.id,
            "batch_name": batch.batch_name,
            "destination": batch.destination,
            "vehicle_number": batch.vehicle_number,
            "dispatch_date": batch.dispatch_date,
            "status": batch.status
        }

        response.append(temp_batch)

    session.close()
    return response

# Endpoint 7: GET /analytics
# Purpose: Get warehouse statistics

def get_analytics():

    session = Session(engine)
    total_packages = session.query(Package).count()

    pending_packages = session.query(Package).filter(
        Package.status == "Pending"
    ).count()

    assigned_packages = session.query(Package).filter(
        Package.status == "Assigned"
    ).count()

    pending_packages = pending_packages + assigned_packages

    dispatched_packages = session.query(Package).filter(
        Package.status == "Dispatched"
    ).count()

    packages = session.query(Package).all()

    destination_count = {}

    for package in packages:
        destination = package.destination

        if destination in destination_count:
            destination_count[destination] += 1
        else:
            destination_count[destination] = 1

    response = {
        "total_packages_received": total_packages,
        "pending_dispatch": pending_packages,
        "dispatched": dispatched_packages,
        "destination_wise_count": destination_count
    }

    session.close()
    return response

# Endpoint 8: POST /dispatch-batches
# Purpose: Create a dispatch batch and assign packages

def add_dispatch_batch(batch_name, destination, vehicle_number,dispatch_date, package_ids):

    session = Session(engine)
    package_ids = package_ids.split(",")

    if not package_ids or package_ids == [""]:
        session.close()
        return "package_not_found"

    package_ids = [package_id.strip() for package_id in package_ids]

    if len(package_ids) != len(set(package_ids)):
        session.close()
        return "duplicate_package"

    packages = []

    for package_id in package_ids:

        if not package_id.isdigit():
            session.close()
            return "package_not_found"

        package = session.get(Package, int(package_id))

        if package is None:
            session.close()
            return "package_not_found"

        if package.destination != destination:
            session.close()
            return "destination_mismatch"

        if package.status != "Pending":
            session.close()
            return "package_not_pending"

        packages.append(package)

    batch = DispatchBatch(
        batch_name=batch_name,
        destination=destination,
        vehicle_number=vehicle_number,
        dispatch_date=dispatch_date
    )

    session.add(batch)
    session.commit()

    for package in packages:
        package.dispatch_batch_id = batch.id
        package.status = "Assigned"

    session.commit()

    response = {
        "id": batch.id,
        "batch_name": batch.batch_name,
        "destination": batch.destination,
        "vehicle_number": batch.vehicle_number,
        "dispatch_date": batch.dispatch_date,
        "status": batch.status,
        "assigned_package_ids": [
            package.id for package in packages
        ]
    }

    session.close()
    return response



def verify_login(username , password):
    session = Session(engine)
    user = session.query(User).filter_by(user_name = username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError :
        session.close()
        return False  
    session.close()
    access_token = create_token(username=username, token_type="access")
    refresh_token = create_token(username=username, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}  
        
    
       
    
    


def create_token(username, token_type): 
    time = ACCESS_TOKEN_EXPIRY
    if token_type =="refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time) 
    }
    token = jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
         
    except:
        return False
    if payload["token_type"] == token_type:
        return payload["username"]
    return False
    
   
    #----users---
def register_user(user_name:str, password:str):
    session = Session(engine)
    user_exists = session.query(User).filter_by(user_name=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(User(user_name=user_name,password=ph.hash(password)))
    session.commit()
    session.close()
    return True
    