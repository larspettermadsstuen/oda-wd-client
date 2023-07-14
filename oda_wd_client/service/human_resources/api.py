from datetime import date, timedelta, datetime
from typing import Iterator, Union

from suds import sudsobject, WebFault

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.tools import suds_to_dict
from oda_wd_client.service.human_resources.types import Worker
from oda_wd_client.service.human_resources.utils import workday_worker_to_pydantic


class HumanResources(WorkdayClient):
    service = "Human_Resources"

    def get_workers(self, as_of_date: date | None = None) -> Iterator[sudsobject.Object]:
        """
        Get all workers
        """
        method = "Get_Workers"
        filters = {}
        if as_of_date:
            filters["As_Of_Effective_Date"] = date.today() + timedelta(days=15)

        return self._get_paginated(method, "Worker", filters=filters)

    def _get_worker_by_id(
        self, id_: str, id_type: str, return_object: bool = False
    ) -> Union[Worker, sudsobject.Object]:
        """
        Lookup a given worker by ID
        """
        method = "Get_Workers"
        refs = self.factory("ns0:Worker_Request_ReferencesType")
        ref = self.factory("ns0:WorkerObjectType")
        obj_id = self.factory("ns0:WorkerObjectIDType")
        obj_id.value = id_
        obj_id._type = id_type
        ref.ID.append(obj_id)
        refs.Worker_Reference.append(ref)
        # Catching one class of errors to raise a more sane value error if the ID is invalid
        try:
            response = self._request(method, Request_References=refs)
        except WebFault as e:
            if e.fault.faultcode == "SOAP-ENV:Client.validationError":
                raise ValueError(f'Invalid ID of type "{id_type}"')
            raise
        worker = response.Response_Data.Worker[0]
        if return_object:
            return worker
        return workday_worker_to_pydantic(suds_to_dict(worker))

    def get_worker_by_workday_id(self, id_: str) -> Worker:
        """
        Lookup a single worker based on Workday ID
        """
        return self._get_worker_by_id(id_, "WID")

    def get_worker_by_employee_number(self, id_: str) -> Worker:
        """
        Lookup a single worker based on employee number
        """
        return self._get_worker_by_id(id_, "Employee_ID")

    def change_work_contact_info(self, *args, **kwargs) -> sudsobject.Object:
        """
        Changing contact info for a given user
        """
        method = "Change_Work_Contact_Information"
        return self._request(method, *args, **kwargs)


