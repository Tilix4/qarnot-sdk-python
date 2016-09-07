"""Notification"""

# Copyright 2016 Qarnot computing
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from qarnot import get_url, raise_on_error


class Notification(object):
    """A Qarnot Notification

    .. note::
       A :class:`Notification` must be created with
       :meth:`qarnot.connection.Connection.create_task_state_changed_notification`,
       :meth:`qarnot.connection.Connection.create_task_created_notification`,
       :meth:`qarnot.connection.Connection.create_task_ended_notification`
       or retrieved with :meth:`qarnot.connection.Connection.retrieve_notification`.

    """
    def __init__(self, json_notification, connection):
        """Initialize a notification from a dictionary

        :param dict json_notification: Dictionary representing the
                notification, must contain following keys:

                  * uuid: string, the notification's uuid
                  * mask: TaskStateChanged
                  * filter.destination: string, destination (email)
                  * filter.filterKey
                  * filter.filterValue

                optional
                  * filter.template Mail template for the notification
                  * filter.to To state regex (default to .*)
                  * filter.from From state regex (default to .*)
                  * filter.state From or To state regex (default to .*)


        """
        self._connection = connection

        self._uuid = json_notification['uuid']
        self._mask = json_notification['mask']

        destination = json_notification['filter']['destination']
        template = json_notification['filter']['template'] if 'template' in json_notification['filter'] else None

        filterkey = json_notification['filter']['filterKey']
        filtervalue = json_notification['filter']['filterValue']

        if self._mask == "TaskStateChanged":
            _from = json_notification['filter']['from']
            state = json_notification['filter']['state']
            to = json_notification['filter']['to']
            self._filter = TaskStateChanged(template, destination, filterkey, filtervalue, to, _from, state)
        elif self._mask == "TaskCreated":
            self._filter = TaskCreated(template, destination, filterkey, filtervalue)
        elif self._mask == "TaskEnded":
            self._filter = TaskEnded(template, destination, filterkey, filtervalue)

    @classmethod
    def _create(cls, connection, _filter):
        """Create a new Notification
        """
        data = {
            "mask": type(_filter).__name__,
            "filter": _filter.json()
            }
        url = get_url('notification')
        response = connection._post(url, json=data)
        raise_on_error(response)
        rid = response.json()['uuid']
        response = connection._get(get_url('notification update', uuid=rid))
        raise_on_error(response)
        return Notification(response.json(), connection)

    def delete(self):
        """Delete the notification represented by this :class:`Notification`.

        :raises qarnot.QarnotException: API general error, see message for details
        :raises qarnot.connection.UnauthorizedException: invalid credentials
        """

        response = self._connection._delete(
            get_url('notification update', uuid=self._uuid))
        raise_on_error(response)

    @property
    def uuid(self):
        """Uuid Getter
        """
        return self._uuid

    @property
    def filter(self):
        """Filter getter
        """
        return self._filter

    @filter.setter
    def filter(self, value):
        """Filter setter
        """
        self._filter = value


class Filter(object):
    """Filter class
    """
    def __init__(self, template, destination):
        self._template = template
        self._destination = destination

    def json(self):
        """Json representation of the class
        """
        json = {}
        json["destination"] = self._destination
        if self._template is not None:
            json["template"] = self._template
        return json

    @property
    def destination(self):
        """Destination getter
        """
        return self._destination

    @destination.setter
    def destination(self, value):
        """Destination setter
        """
        self._destination = value

    @property
    def template(self):
        """Template getter
        """
        return self._template

    @template.setter
    def template(self, value):
        """Template setter
        """
        self._template = value


class TaskNotification(Filter):
    """TaskNotification class
    """
    def __init__(self, template, destination, filterkey, filtervalue):
        Filter.__init__(self, template, destination)
        self._filterkey = filterkey
        self._filtervalue = filtervalue

    def json(self):
        json = Filter.json(self)
        json["filterKey"] = self._filterkey
        json["filterValue"] = self._filtervalue
        return json

    @property
    def filterkey(self):
        """Filterkey getter
        """
        return self._filterkey

    @filterkey.setter
    def filterkey(self, value):
        """Filterkey setter
        """
        self._filterkey = value

    @property
    def filtervalue(self):
        """Filtervalue getter
        """
        return self._filtervalue

    @filtervalue.setter
    def filtervalue(self, value):
        """Filtervalue setter
        """
        self._filtervalue = value


class TaskStateChanged(TaskNotification):
    """TaskStateChanged class
    """
    def __init__(self, template, destination, filterkey, filtervalue, to, _from, state):
        TaskNotification.__init__(self, template, destination, filterkey, filtervalue)
        self._to = to
        self._from = _from
        self._state = state

    def json(self):
        json = TaskNotification.json(self)
        if self._to is not None:
            json["to"] = self._to
        if self._from is not None:
            json["from"] = self._from
        if self._state is not None:
            json["state"] = self._state
        return json

    @property
    def toregex(self):
        """To getter
        """
        return self._to

    @toregex.setter
    def toregex(self, value):
        """To setter
        """
        self._to = value

    @property
    def fromregex(self):
        """To getter
        """
        return self._from

    @fromregex.setter
    def fromregex(self, value):
        """To setter
        """
        self._from = value

    @property
    def stateregex(self):
        """To getter
        """
        return self._state

    @stateregex.setter
    def stateregex(self, value):
        """To setter
        """
        self._state = value


class TaskCreated(TaskNotification):
    """TaskCreated class
    """
    def __init__(self, template, destination, filterkey, filtervalue):
        TaskNotification.__init__(self, template, destination, filterkey, filtervalue)

    def json(self):
        json = TaskNotification.json(self)
        return json


class TaskEnded(TaskNotification):
    """TaskEnded class
    """
    def __init__(self, template, destination, filterkey, filtervalue):
        TaskNotification.__init__(self, template, destination, filterkey, filtervalue)

    def json(self):
        json = TaskNotification.json(self)
        return json
