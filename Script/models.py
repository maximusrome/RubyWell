from sqlalchemy import Column, Integer, String, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Plan(Base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True)
    bid_id = Column(String)
    segment_number = Column(String)
    contract_id = Column(String)
    eoc_url = Column(String)
    full_plan_id = Column(String)
    plan_market = Column(String)
    plan_name = Column(String)
    source = Column(String)
    company = Column(String)
    states = Column(ARRAY(String))
    zip_code = Column(String)
    plan_zipcodes = relationship('PlanZipcode', back_populates='plan')


class Benefit(Base):
    __tablename__ = 'benefits'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    cost_info = Column(ARRAY(Text))  # Use ARRAY to store multiple cost info strings
    steps_to_use = Column(ARRAY(Text))  # Use ARRAY to store multiple steps
    special_qualifications = Column(Text)
    amount_free = Column(Integer)  # Assuming amountFree is an integer count
    type = Column(String)
    page = Column(Integer)  # Assuming page is a simple integer
    plan_id = Column(Integer, ForeignKey('plans.id'))  # Establishes the relationship to the Plan table

    plan = relationship("Plan", back_populates="benefits")

class Zipcode(Base):
    __tablename__ = 'zipcodes'
    
    zip = Column(String, primary_key=True, nullable=False) 
    type = Column(String, nullable=False)
    primary_city = Column(String, nullable=False)
    acceptable_cities = Column(String, nullable=True)
    unacceptable_cities = Column(String, nullable=True)
    state = Column(String, nullable=False)
    county = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    area_codes = Column(String, nullable=False)
    world_region = Column(String, nullable=True)
    country = Column(String, nullable=False)
    irs_estimated_population = Column(Integer, nullable=False)
    
    plan_zipcodes = relationship('PlanZipcode', back_populates='zipcode')



class PlanZipcode(Base):
    __tablename__ = 'plan_zipcodes'
    
    plan_id = Column(Integer, ForeignKey('plans.id'), primary_key=True)
    zipcode_id = Column(String, ForeignKey('zipcodes.zip'), primary_key=True)  # Reference zipcodes.zip
    
    zipcode = relationship('Zipcode', back_populates='plan_zipcodes')
    plan = relationship('Plan', back_populates='plan_zipcodes')
    
Plan.benefits = relationship("Benefit", order_by=Benefit.id, back_populates="plan")