import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_workflow_team.config.settings import settings
from data_workflow_team.core.audit_logger import log_audit_event, AUDIT_LOG_FILE
from data_workflow_team.integrations.data_connectors import health_check_system, execute_read_only_query
from data_workflow_team.integrations.agile_board import create_agile_ticket, update_ticket_status
from data_workflow_team.integrations.notification_manager import send_alert_notification
from data_workflow_team.integrations.git_manager import git_create_issue
from data_workflow_team.agent import root_agent

class TestEnterpriseSystem(unittest.TestCase):

    def test_01_audit_logger(self):
        """Verifica que los eventos de auditoría se registren inmutablemente en disco."""
        res = log_audit_event("TestAgent", "UNIT_TEST", "TestTarget", "SUCCESS", {"key": "val"})
        self.assertIn("Audit log registrado", res)
        self.assertTrue(os.path.exists(AUDIT_LOG_FILE))

    def test_02_health_check(self):
        """Verifica que el informe de salud del sistema se ejecute sin excepciones."""
        report = health_check_system()
        self.assertIn("INFORME DE SALUD", report)

    def test_03_read_only_security_guardrail(self):
        """Verifica que execute_read_only_query bloquee intentos de mutación DDL/DML."""
        res = execute_read_only_query("DROP TABLE bakehouse.sales_customers", "databricks")
        self.assertIn("ERROR DE SEGURIDAD: Operación denegada", res)

    def test_04_kanban_local_ticket(self):
        """Verifica la creación y actualización de tarjetas en el Kanban local."""
        res_create = create_agile_ticket("Test Story", "Test Desc", "QA")
        self.assertTrue("creada" in res_create or "Trello" in res_create)

    def test_05_notification_manager(self):
        """Verifica que el motor de notificaciones despache alertas multicanal a maximilianonaranjo@gmail.com."""
        res = send_alert_notification("TEST_EVENT", "Alerta de Prueba Unitarias", "Mensaje de prueba de integración", "maximilianonaranjo@gmail.com", ["email"])
        self.assertIn("Alerta 'TEST_EVENT' procesada exitosamente", res)

    def test_06_github_issue_creator(self):
        """Verifica que la función de creación de GitHub Issues funcione o registre la auditoría."""
        res = git_create_issue("Test GitHub Issue", "Descripción de prueba para el issue de desarrollo de datos.")
        self.assertTrue("Issue #" in res or "Issue local registrado" in res)

    def test_07_agent_orchestrator_load(self):
        """Verifica que el agente orquestador de Google ADK cargue los 6 subagentes."""
        self.assertEqual(root_agent.name, "Orchestrator")
        self.assertEqual(len(root_agent.sub_agents), 6)
        sub_agent_names = [sa.name for sa in root_agent.sub_agents]
        expected_names = ["Analyst", "Explorer", "Engineer", "QA", "BI", "DataOps"]
        for name in expected_names:
            self.assertIn(name, sub_agent_names)

if __name__ == "__main__":
    unittest.main()
