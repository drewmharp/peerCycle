
create or replace function Confirm () returns trigger as $$
declare
trip TRIPS%ROWTYPE;
tripend timestamp;
newend timestamp;
inter varchar;
begin

	if new.isHrly then
		inter := CONCAT(new.numofhrsdays, ' hours');
	else 
		inter := CONCAT(new.numofhrsdays, ' days');
	end if;
	
	newend :=  new.StartTime + inter::INTERVAL; 

	for trip in select * from trips t
	where t.bikeid = new.bikeid
	loop
		if trip.isHrly then
			inter := CONCAT(trip.numofhrsdays, ' hours');		
		else
			inter := CONCAT(trip.numofhrsdays, ' days');
		end if;
		
		tripend = trip.starttime + inter::INTERVAL;
		if (new.starttime,newend) overlaps (trip.starttime,tripend) then
			RAISE EXCEPTION 'Trip overlaps with previously scheduled Trip.';
		end if;
	end loop;
	return new;
end;
$$ language 'plpgsql';

create trigger ConfirmTrip before insert or update on Trips
for each row execute procedure Confirm();

