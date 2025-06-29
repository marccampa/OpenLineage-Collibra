# Copyright 2018-2025 contributors to the OpenLineage project
# SPDX-License-Identifier: Apache-2.0

from typing import Any

import attr
from openlineage.airflow.extractors.base import OperatorLineage
from openlineage.client.event_v2 import Dataset
from openlineage.client.facet_v2 import BaseFacet, parent_run, sql_job

from airflow import DAG
from airflow.models import BaseOperator
from airflow.utils.dates import days_ago

INPUTS = [Dataset(namespace="database://host:port", name="inputtable")]
OUTPUTS = [Dataset(namespace="database://host:port", name="inputtable")]
RUN_FACETS = {
    "parent": parent_run.ParentRunFacet(
        run=parent_run.Run(runId="3bb703d1-09c1-4a42-8da5-35a0b3216072"),
        job=parent_run.Job(namespace="namespace", name="parentjob"),
    )
}
JOB_FACETS = {"sql": sql_job.SQLJobFacet(query="SELECT * FROM inputtable")}


@attr.define
class CompleteRunFacet(BaseFacet):
    finished: bool


class ExampleOperator(BaseOperator):
    def execute(self, context) -> Any:
        pass

    def get_openlineage_facets_on_start(self) -> OperatorLineage:
        return OperatorLineage(
            inputs=INPUTS,
            outputs=OUTPUTS,
            run_facets=RUN_FACETS,
            job_facets=JOB_FACETS,
        )

    def get_openlineage_facets_on_complete(self, task_instance) -> OperatorLineage:
        return OperatorLineage(
            inputs=INPUTS,
            outputs=OUTPUTS,
            run_facets=RUN_FACETS,
            job_facets={"complete": CompleteRunFacet(True)},
        )


default_args = {
    "owner": "datascience",
    "depends_on_past": False,
    "start_date": days_ago(7),
    "email_on_failure": False,
    "email_on_retry": False,
    "email": ["datascience@example.com"],
}

dag = DAG(
    "default_extractor_dag",
    schedule_interval="@once",
    default_args=default_args,
    description="Determines the popular day of week orders are placed.",
)


t1 = ExampleOperator(task_id="default_operator_first", dag=dag)

t2 = ExampleOperator(task_id="default_operator_second", dag=dag)

t1 >> t2
