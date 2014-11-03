# Copyright (c) 2001-2014, Canal TP and/or its affiliates. All rights reserved.
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
from jormungandr.interfaces.v1.transform_id import transform_id

class TestTransformId:
    def test_transform_id_coord(self):
        id = "1.23456789012345;2.23456789012345"
        uri = "coord:1.23456789012345:2.23456789012345"
        assert transform_id(id) == uri

    def test_transform_id_almost_coord(self):
        id = "1.23456789012345;2.23456789012345toto"
        uri = id
        assert transform_id(id) == uri

    def test_transform_id_admin(self):
        id = "admin:1:12345"
        uri = "admin:12345"
        assert transform_id(id) == uri

    def test_transform_id_address(self):
        id = "address:1:12345"
        uri = "address:12345"
        assert transform_id(id) == uri

    def test_transform_id_something(self):
        id = "something"
        uri = id
        assert transform_id(id) == uri