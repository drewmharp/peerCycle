create view totalrevenue as select sum(totalcost + tip) as totalrevenue from trips;

create view zipcoderevenue as select zipcode,sum(totalcost + tip) as revenue from trips natural join bike group by zipcode;

create view bikesbyzip as select zipcode,count(bikeid) as numofbikes from bike group by zipcode;

create view bikeuses as select count(tripid) from trips group by bikeid;

create view revenuebyowner as select ownerid,sum(totalcost + tip) from trips group by ownerid;

