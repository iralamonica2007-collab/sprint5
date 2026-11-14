from fastapi import FastAPI, HTTPException, Header
from datetime import date
import function
from pydantic import BaseModel, Field

app = FastAPI()


# Check user authentication and authorization

def check_role(token, allowed_roles):

    username = function.verify_token(token=token, token_type="access")

    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    role = function.get_user_role(username)

    if role is None:
        raise HTTPException(status_code=401, detail="User not found")

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You do not have permission")

    return username


# Model 1: Create Package
class PackageCreate(BaseModel):
    package_name: str
    destination: str
    weight: float = Field(gt=0)
    arrival_date: date


# Model 2: Update Package
class PackageUpdate(BaseModel):
    package_name: str | None = None
    destination: str | None = None
    weight: float | None = Field(default=None, gt=0)
    arrival_date: date | None = None
    status: str | None = None


# Model 3: Create Dispatch Batch
class DispatchBatchCreate(BaseModel):
    batch_name: str
    destination: str
    vehicle_number: str
    dispatch_date: date
    package_ids: str


# Model 4: Login
class LoginRequest(BaseModel):
    username: str
    password: str


# Model 5: Register
class RegisterRequest(BaseModel):
    user_name: str
    password: str
    role: str 
    



# Endpoint 1: POST /packages
# Purpose: Register a new package

@app.post("/packages")
def add_package(package: PackageCreate, token: str = Header(None)):

    check_role(token, ["admin", "staff"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    package_data = function.add_package(
        package.package_name,
        package.destination,
        package.weight,
        str(package.arrival_date)
    )

    return package_data


# Endpoint 2: GET /packages/{package_id}
# Purpose: Get package details using package ID

@app.get("/packages/{package_id}")
def get_package(package_id: int, token: str = Header(None)):

    check_role(token, ["admin", "staff"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    package = function.get_package_by_id(package_id)

    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")

    return package


# Endpoint 3: PATCH /packages/{package_id}
# Purpose: Update package details

@app.patch("/packages/{package_id}")
def update_package(package_id: int, package: PackageUpdate, token: str = Header(None)):

    check_role(token, ["admin", "staff"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    data = package.model_dump(exclude_unset=True)

    if "arrival_date" in data and data["arrival_date"] is not None:
        data["arrival_date"] = str(data["arrival_date"])

    result = function.update_package(
        package_id,
        data.get("package_name"),
        data.get("destination"),
        data.get("weight"),
        data.get("arrival_date"),
        data.get("status")
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Package not found")

    if result == "invalid_status":
        raise HTTPException(status_code=400, detail="Invalid package status")

    return result


# Endpoint 4: DELETE /packages/{package_id}
# Purpose: Delete a package if it is not dispatched

@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token: str = Header(None)):

    check_role(token, ["admin"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    result = function.delete_package(package_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Package not found")

    if result == "dispatched":
        raise HTTPException(status_code=409, detail="Dispatched package cannot be deleted")

    return result


# Endpoint 5: GET /packages
# Purpose: Get all packages with optional filters

@app.get("/packages")
def get_all_packages(
    destination: str = None,
    status: str = None,
    arrival_date: date = None,
    token: str = Header(None)
):

    check_role(token, ["admin", "staff"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    if arrival_date is not None:
        arrival_date = str(arrival_date)

    return function.get_all_packages(
        destination=destination,
        status=status,
        arrival_date=arrival_date
    )


# Endpoint 6: GET /dispatch-batches
# Purpose: Get all dispatch batches with optional filters

@app.get("/dispatch-batches")
def get_all_dispatch_batches(
    destination: str = None,
    vehicle_number: str = None,
    status: str = None,
    token: str = Header(None)
):

    check_role(token, ["admin", "staff"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    batches = function.get_all_dispatch_batches(
        destination,
        vehicle_number,
        status
    )

    return batches


# Endpoint 7: GET /analytics
# Purpose: Display warehouse statistics

@app.get("/analytics")
def get_analytics(token: str = Header(None)):

    check_role(token, ["admin"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    analytics = function.get_analytics()

    return analytics


# Endpoint 8: POST /dispatch-batches
# Purpose: Create a dispatch batch and assign packages

@app.post("/dispatch-batches")
def add_dispatch_batch(batch: DispatchBatchCreate, token: str = Header(None)):

    check_role(token, ["admin"])

    # username = function.verify_token(token=token,token_type="access")
    # if not username:
    #     raise HTTPException(status_code=401,detail="Invalid or expired token")

    result = function.add_dispatch_batch(
        batch.batch_name,
        batch.destination,
        batch.vehicle_number,
        str(batch.dispatch_date),
        batch.package_ids
    )

    if result == "package_not_found":
        raise HTTPException(status_code=404, detail="Package not found or invalid package ID")

    if result == "destination_mismatch":
        raise HTTPException(status_code=400, detail="Package destination does not match batch destination")

    if result == "package_not_pending":
        raise HTTPException(status_code=409, detail="Package is already assigned or dispatched")

    if result == "duplicate_package":
        raise HTTPException(status_code=400, detail="Duplicate package IDs are not allowed")

    return result


# Endpoint 9: POST /login
# Purpose: Login user and generate tokens

@app.post("/login")
def login(data: LoginRequest):

    token = function.verify_login(username=data.username,password=data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    return token


# Endpoint 10: POST /refresh
# Purpose: Generate a new access token

@app.post("/refresh")
def refresh(refresh_token: str = Header(None)):

    username = function.verify_token(token=refresh_token,token_type="refresh")

    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")

    access_token = function.create_token(username=username,token_type="access")

    return {"access_token": access_token}


# Endpoint 11: POST /register
# Purpose: Register a new user with a selected role

@app.post("/register")
def register_user(data: RegisterRequest):

    if data.role not in ["admin", "staff"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    if function.register_user(
        user_name=data.user_name,
        password=data.password,
        role=data.role
    ):
        return {"message": "user registered successfully"}

    raise HTTPException(status_code=400, detail="User already exists")

# @app.post("/register")
# def register_user(data: RegisterRequest):

#     if function.register_user(user_name=data.user_name,password=data.password):
#         return {"message": "user registered successfully"}

#     raise HTTPException(status_code=400, detail="User already exists")