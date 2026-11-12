from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, Session

# Database connection
DB_PATH = "warehouse.db" 
engine = create_engine(f"sqlite:///{DB_PATH}")

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

