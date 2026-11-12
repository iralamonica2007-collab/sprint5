from fastapi import FastAPI, HTTPException
import function

app = FastAPI()


# Endpoint 1: POST /packages
# Purpose: Register a new package

@app.post("/packages")
def add_package(
    package_name: str,
    destination: str,
    weight: float,
    arrival_date: str
):

    package = function.add_package(
        package_name,
        destination,
        weight,
        arrival_date
    )

    return package

# Endpoint 2: GET /packages/{package_id}
# Purpose: Get package details using package ID

@app.get("/packages/{package_id}")
def get_package(package_id: int):

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
    arrival_date: str = None
):
    package = function.update_package(
        package_id,
        package_name,
        destination,
        weight,
        arrival_date
    )

    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")

    return package

# Endpoint 4: DELETE /packages/{package_id}
# Purpose: Delete a package if it is not dispatched

@app.delete("/packages/{package_id}")
def delete_package(package_id: int):

    result = function.delete_package(package_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Package not found")

    if result == "dispatched":
        raise HTTPException(status_code=409, detail="Dispatched package cannot be deleted")

    return result

