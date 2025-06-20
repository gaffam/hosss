class AutomationCurve:
    """Simple linear automation curve."""

    def __init__(self):
        self.points = [(0.0, 1.0)]

    def add_point(self, time: float, value: float):
        self.points.append((time, value))
        self.points.sort()

    def value_at(self, time: float) -> float:
        if not self.points:
            return 1.0
        prev_t, prev_v = self.points[0]
        for t, v in self.points[1:]:
            if time < t:
                if t == prev_t:
                    return v
                frac = (time - prev_t) / (t - prev_t)
                return prev_v + (v - prev_v) * frac
            prev_t, prev_v = t, v
        return self.points[-1][1]
