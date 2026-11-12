from fastapi import FastAPI, HTTPException ,Header
from datetime import date
import function

app = FastAPI()


# Endpoint 1: POST /packages
# Purpose: Register a new package

@app.post("/packages")
def add_package(
    package_name: str,
    destination: str,
    weight: float,
    arrival_date: date,
    token: str = Header(None)):
    username = function.verify_token(token=token,token_type="access")
    

    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    package = function.add_package(
        package_name,
        destination,
        weight,
        arrival_date )

    return package

# Endpoint 2: GET /packages/{package_id}
# Purpose: Get package details using package ID

@app.get("/packages/{package_id}")
def get_package(package_id: int,token: str = Header(None)):
    username = function.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    package = function.get_package_by_id(package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

# Endpoint 3: PATCH /packages/{package_id}
# Purpose: Update package details

@app.patch("/packages/{package_id}")
def update_package(
    package_id: int,
    package_name: str = None,
    destination: str = None,
    weight: float = None,
    arrival_date: date = None,
    status: str = None,
    token: str = Header(None)
):
    username = function.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if arrival_date is not None:
        arrival_date = str(arrival_date)
    package = function.update_package(
        package_id,
        package_name,
        destination,
        weight,
        arrival_date,
        status)
    
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")

    if package == "invalid_status":
     raise HTTPException( status_code=400,detail="Invalid package status")
    return package

# Endpoint 4: DELETE /packages/{package_id}
# Purpose: Delete a package if it is not dispatched

@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token: str = Header(None)):
    username = function.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

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
    token = Header(None)):
    username = function.verify_token(token = token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if arrival_date is not None:
        arrival_date = str(arrival_date)

    return function.get_all_packages(destination=destination, status=status, arrival_date=arrival_date)
    # packages = function.get_all_packages(
    #     destination,
    #     status,
    #     arrival_date
    # )
    return packages

# Endpoint 6: GET /dispatch-batches
# Purpose: Get all dispatch batches with optional filters

@app.get("/dispatch-batches")
def get_all_dispatch_batches(
    destination: str = None,
    vehicle_number: str = None,
    status: str = None,
    token: str = Header(None)):
    username = function.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
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
    username = function.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    analytics = function.get_analytics()
    return analytics

# Endpoint 8: POST /dispatch-batches
# Purpose: Create a dispatch batch and assign packages

@app.post("/dispatch-batches")
def add_dispatch_batch(
    batch_name: str,
    destination: str,
    vehicle_number: str,
    dispatch_date: str,
    package_ids: str,
    token: str = Header(None)):
    username = function.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = function.add_dispatch_batch(
        batch_name,
        destination,
        vehicle_number,
        dispatch_date,
        package_ids
    )
    if result == "package_not_found":
        raise HTTPException(status_code=404,detail="Package not found or invalid package ID")
    if result == "destination_mismatch":
        raise HTTPException(status_code=400,detail="Package destination does not match batch destination" )
    if result == "package_not_pending":
        raise HTTPException(status_code=409,detail="Package is already assigned or dispatched")
    if result == "duplicate_package":
        raise HTTPException( status_code=400, detail="Duplicate package IDs are not allowed")
    return result


@app.post("/login")
def login(username:str, password:str):
    token = function.verify_login(username=username, password=password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return token

@app.post("/refresh")
def refresh(refresh_token = Header(None)):
    username = function.verify_token(token= refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")
    access_token= function.create_token(username=username, token_type="access")
    return {"access_token": access_token}


