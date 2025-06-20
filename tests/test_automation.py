import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.automation import AutomationCurve

def test_automation_curve():
    curve = AutomationCurve()
    curve.add_point(1.0, 0.5)
    assert abs(curve.value_at(0.5) - 0.75) < 1e-6
    assert abs(curve.value_at(2.0) - 0.5) < 1e-6
