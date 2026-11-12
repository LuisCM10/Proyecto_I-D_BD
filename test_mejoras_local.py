"""Pruebas sin conexión: python test_mejoras_local.py"""
from datetime import date, timedelta
import importlib
import sys
import types
import unittest

class BaseSimulada:
    def __init__(self):
        self.calls=[]
        self.resultados=[]
    def ejecutar_consulta(self, query, parameters=None, write=True):
        self.calls.append((query, parameters or {}, write))
        return self.resultados.pop(0) if self.resultados else []

fake_db=BaseSimulada()
conn=types.ModuleType('conexion')
conn.db=fake_db
sys.modules['conexion']=conn
import jobtogo_mejoras as m

class TestMejoras(unittest.TestCase):
    def setUp(self):
        fake_db.calls=[]
        fake_db.resultados=[]

    def test_vencimiento_y_cierre(self):
        hoy=date.today()
        fake_db.resultados=[[{'id':'a','estado':'Abierta','fecha_cierre':str(hoy-timedelta(days=1))},
                             {'id':'b','estado':'Abierta','fecha_cierre':str(hoy+timedelta(days=2))},
                             {'id':'c','estado':'Cerrada','fecha_cierre':str(hoy+timedelta(days=2))}]]
        rows=m.ofertas_detalladas('usr_1')
        self.assertEqual([x['estado_visible'] for x in rows],['Vencida','Abierta','Cerrada'])
        self.assertEqual(fake_db.calls[-1][2],False)

    def test_estado_postulacion_permisos(self):
        with self.assertRaises(ValueError):
            m.cambiar_estado_postulacion('emp_1','ofe_1','usr_1','Inventado')
        self.assertEqual(len(fake_db.calls),0)
        fake_db.resultados=[[{'estado':'En revisión','usuario_id':'usr_1'}]]
        m.cambiar_estado_postulacion('emp_1','ofe_1','usr_1','En revisión')
        q,p,_=fake_db.calls[-1]
        self.assertIn('PUBLICA',q)
        self.assertEqual(p['empresa_id'],'emp_1')
        self.assertEqual(p['estado'],'En revisión')

    def test_cierre_y_reapertura(self):
        with self.assertRaises(ValueError):
            m.cambiar_estado_vacante('emp_1','ofe_1','Abierta',str(date.today()-timedelta(days=1)))
        self.assertFalse(fake_db.calls)
        fake_db.resultados=[[{'id':'ofe_1','estado':'Cerrada'}]]
        m.cambiar_estado_vacante('emp_1','ofe_1','Cerrada')
        self.assertIn('PUBLICA', fake_db.calls[-1][0])

    def test_postulacion_sin_duplicados_y_cierre(self):
        with self.assertRaises(ValueError):
            m.postular_vacante('usr_1','ofe_1')
        q,params,_=fake_db.calls[-1]
        self.assertIn('NOT EXISTS',q)
        self.assertIn("coalesce(o.estado, 'Abierta')",q)
        self.assertIn('fecha_cierre',q)
        self.assertEqual(params,{'usuario_id':'usr_1','oferta_id':'ofe_1'})

    def test_vinculacion_restringida(self):
        with self.assertRaises(ValueError):
            m.resolver_solicitud_laboral('emp_1','usr_1','NO_EXISTE',True)
        fake_db.resultados=[[{'estado':'Aceptada'}]]
        m.resolver_solicitud_laboral('emp_1','usr_1','SOLICITA_VINCULACION',True)
        q,p,_=fake_db.calls[-1]
        self.assertIn('TRABAJA_EN',q)
        self.assertIn('r:SOLICITA_VINCULACION',q)
        self.assertEqual(p['empresa_id'],'emp_1')

    def test_guardar_favoritos(self):
        fake_db.resultados=[[{'id':'ofe_1'}]]
        m.guardar_favorito('usr_1','ofe_1')
        self.assertIn('MERGE (u)-[r:GUARDA_OFERTA]->(o)',fake_db.calls[-1][0])

    def test_notificaciones_sin_nuevas_entidades(self):
        # 5 consultas de eventos + una de avisos vistos
        fake_db.resultados=[[],[],[],[],[],[{'vistos':[]}]]
        self.assertEqual(m.notificaciones('profesional','usr_1'),[])
        self.assertTrue(all(not write for _,_,write in fake_db.calls))
        fake_db.resultados=[[{'total':1}]]
        m.marcar_notificaciones_leidas('profesional','usr_1',['uno'])
        q,params,_=fake_db.calls[-1]
        self.assertIn('n.notificaciones_vistas',q)
        self.assertEqual(params['claves'],['uno'])

if __name__=='__main__':
    unittest.main(verbosity=2)
