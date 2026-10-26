import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Activity,
  CalendarDays,
  CalendarClock,
  ChevronRight,
  CircleAlert,
  CircleDollarSign,
  Clock3,
  MoreHorizontal,
  MoveUpRight,
  Sparkles,
  Users,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from "recharts";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Avatar, SectionHeading } from "../../components/ui";
import { chartData, money } from "../../data/demo";
import { useGymStore } from "../../app/use-gym-store";

function StatCard({
  title,
  value,
  delta,
  change,
  icon: Icon,
  shade = "green",
  index = 0,
}: {
  title: string;
  value: string;
  delta: string;
  change: "up" | "down";
  icon: React.ElementType;
  shade?: "green" | "neutral" | "amber";
  index?: number;
}) {
  return (
    <motion.article
      className="stat-card"
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.07 }}
      whileHover={{ y: -3, transition: { duration: 0.18 } }}
    >
      <div className="stat-card-top">
        <span>{title}</span>
        <span className={`stat-icon stat-icon-${shade}`}><Icon size={18} strokeWidth={1.8} /></span>
      </div>
      <div className="stat-card-value">{value}</div>
      <div className="stat-card-foot">
        <span className={`stat-change stat-change-${change}`}>
          {change === "up" ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {delta}
        </span>
        <span>vs last week</span>
      </div>
    </motion.article>
  );
}

function VisitsChart() {
  return (
    <section className="panel chart-panel">
      <SectionHeading
        title="Attendance"
        description="Member visits throughout the week"
        action={
          <button className="select-compact" aria-label="Attendance range">
            Last 7 days <ChevronRight size={13} className="rotate-down" />
          </button>
        }
      />
      <div className="chart-legend"><span className="legend-marker" /> Check-ins <span className="chart-total">1,614 <small>visits</small></span></div>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 14, left: -18, right: 8, bottom: 0 }}>
            <defs>
              <linearGradient id="visitsFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#b5f24a" stopOpacity={0.19} />
                <stop offset="98%" stopColor="#b5f24a" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="var(--line)" strokeDasharray="3 7" />
            <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "var(--muted-2)", fontSize: 11 }} dy={10} />
            <Tooltip
              contentStyle={{ background: "var(--panel-strong)", border: "1px solid var(--line)", borderRadius: 12, color: "var(--text)", fontSize: 12 }}
              cursor={{ stroke: "var(--accent)", strokeDasharray: "4 4" }}
              formatter={(value) => [`${value} visits`, "Check-ins"]}
            />
            <Area type="monotone" dataKey="visits" stroke="#b5f24a" strokeWidth={2.5} fill="url(#visitsFill)" dot={false} activeDot={{ fill: "#b5f24a", stroke: "var(--panel)", strokeWidth: 3, r: 5 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="chart-bottom-note"><span><MoveUpRight size={14} /> 11.8%</span> more check-ins than last week</div>
    </section>
  );
}

function AtRiskPanel() {
  const members = useGymStore((state) => state.members);
  const atRisk = members.filter((member) => member.risk !== "low").slice(0, 4);
  return (
    <section className="panel risk-panel">
      <SectionHeading
        title="Members to check in on"
        description="Based on recent visit patterns"
        action={<button className="icon-button" aria-label="More options" onClick={() => toast.message("Member insights are based on seeded demo visits.")}><MoreHorizontal size={19} /></button>}
      />
      {atRisk.map((member, index) => (
        <Link className="risk-member-row" to={`/app/members/${member.id}`} key={member.id}>
          <Avatar name={member.name} color={member.color} size="small" />
          <span className="risk-member-info"><b>{member.name}</b><small>{member.visits} visits this month</small></span>
          <span className={`risk-signal risk-signal-${member.risk}`}>{member.risk}</span>
          <ChevronRight size={15} className="risk-arrow" />
          {index === 0 && <span className="sr-only">Highest follow-up priority</span>}
        </Link>
      ))}
      <Link to="/app/ai" className="panel-link">View all insights <ArrowRight size={14} /></Link>
    </section>
  );
}

function BusyHours() {
  const bars = [
    { hour: "6 AM", value: 46 },
    { hour: "8 AM", value: 67 },
    { hour: "10 AM", value: 35 },
    { hour: "12 PM", value: 24 },
    { hour: "2 PM", value: 31 },
    { hour: "4 PM", value: 59 },
    { hour: "6 PM", value: 88 },
    { hour: "8 PM", value: 71 },
  ];
  return (
    <section className="panel busy-panel">
      <SectionHeading
        title="When members come in"
        description="Average visits by hour"
        action={<span className="live-label"><span /> TODAY</span>}
      />
      <div className="busy-bars" aria-label="Average visits are highest at 6 PM">
        {bars.map((bar) => (
          <div className="busy-bar-column" key={bar.hour}>
            <div className={`busy-bar-track ${bar.value >= 80 ? "busy-bar-highlight" : ""}`}>
              <span style={{ height: `${bar.value}%` }} />
            </div>
            <span className="busy-bar-label">{bar.hour}</span>
          </div>
        ))}
      </div>
      <p className="busy-recommendation"><Sparkles size={15} /><span>Plan an extra coach from <b>5:30 PM</b>. Your busiest hour starts at 6.</span></p>
    </section>
  );
}

export default function DashboardPage() {
  const members = useGymStore((state) => state.members);
  const payments = useGymStore((state) => state.payments);
  const checkins = useGymStore((state) => state.checkedInIds);
  const activeMembers = members.filter((member) => member.status === "active").length;
  const expiring = members.filter((member) => member.status === "expiring").length;
  const revenue = payments.filter((payment) => payment.status === "Paid").reduce((sum, payment) => sum + payment.amount, 0);
  const outstanding = payments.filter((payment) => payment.status === "Due").reduce((sum, payment) => sum + payment.amount, 0);
  const arrivalText = new Intl.DateTimeFormat("en", { weekday: "long", month: "long", day: "numeric" }).format(new Date());

  return (
    <div className="dashboard-page">
      <motion.header
        className="dashboard-welcome"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="dashboard-welcome-copy">
          <span className="welcome-date">{arrivalText} <span> / </span> Iron Peak Fitness</span>
          <h1>Good morning, Aru.</h1>
          <p>Your club, at a glance. Here&apos;s what&apos;s happening today.</p>
          <div className="welcome-actions">
            <Link to="/app/check-in" className="button button-primary"><CircleDollarSign size={16} /> Open check-in</Link>
            <button className="button button-glass" onClick={() => toast.message("Your weekly summary is ready to review in AI insights.")}><Sparkles size={16} /> Weekly summary</button>
          </div>
        </div>
        <div className="dashboard-welcome-image" role="img" aria-label="Strength equipment inside a modern gym">
          <div className="welcome-image-caption"><span className="live-pulse" /><span>CLUB STATUS</span><b>All systems running</b></div>
        </div>
        <div className="welcome-glow" aria-hidden="true" />
      </motion.header>

      <div className="stats-grid">
        <StatCard index={0} title="Active members" value={String(activeMembers + 112)} delta="+8.4%" change="up" icon={Users} />
        <StatCard index={1} title="Check-ins today" value={String(84 + checkins.length)} delta="+12.1%" change="up" icon={Activity} shade="neutral" />
        <StatCard index={2} title="Collected today" value={money(revenue + 126400)} delta="+6.2%" change="up" icon={CircleDollarSign} shade="neutral" />
        <StatCard index={3} title="Renewals due" value={String(expiring + 8)} delta="4 this week" change="down" icon={CalendarClock} shade="amber" />
      </div>

      <div className="dashboard-main-grid">
        <VisitsChart />
        <AtRiskPanel />
      </div>

      <div className="dashboard-lower-grid">
        <BusyHours />
        <section className="panel quick-summary-panel">
          <div className="quick-summary-heading"><div className="summary-icon"><CircleAlert size={18} /></div><button className="icon-button" aria-label="More summary options" onClick={() => toast.message("Summary is using the seeded demo payment data.")}><MoreHorizontal size={19} /></button></div>
          <p className="quick-summary-label">Needs attention</p>
          <h2>{money(outstanding + 42200)} <span>open dues</span></h2>
          <p className="quick-summary-copy">A few members are waiting on payment reminders. A quick note today can save a missed renewal.</p>
          <Link className="button button-secondary summary-action" to="/app/payments">Review dues <ArrowRight size={15} /></Link>
        </section>
      </div>

      <section className="today-schedule">
        <SectionHeading
          title="Coming up today"
          description="Your studio schedule"
          action={<Link to="/app/classes" className="panel-link">See timetable <ArrowRight size={14} /></Link>}
        />
        <div className="schedule-strip">
          {[
            { time: "05:30 PM", name: "Strength Lab", trainer: "Dinesh Herath", count: "15 / 16", type: "strength" },
            { time: "06:30 PM", name: "Zumba", trainer: "Maya de Alwis", count: "17 / 20", type: "dance" },
            { time: "07:30 PM", name: "Boxing Basics", trainer: "Kasun Silva", count: "8 / 12", type: "boxing" },
          ].map((session) => (
            <article className={`schedule-item schedule-${session.type}`} key={session.name}>
              <div className="schedule-time"><Clock3 size={13} /> {session.time}</div>
              <h3>{session.name}</h3>
              <div className="schedule-footer"><Avatar name={session.trainer} size="small" /><span>{session.trainer}</span><span className="schedule-count">{session.count}</span></div>
            </article>
          ))}
          <Link to="/app/classes" className="schedule-add"><CalendarDays size={19} /><span>View full<br />schedule</span><ChevronRight size={15} /></Link>
        </div>
      </section>
    </div>
  );
}
