import csv
from datetime import datetime
from abc import ABC,abstractmethod
row_data=[]
with open("courses.csv","r") as file:
    reader=csv.DictReader(file)
    columns=reader.fieldnames
    for row in reader:
        row_data.append(row)
valid_rows=[]
valid_ids=set()

#  Course ID must be unique.
# • Course name must not be empty.
# • Course type must be either Classroom or Online.
# • Base fee must be numeric and greater than zero.
# • Offer discount must be numeric and between 0 and 100, inclusive.
# • Offer end date must be a valid date in YYYY-MM-DD format when provided.
# • Reject records that violate any validation rule.
# • Continue processing the remaining records when an individual record is invalid
for row in row_data:
    try:
        if row["CourseID"] in valid_ids:
            raise ValueError(row["CourseID"],"found Duplicate")
        if not row["CourseName"].strip().lower() or (row["CourseName"].strip().lower() in ["na", "none", "null"]):
            raise ValueError(row["CourseID"],"Course Name is Invalid")
        if row["CourseType"] not in ["Classroom","Online"]:
            raise ValueError(row["CourseID"],"Course not Found")
        # basefee=int(row["BaseFee"])
        if not row["BaseFee"].isdigit() or (int(row["BaseFee"])<0):
            raise ValueError(row["CourseID"],"BaseFee is in invalid format")
        if not (row["OfferDiscount"]).isdigit() or (int(row["OfferDiscount"])<0 or int(row["OfferDiscount"])>100):
            raise ValueError(row["CourseID"],"OfferDiscount is invalid")
        date_value = row["OfferEndDate"].strip()
        if date_value:
            try:
                 datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(row["CourseID"], "Date is invalid")

        valid_ids.add(row["CourseID"])
        valid_rows.append(row)
    except ValueError as e:
        print(e)
        continue

#  Create a base class named Course with course ID, course name and base fee.
# • Create two subclasses: ClassroomCourse and OnlineCourse.
# • Implement a common fee-calculation method in the base class and override it in each subclass.
# • Use polymorphism to calculate fees for different course types
class Course(ABC):
    def __init__(self,course_id,course_name,base_fee):
        self.course_id=course_id
        self.course_name=course_name
        self.base_fee=base_fee
    @abstractmethod
    def fee_calculation(self):
        pass
class ClassroomCourse(Course):
    def __init__(self,course_id,course_name,base_fee,course_type,offer_discount,date):
        super().__init__(course_id,course_name,base_fee)
        self.course_type=course_type
        self.offer_discount=offer_discount
        self.date=date  
        self.parameters={}
    def fee_calculation(self):
           offer_applicable = (self.date is not None and datetime.today().date() <= self.date.date())
           facility_fee = 200
           total_fee = self.base_fee + facility_fee
           if offer_applicable:
               offer = (self.offer_discount / 100) * total_fee
               total_fee -= offer
               self.parameters["OfferStatus"]="With Offer"
               self.parameters["OfferDiscountAmount"]=offer
           else:
               offer = 0
               self.parameters["OfferStatus"]="Without Offer"
               self.parameters["OfferDiscountAmount"]=offer
            
           self.parameters["CourseID"]=self.course_id
           self.parameters["CourseName"]=self.course_name
           self.parameters["CourseType"]=self.course_type
           self.parameters["BaseFee"]=self.base_fee
           self.parameters["CourseAdjustmentFee"]="Facility-fee of 200"
           self.parameters["OfferDiscountPercent"]=self.offer_discount
           self.parameters["OfferEndDate"]=self.date
           self.parameters["FinalFee"]=total_fee
           
           return self.parameters
   
    
class OnlineCourse(Course):

    def __init__(self,course_id,course_name,base_fee,course_type,offer_discount,date):
        super().__init__(course_id,course_name,base_fee)
        self.course_type=course_type
        self.offer_discount=offer_discount
        self.date=date
        self.parameters={}
    def fee_calculation(self):
        offer_applicable = (self.date is not None and datetime.today().date() <= self.date.date())

        # 10% course-type discount
        Discount = (10 / 100) * self.base_fee
        total_fee = self.base_fee - Discount

        if offer_applicable:
            offer = (self.offer_discount / 100) * total_fee
            total_fee -= offer
            self.parameters["OfferStatus"]="With Offer"
            self.parameters["OfferDiscountAmount"]=offer
        else:
            offer = 0
            self.parameters["OfferStatus"]="Without Offer"
            self.parameters["OfferDiscountAmount"]=offer

        self.parameters["CourseID"]=self.course_id
        self.parameters["CourseName"]=self.course_name
        self.parameters["CourseType"]=self.course_type
        self.parameters["BaseFee"]=self.base_fee
        self.parameters["CourseAdjustmentFee"]="Discount of 10%"
        self.parameters["OfferDiscountPercent"]=self.offer_discount
        self.parameters["OfferEndDate"]=self.date
        self.parameters["FinalFee"]=total_fee
        return self.parameters
  

dict_id = {}

for row in valid_rows:
    course_id = row["CourseID"]
    course_name = row["CourseName"]
    base_fee = float(row["BaseFee"])
    course_type = row["CourseType"]
    offer_discount = float(row["OfferDiscount"])
    offer_Enddate = row["OfferEndDate"].strip()
    date = datetime.strptime(offer_Enddate, "%Y-%m-%d") if offer_Enddate else None
    if course_type == "Classroom":
        obj = ClassroomCourse(course_id, course_name, base_fee, course_type, offer_discount, date)
    else:
        obj = OnlineCourse(course_id, course_name, base_fee, course_type, offer_discount, date)

    res = obj.fee_calculation()
    dict_id[course_id] = res


report_columns = [
    "CourseID",
    "CourseName",
    "CourseType",
    "BaseFee",
    "CourseAdjustmentFee",
    "OfferDiscountPercent",
    "OfferEndDate",
    "OfferStatus",
    "OfferDiscountAmount",
    "FinalFee"
]

with open("course_fee_report.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=report_columns)

    writer.writeheader()
    writer.writerows(dict_id.values())

print("course_fee_report.csv created successfully.")
