create table uniqZIPS 
(Zip numeric(5) primary key
);

create table PERSON
    (UserID   	  SERIAL,
     PhoneNumber   numeric(10,0),
     FirstName     varchar(15),
     LastName     varchar(15),
     Password     varchar(125),
     Email   	  varchar(25),
     primary key (userID)
     );
     
     
     create table RENTER
    (UserID   	  integer,
     Rating   	  numeric(1,0),
     CredCardNum numeric (16,0),
     primary key (UserID),
     foreign key (UserID) references PERSON
   	 on delete set null
     );

create table OWNER
    (UserID   	 SERIAL,
     Rating   	  numeric(1,0),
     BankNo   	 numeric(12,0),
     primary key (userID),
     foreign key (userID) references PERSON
   	 on delete set null
   	 );
   	 
   	 create table BIKE
  	( BikeID  SERIAL,
    OwnerID integer,
  	StreetAddress Varchar(50),
  	City Varchar(20),
  	State Varchar (20),
  	ZIPCode numeric(5),
  	dlyRate Decimal (5,2) check(dlyRate >= 0),
  	hlyRate Decimal (5,2) check(dlyRate >= 0),
  	Model  Varchar (100),
  	Make   Varchar (100),
  	BikeType Varchar (100),
  	ModelYear Date,
  	LockCode  numeric (8) check (lockcode > 0),
  	Description text,
  	primary key (BikeID),
  	foreign key (OwnerID) references Owner(UserID) on delete set null,
	foreign key (ZIPCode) references uniqZips(zip) on delete set null
  	);
  	
   	 create table TRIPS
  (tripID SERIAL primary key,
  isHrly boolean,
  NumOfHrsDays numeric(3,1) check (NumOfHrsDays>0),
  StartTime timestamp,
  RiderExperience numeric(2,1) check(0<= RiderExperience AND RiderExperience <=5),
  OwnerExperience numeric(2,1) check(0<= OwnerExperience AND OwnerExperience <=5),
  Tip numeric(5,2) check (Tip >= 0),
  Tax numeric(5,2) check (Tip >= 0),
  DerivedCost numeric(5,2) check (DerivedCost >= 0),
  TotalCost numeric(6,2) check (TotalCost >= 0),
  OwnerID integer references BIKE on delete set null,
  RenterID integer references RENTER(UserID) on delete set null,
  BikeId integer references BIKE on delete set null
  );
  
  create table REVIEWS (
	tripid integer,				  /* The ID value of the trip **/
	reviewerid integer,			  /* The ID of the reviewer **/
	review numeric(1,0),			  /* The value of the review recived **/
	comments varChar (200)			  /* The reviewer's comments recived **/
	primary key (tripid),
	foreign key (tripid) references TRIPS(tripID) on delete set null
);
