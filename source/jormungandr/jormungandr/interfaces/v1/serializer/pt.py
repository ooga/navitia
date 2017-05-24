#  Copyright (c) 2001-2016, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

from __future__ import absolute_import, print_function, unicode_literals, division
import serpy
from jormungandr.interfaces.v1.serializer.base import GenericSerializer, EnumListField, LiteralField
from jormungandr.interfaces.v1.serializer.time import LocalTimeField, PeriodSerializer, DateTimeField
from jormungandr.interfaces.v1.serializer.fields import *
from jormungandr.interfaces.v1.serializer import jsonschema


class Equipments(EnumListField):
    """
    hack for equiments their is a useless level in the proto
    """
    def as_getter(self, serializer_field_name, serializer_cls):
        #For enum we need the full object :(
        return lambda x: x.has_equipments


class ChannelSerializer(PbNestedSerializer):
    content_type = jsonschema.Field()
    id = jsonschema.Field()
    name = jsonschema.Field()
    types = EnumListField(attr='channel_types')


class MessageSerializer(PbNestedSerializer):
    text = jsonschema.Field()
    channel = ChannelSerializer()


class SeveritySerializer(PbNestedSerializer):
    name = jsonschema.Field()
    effect = jsonschema.Field()
    color = jsonschema.Field()
    priority = jsonschema.Field()


class PtObjectSerializer(GenericSerializer):
    quality = jsonschema.Field(schema_type=int, required=False, display_none=True)
    stop_area = jsonschema.MethodField(schema_type=lambda: StopAreaSerializer)
    line = jsonschema.MethodField(schema_type=lambda: LineSerializer)
    network = jsonschema.MethodField(schema_type=lambda: NetworkSerializer)
    route = jsonschema.MethodField(schema_type=lambda: RouteSerializer)
    commercial_mode = jsonschema.MethodField(schema_type=lambda: CommercialModeSerializer)
    trip = jsonschema.MethodField(schema_type=lambda: TripSerializer)
    embedded_type = EnumField(attr='embedded_type')

    def get_trip(self, obj):
        if obj.HasField(str('trip')):
            return TripSerializer(obj.trip, display_none=False).data
        else:
            return None

    def get_commercial_mode(self, obj):
        if obj.HasField(str('commercial_mode')):
            return CommercialModeSerializer(obj.commercial_mode, display_none=False).data
        else:
            return None

    def get_route(self, obj):
        if obj.HasField(str('route')):
            return RouteSerializer(obj.route, display_none=False).data
        else:
            return None

    def get_network(self, obj):
        if obj.HasField(str('network')):
            return NetworkSerializer(obj.network, display_none=False).data
        else:
            return None

    def get_line(self, obj):
        if obj.HasField(str('line')):
            return LineSerializer(obj.line, display_none=False).data
        else:
            return None

    def get_stop_area(self, obj):
        if obj.HasField(str('stop_area')):
            return StopAreaSerializer(obj.stop_area, display_none=False).data
        else:
            return None


class TripSerializer(GenericSerializer):
    pass


class ValidityPatternSerializer(PbNestedSerializer):
    beginning_date = serpy.Field()
    days = serpy.Field()


class WeekPatternSerializer(PbNestedSerializer):
    monday = serpy.BoolField()
    tuesday = serpy.BoolField()
    wednesday = serpy.BoolField()
    thursday = serpy.BoolField()
    friday = serpy.BoolField()
    saturday = serpy.BoolField()
    sunday = serpy.BoolField()


class CalendarPeriodSerializer(PbNestedSerializer):
    begin = serpy.Field()
    end = serpy.Field()


class CalendarExceptionSerializer(PbNestedSerializer):
    datetime = serpy.Field(attr='date')
    type = EnumField()


class CalendarSerializer(GenericSerializer):
    week_pattern = WeekPatternSerializer()
    validity_pattern = ValidityPatternSerializer(display_none=False)
    exceptions = CalendarExceptionSerializer(many=True)
    active_periods = CalendarPeriodSerializer(many=True)


class ImpactedStopSerializer(PbNestedSerializer):
    stop_point = jsonschema.MethodField(schema_type='get_stop_point_jsonschema', display_none=False)
    base_arrival_time = LocalTimeField(attr='base_stop_time.arrival_time')
    base_departure_time = LocalTimeField(attr='base_stop_time.departure_time')
    amended_arrival_time = LocalTimeField(attr='amended_stop_time.arrival_time')
    amended_departure_time = LocalTimeField(attr='amended_stop_time.departure_time')
    cause = jsonschema.Field(schema_type=str, display_none=True)
    stop_time_effect = EnumField(attr='effect')
    departure_status = EnumField()
    arrival_status = EnumField()

    def get_stop_point_jsonschema(self):
        return StopPointSerializer(display_none=False)

    def get_stop_point(self, obj):
        if obj.HasField(str('stop_point')):
            return StopPointSerializer(obj.stop_point, display_none=False).data
        else:
            return None


class ImpactedSectionSerializer(PbNestedSerializer):
    f = PtObjectSerializer(label='from', attr='from')
    to = PtObjectSerializer()


class ImpactedSerializer(PbNestedSerializer):
    pt_object = PtObjectSerializer(display_none=False)
    impacted_stops = ImpactedStopSerializer(many=True, display_none=False)
    impacted_section = ImpactedSectionSerializer(display_none=False)


class DisruptionSerializer(PbNestedSerializer):
    # @schema(type=str)
    id = jsonschema.Field(schema_type=str, attr='uri')

    disruption_id = jsonschema.Field(schema_type=str, attr='disruption_uri')
    impact_id = jsonschema.Field(schema_type=str, attr='uri')
    title = jsonschema.Field(schema_type=str),
    application_periods = PeriodSerializer(many=True)
    status = EnumField(attr='status')
    updated_at = DateTimeField()
    tags = serpy.Serializer(many=True, display_none=False)
    cause = jsonschema.Field(schema_type=str, display_none=True)
    category = jsonschema.Field(schema_type=str, display_none=False)
    severity = SeveritySerializer()
    messages = MessageSerializer(many=True)
    impacted_objects = ImpactedSerializer(many=True, display_none=False)
    uri = jsonschema.Field(schema_type=str, attr='uri')
    disruption_uri = jsonschema.Field(schema_type=str)
    contributor = jsonschema.Field(schema_type=str)


class PoiTypeSerializer(GenericSerializer):
    pass


class StandsSerializer(PbNestedSerializer):
    available_places = jsonschema.IntField()
    available_bikes = jsonschema.IntField()
    total_stands = jsonschema.IntField()


class AdminSerializer(GenericSerializer):
    level = jsonschema.Field(schema_type=int)
    zip_code = jsonschema.Field(schema_type=str, display_none=True)
    label = jsonschema.Field(schema_type=str)
    insee = jsonschema.Field(schema_type=str)
    coord = CoordSerializer(required=False)


class AddressSerializer(GenericSerializer):
    house_number = jsonschema.Field(schema_type=int, display_none=True)
    coord = CoordSerializer(required=False)
    label = jsonschema.Field(schema_type=str)
    administrative_regions = AdminSerializer(many=True, display_none=False)


class PoiSerializer(GenericSerializer):
    coord = CoordSerializer(required=False)
    label = jsonschema.Field(schema_type=str)
    administrative_regions = AdminSerializer(many=True, display_none=False)
    poi_type = PoiTypeSerializer(display_none=False)
    properties = jsonschema.MethodField(schema_type='object')
    address = AddressSerializer()
    stands = LiteralField(None, schema_type=StandsSerializer, display_none=False)

    def get_properties(self, obj):
        res = {}
        for code in obj.properties:
            res[code.type] = code.value
        return res


class PhysicalModeSerializer(GenericSerializer):
    pass


class CommercialModeSerializer(GenericSerializer):
    pass


class StopPointSerializer(GenericSerializer):
    comments = CommentSerializer(many=True, display_none=False)
    comment = FirstCommentField(attr='comments', display_none=False)
    codes = CodeSerializer(many=True, display_none=False)
    label = jsonschema.Field(schema_type=str)
    coord = CoordSerializer(required=False)
    links = LinkSerializer(attr='impact_uris', display_none=True)
    commercial_modes = CommercialModeSerializer(many=True, display_none=False)
    physical_modes = PhysicalModeSerializer(many=True, display_none=False)
    administrative_regions = AdminSerializer(many=True, display_none=False)
    stop_area = jsonschema.MethodField(schema_type='get_stop_area_jsonschema', display_none=False)
    equipments = Equipments(attr='has_equipments')
    address = AddressSerializer(display_none=False)

    def get_stop_area_jsonschema(self):
        return StopAreaSerializer(display_none=False)

    def get_stop_area(self, obj):
        if obj.HasField(str('stop_area')):
            return StopAreaSerializer(obj.stop_area, display_none=False).data
        else:
            return None


class StopAreaSerializer(GenericSerializer):
    comments = CommentSerializer(many=True, display_none=False)
    comment = FirstCommentField(attr='comments', display_none=False)
    codes = CodeSerializer(many=True)
    timezone = jsonschema.Field(schema_type=str)
    label = jsonschema.Field(schema_type=str)
    coord = CoordSerializer(required=False)
    links = LinkSerializer(attr='impact_uris', display_none=True)
    commercial_modes = CommercialModeSerializer(many=True, display_none=False)
    physical_modes = PhysicalModeSerializer(many=True, display_none=False)
    administrative_regions = AdminSerializer(many=True, display_none=False)
    stop_points = StopPointSerializer(many=True, display_none=False)


class PlaceSerializer(GenericSerializer):
    quality = jsonschema.Field(schema_type=int, required=False)
    stop_area = StopAreaSerializer(display_none=False)
    stop_point = StopPointSerializer(display_none=False)
    administrative_region = AdminSerializer(display_none=False)
    embedded_type = EnumField(attr='embedded_type')
    address = AddressSerializer(display_none=False)
    poi = PoiSerializer(display_none=False)


class NetworkSerializer(GenericSerializer):
    lines = jsonschema.MethodField(schema_type='get_lines_jsonschema', display_none=False)
    links = LinkSerializer(attr='impact_uris', display_none=True)
    codes = CodeSerializer(many=True, display_none=False)

    def get_lines_jsonschema(self):
        return LineSerializer(many=True, display_none=False)

    def get_lines(self, obj):
        return LineSerializer(obj.lines, many=True, display_none=False).data


class RouteSerializer(GenericSerializer):
    is_frequence = serpy.StrField()
    direction_type = jsonschema.Field(schema_type=str)
    physical_modes = PhysicalModeSerializer(many=True, display_none=False)
    comments = CommentSerializer(many=True, display_none=False)
    codes = CodeSerializer(many=True, display_none=False)
    direction = PlaceSerializer()
    geojson = MultiLineStringField(display_none=False)
    links = LinkSerializer(attr='impact_uris', display_none=True)
    line = jsonschema.MethodField(schema_type='get_line_jsonschema')
    stop_points = StopPointSerializer(many=True, display_none=False)

    def get_line_jsonschema(self):
        return LineSerializer(display_none=False)

    def get_line(self, obj):
        if obj.HasField(str('line')):
            return LineSerializer(obj.line, display_none=False).data
        else:
            return None


class LineGroupSerializer(GenericSerializer):
    lines = jsonschema.MethodField(schema_type='get_lines_jsonschema', display_none=False)
    main_line = jsonschema.MethodField(schema_type='get_main_line_jsonschema', display_none=False)
    comments = CommentSerializer(many=True)

    def get_lines_jsonschema(self):
        return LineSerializer(many=True, display_none=False)

    def get_lines(self, obj):
        return LineSerializer(obj.lines, many=True, display_none=False).data

    def get_main_line_jsonschema(self):
        return LineSerializer()

    def get_main_line(self, obj):
        if obj.HasField(str('main_line')):
            return LineSerializer(obj.main_line).data
        else:
            return None


class LineSerializer(GenericSerializer):
    code = jsonschema.Field(schema_type=str)
    color = jsonschema.Field(schema_type=str)
    text_color = jsonschema.Field(schema_type=str)
    comments = CommentSerializer(many=True, display_none=False)
    comment = FirstCommentField(attr='comments', display_none=False)
    codes = CodeSerializer(many=True, required=False)
    physical_modes = PhysicalModeSerializer(many=True)
    commercial_mode = CommercialModeSerializer(display_none=False)
    routes = RouteSerializer(many=True, display_none=False)
    network = NetworkSerializer(display_none=False)
    opening_time = LocalTimeField()
    closing_time = LocalTimeField()
    properties = PropertySerializer(many=True, display_none=False)
    geojson = MultiLineStringField(display_none=False)
    links = LinkSerializer(attr='impact_uris', display_none=True)
    line_groups = LineGroupSerializer(many=True, display_none=False)


class JourneyPatternPointSerializer(PbNestedSerializer):
    id = serpy.Field(attr='uri')
    stop_point = StopPointSerializer(display_none=False)


class JourneyPatternSerializer(GenericSerializer):
    journey_pattern_points = JourneyPatternPointSerializer(many=True)
    route = RouteSerializer(display_none=False)


class StopTimeSerializer(PbNestedSerializer):
    arrival_time = LocalTimeField()
    departure_time = LocalTimeField()
    headsign = serpy.Field()
    journey_pattern_point = JourneyPatternPointSerializer()
    stop_point = StopPointSerializer()


class VehicleJourneySerializer(GenericSerializer):
    journey_pattern = JourneyPatternSerializer(display_none=False)
    stop_times = StopTimeSerializer(many=True)
    comments = CommentSerializer(many=True, display_none=False)
    comment = FirstCommentField(attr='comments', display_none=False)
    codes = CodeSerializer(many=True)
    validity_pattern = ValidityPatternSerializer()
    calendars = CalendarSerializer(many=True)
    trip = TripSerializer()
    disruptions = LinkSerializer(attr='impact_uris', display_none=True)
