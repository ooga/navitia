from werkzeug.wrappers import Response
from uri import Uri, InvalidUriException, collections_to_resource_type, types_not_ptrefable
from apis import validate_and_fill_arguments, InvalidArguments, validate_pb_request
from instance_manager import NavitiaManager
from error import generate_error
import datetime
import output_v1
import logging
def coverage(request):
    return output_v1.coverage(request, format=request.accept_mimetypes)

def coord(request, lon, lat):
    return output_v1.coord(request, lon, lat)

def departures_arrivals(type, request, uri1):
    u = None
    try:
        u = Uri(uri1)
    except InvalidUriException:
        return generate_error("Invalid uri")
    
    if u.is_region:
        if len(u.objects) == 0:
            return generate_error(type+" are only available from a stop area or a stop point", 501)

        resource_type, uid = u.objects.pop()
        if resource_type not in ['stop_points', 'stop_areas']: 
            return generate_error(type+" are only available from a stop area or a stop point", 501)
        filter_ = collections_to_resource_type[resource_type]+".uri="+uid
    else:
        filter_ = "stop_point.coord DWITHIN("+str(u.lon)+","+str(u.lat)+", 200)"

    req = {            
            'filter': [filter_], 
            'from_datetime': [datetime.datetime.now().strftime("%Y%m%dT1337")]
          }
    arguments = validate_and_fill_arguments("next_"+type, req)
    return NavitiaManager().dispatch(arguments, u.region(), "next_"+type), u.region()

def departures(request, uri1):
    response, region = departures_arrivals("departures", request, uri1)
    return output_v1.departures(response,  region, request.accept_mimetypes, request.args.get("callback"))

def arrivals(request, uri1):
    response, region = departures_arrivals("arrivals", request, uri1)
    return output_v1.arrivals(response,  region, request.accept_mimetypes, request.args.get("callback"))


def uri(request, uri):
    u = None
    try:
        u = Uri(uri)
    except InvalidUriException, e:
        return generate_error("Invalid uri")

    if len(u.objects) == 0:
        if u.is_region:
            return output_v1.coverage(request, u.region(), request.accept_mimetypes)

    resource_type, uid = u.objects.pop()
    if resource_type in types_not_ptrefable:
        return generate_error("Type : " + resource_type + " not consultable yet", 501)
    req = {}
    if 'start_page' in request.args:
        req['startPage'] = [int(request.args.get('start_page'))]

    filters = []
    if uid:
        filters.append(collections_to_resource_type[resource_type]+".uri="+uid)
    else:
        for resource_type2, uid2 in u.objects:
            filters.append(collections_to_resource_type[resource_type2]+".uri="+uid2)

    if 'filter' in request.args:
        filters.append(request.args.get('filter'))

    if len(filters)>0:
        req["filter"] = [" and ".join(filters)]
    arguments = None
    try:
        arguments = validate_and_fill_arguments(resource_type, req)
        response = NavitiaManager().dispatch(arguments, u.region(), resource_type)
    except InvalidArguments, e:
        return generate_error(e.message)
    return output_v1.render_ptref(response, u.region(), resource_type, uid, request.accept_mimetypes, request.args.get("callback"))

def places(request, uri):
    u = None
    try:
        u = Uri(uri)
    except InvalidUriException, e:
        return generate_error("Invalid uri", e.message)

    if len(u.objects) > 0:
        return generate_error("You cannot search places within this object, not implemented", status=501)

    arguments = validate_pb_request("places", request)
    if arguments.valid:
        response = NavitiaManager().dispatch(arguments, u.region(), "places")
        return output_v1.places(response, u, request.accept_mimetypes, request.args.get("callback"))
    else:
        return generate_error("Invalid arguments : " + arguments.details)


def route_schedules(request, uri1=None):
    u = None
    req = {"filter" : [], "from_datetime": []}
    region = ""
    if(uri1):
	    try:
		u = Uri(uri1)
	    except InvalidUriException, e:
		return generate_error("Invalid uri", e.message)

	    resource_type, uid = u.objects[-1]
	    region = u.region()	
	    if not uid:
		return generate_error("You cannot ask a route schedule with this object, not implemented", status=501)
	    req["filter"] =[collections_to_resource_type[resource_type]+".uri="+uid]
    elif(request.args.get("filter")):
	filter_ = request.args.get("filter", str)
	if filter_.count("=") == 0 :
		return generate_error("Invalid filter")
	region = filter_.split("=")[1].split("/")[0]
	filters = []
	for f in filter_.split("="):
	    filters.append(f.replace(f, f.split("/")[-1]))
	tmp = "=".join(filters)
	req["filter"] = [tmp]
    else:
    	return generate_error("Invalid request")
    if not request.args.get("from_datetime"):
        req["from_datetime"] = [datetime.datetime.now().strftime("%Y%m%dT1337")]
    else:
        req["from_datetime"] = [request.args.get("from_datetime", str)]

    if request.args.get("duration"):
        req["duration"] = [int(request.args.get("duration"))]
    if request.args.get("depth"):
        req["depth"] = [int(request.args.get("depth"))]

    arguments = validate_and_fill_arguments("route_schedules", req)
    if arguments.valid:
        response = NavitiaManager().dispatch(arguments, region, "route_schedules")
        return output_v1.route_schedules(response, u, region, request.accept_mimetypes, request.args.get("callback"))
    else:
        return generate_error("Invalid arguments : " + arguments.details)

def stop_schedules(request, uri1, uri2=None):
    return_ = '{"apiname":"schedules", uri1:"'+uri1+'"'
    if uri2:
        return_ += ', uri2:"'+uri2+'"'
    return Response(return_ +'}', mimetype='text/plain;charset=utf-8')

def journeys(request, uri1=None):
    acceptable_types = ["stop_areas", "stop_points", "addresses", "coords", "poi"]
    u1 = None
    from_=""
    if uri1:
        from_ = uri1
    else:
        from_ =request.args.get("from", str)
    try:
        u1 = Uri(from_)
    except InvalidUriException, e:
        return generate_error("Invalid id" + e.message)
    resource_type1, uid1 = "", ""
    if u1.is_region:
        resource_type1, uid1 = u1.objects[-1]
    else:
        resource_type1 = "coord"
        uid1 = "coord:"+str(u1.lon)+":"+str(u1.lat)

    if not uid1 or not resource_type1 in acceptable_types:
        return generate_error("Unsupported id: " + uri1 + ", not implemented", status=501)
    req = {}
    req["origin"] = [uid1]
    if not request.args.get("datetime"):
        req["datetime"] = [datetime.datetime.now().strftime("%Y%m%dT1337")]
    else:
        req["datetime"] = [request.args.get("datetime", str)]
    
    if request.args.get("to"):
        try:
            u2 = Uri(request.args.get("to"))
        except InvalidUriException, e:
            return generate_error("Invalid uri" + e.message)
        resource_type2, uid2 = u2.objects.pop()
        if not uid2 or not resource_type2 in acceptable_types:
            return generate_error("Unsupported uri : " + request.args.get("to") + ", not implemented", status=501)
        if u1.region() != u2.region():
            return generate_error("The origin and destination are not in the same region, not implemented", status=501)
        req["destination"] = [uid2]
        try:
            arguments = validate_and_fill_arguments("journeys", req)
        except InvalidArguments, e:
            return generate_error("Invalid Arguments : " + str(e.message))
        if arguments.valid:
            response = NavitiaManager().dispatch(arguments, u1.region(), "journeys")
            return output_v1.journeys(request.path, u1, response, request.accept_mimetypes, request.args.get("callback"))
        else:
            return generate_error("Invalid arguments : " + arguments.details)
    else:
        try:
            arguments = validate_and_fill_arguments("isochrone", req)
        except InvalidArguments, e:
            return generate_error("Invalid Arguments : " + str(e.message))
        if arguments.valid:
            response = NavitiaManager().dispatch(arguments, u1.region(), "isochrone")
            return output_v1.journeys(arguments, u1, response, request.accept_mimetypes, request.args.get("callback"), True)
        else:
            return generate_error("Invalid arguments : " + arguments.details)


def nearby(request, uri1, uri2=None):
    u = None
    try:
        u = Uri(uri1)
    except InvalidUriException, e:
        return generate_error("Invalid uri" + e.message)
    resource_type, uid = "", "" 
    if u.is_region:
        resource_type, uid = u.objects.pop()
    else:
        resource_type = "coord"
        uid = "coord:"+str(u.lon)+":"+str(u.lat)
    req = {}
    if uid:
        req["uri"] = [uid]
    else:
        return generate_error("You cannot search places around this object, not implemented", status=501)
    try:
        arguments = validate_and_fill_arguments("places_nearby", req)
    except InvalidArguments, e:
        return generate_error("Invalid Arguments : " + e.message)
    if arguments.valid:
        response = NavitiaManager().dispatch(arguments, u.region(), "places_nearby")
        return output_v1.nearby(response, u, request.accept_mimetypes, request.args.get("callback"))
    else:
        return generate_error("Invalid arguments : " + arguments.details)


def index(request):
    return output_v1.index(request, format=request.accept_mimetypes)
