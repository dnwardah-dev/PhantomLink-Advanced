import { useMemo } from "react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { Activity, ChartNoAxesCombined } from "lucide-react";

const COLORS = {
  LOW: "#65e8c1",
  MEDIUM: "#ffbd69",
  HIGH: "#ff718c",
  CRITICAL: "#b58cff",
  UNKNOWN: "#8493b3",
};

export default function InvestigationAnalytics({ history = [] }) {
  const { riskData, indicatorData } = useMemo(() => {
    const riskCounts = {};
    const indicatorCounts = {};

    history.forEach((item) => {
      const level = item.risk_level || "UNKNOWN";
      riskCounts[level] = (riskCounts[level] || 0) + 1;

      (Array.isArray(item.indicators) ? item.indicators : []).forEach(
        (indicator) => {
          const code = indicator.code || "UNKNOWN";
          indicatorCounts[code] = (indicatorCounts[code] || 0) + 1;
        }
      );
    });

    return {
      riskData: Object.entries(riskCounts).map(([name, value]) => ({
        name,
        value,
      })),
      indicatorData: Object.entries(indicatorCounts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 6),
    };
  }, [history]);

  return (
    <section className="v5-analytics">
      <div className="v5-analytics-heading">
        <Activity size={19} />
        <span>INVESTIGATION ANALYTICS</span>
      </div>

      <div className="v5-analytics-grid">
        <div className="v5-analytics-card">
          <h3>RISK DISTRIBUTION</h3>
          <p>Distribution across loaded investigation records.</p>

          {riskData.length === 0 ? (
            <div className="v5-analytics-empty">
              No investigation data available.
            </div>
          ) : (
            <div className="v5-analytics-chart">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={105}
                    paddingAngle={4}
                    stroke="none"
                  >
                    {riskData.map((entry) => (
                      <Cell
                        key={entry.name}
                        fill={COLORS[entry.name] || COLORS.UNKNOWN}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="v5-analytics-legend">
            {riskData.map((entry) => (
              <span key={entry.name}>
                <i style={{
                  background: COLORS[entry.name] || COLORS.UNKNOWN
                }} />
                {entry.name}: {entry.value}
              </span>
            ))}
          </div>
        </div>

        <div className="v5-analytics-card">
          <div className="v5-analytics-card-title">
            <ChartNoAxesCombined size={17} />
            <h3>TOP DETECTED INDICATORS</h3>
          </div>
          <p>Most frequently recorded heuristic signals.</p>

          {indicatorData.length === 0 ? (
            <div className="v5-analytics-empty">
              No indicators recorded yet.
            </div>
          ) : (
            <div className="v5-analytics-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={indicatorData.map((item) => ({
                    ...item,
                    label: item.name
                      .replaceAll("_", " ")
                      .toLowerCase()
                      .replace(/\b\w/g, (c) => c.toUpperCase()),
                  }))}
                  margin={{ top: 20, right: 20, left: 0, bottom: 25 }}
                  barCategoryGap="35%"
                >
                  <CartesianGrid
                    stroke="#27344e"
                    strokeDasharray="3 5"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: "#b8c4dc", fontSize: 11 }}
                    tickLine={false}
                    axisLine={{ stroke: "#394763" }}
                    interval={0}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={{ fill: "#91a0bc", fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    cursor={{ fill: "#ad91ff12" }}
                    contentStyle={{
                      background: "#11192b",
                      border: "1px solid #465073",
                      borderRadius: 10,
                      color: "#f4f7ff",
                    }}
                  />
                  <Bar
                    dataKey="count"
                    name="Detected"
                    fill="#9f8aff"
                    radius={[9, 9, 0, 0]}
                    maxBarSize={85}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
