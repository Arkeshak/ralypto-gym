import { zodResolver } from "@hookform/resolvers/zod";
import {
  Activity,
  ArrowDown,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  AudioLines,
  CalendarDays,
  Check,
  CheckCheck,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleAlert,
  CircleDollarSign,
  ClipboardCheck,
  Clock3,
  CreditCard,
  Dumbbell,
  Ellipsis,
  FileDown,
  Filter,
  Flame,
  Heart,
  MessageCircle,
  Minus,
  MoreHorizontal,
  Plus,
  QrCode,
  ScanLine,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  UserRoundPlus,
  Users,
  WalletCards,
  X,
} from "lucide-react";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import { toast } from "sonner";
import { z } from "zod";
import { useGymStore } from "../app/use-gym-store";
import { money, type Member, type Payment } from "../data/demo";
import {
  Avatar,
  Button,
  ConfirmAction,
  EmptyState,
  Modal,
  PageIntro,
  SearchInput,
  SectionHeading,
  StatusPill,
  Toggle,
  useModalState,
} from "../components/ui";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const memberSchema = z.object({
  name: z.string().min(2, "Enter the member's full name."),
  phone: z.string().min(8, "Enter a valid phone number."),
  email: z.union([z.email("Enter a valid email address."), z.literal("")]),
  goal: z.string().min(2, "Select or enter a fitness goal."),
  plan: z.string().min(1, "Choose a membership plan."),
});
type MemberForm = z.infer<typeof memberSchema>;

export function LoginPage({ onLogin }: { onLogin: () => void }) {
  const { setRole } = useGymStore();
  const [pin, setPin] = useState("");
  const [showPin, setShowPin] = useState(false);
  return (
    <main className="login-page">
      <div className="login-card">
        <Link className="brand-lockup" to="/app/dashboard"><span className="brand-icon"><Dumbbell size={20} /></span><span className="brand-name">ralypto<span>GYM</span></span></Link>
        <div className="login-heading"><p>IRON PEAK FITNESS</p><h1>Good to see you.</h1><span>Choose a demo account to enter the workspace.</span></div>
        <div className="login-options">
          {[
            { title: "Owner account", detail: "Full club overview", role: "Owner" as const, icon: CircleDollarSign },
            { title: "Front desk", detail: "Fast member check-in", role: "Front desk" as const, icon: ArrowDownRight },
            { title: "Trainer", detail: "Clients and sessions", role: "Trainer" as const, icon: Dumbbell },
          ].map(({ title, detail, icon: Icon, role }) => (
            <button className="login-option" onClick={() => { setRole(role); onLogin(); }} key={title}><span className="login-option-icon"><Icon size={18} /></span><span><b>{title}</b><small>{detail}</small></span><ArrowRight size={16} className="login-option-arrow" /></button>
          ))}
        </div>
        <button className="demo-pin-toggle" onClick={() => setShowPin(!showPin)}><span>Front desk PIN access</span><ChevronDown size={14} className={showPin ? "rotate-down" : ""} /></button>
        {showPin && <form className="demo-pin-form" onSubmit={(event) => { event.preventDefault(); if (pin === "1234") { setRole("Front desk"); onLogin(); } else toast.error("Use the demo PIN 1234."); }}><label htmlFor="demo-pin">4-digit PIN</label><input id="demo-pin" inputMode="numeric" maxLength={4} value={pin} onChange={(event) => setPin(event.target.value.replace(/\D/g, ""))} placeholder="Enter PIN" /><Button variant="primary" type="submit">Continue</Button><small>Demo PIN: 1234</small></form>}
        <p className="login-note"><ShieldCheck size={14} /> Demo sign-in only. No server or real account is used.</p>
      </div>
      <div className="login-visual"><div className="login-visual-copy"><span>IRON PEAK FITNESS</span><h2>Earn your<br /><em>strong.</em></h2><p>One club. Every detail in its place.</p></div></div>
    </main>
  );
}

function MemberFormPanel({ onSave, onClose }: { onSave: (member: MemberForm) => void; onClose: () => void }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<MemberForm>({
    resolver: zodResolver(memberSchema),
    defaultValues: { name: "", phone: "", email: "", goal: "General fitness", plan: "Monthly" },
  });
  return (
    <form className="stacked-form" onSubmit={handleSubmit((values) => { onSave(values); onClose(); })} noValidate>
      <div className="form-grid">
        <label className="form-field form-field-wide"><span>Full name</span><input {...register("name")} placeholder="e.g. Sanjaya Perera" aria-invalid={Boolean(errors.name)} />{errors.name && <small className="field-error">{errors.name.message}</small>}</label>
        <label className="form-field"><span>Phone number</span><input {...register("phone")} placeholder="+94 77 123 4567" aria-invalid={Boolean(errors.phone)} />{errors.phone && <small className="field-error">{errors.phone.message}</small>}</label>
        <label className="form-field"><span>Email address</span><input {...register("email")} type="email" placeholder="name@email.com" aria-invalid={Boolean(errors.email)} />{errors.email && <small className="field-error">{errors.email.message}</small>}</label>
        <label className="form-field"><span>Fitness goal</span><select {...register("goal")}><option>General fitness</option><option>Build strength</option><option>Lose weight</option><option>Improve endurance</option><option>Build muscle</option></select></label>
        <label className="form-field"><span>Membership plan</span><select {...register("plan")}><option>Monthly</option><option>Quarterly</option><option>Yearly</option><option>Student</option><option>Day Pass</option></select></label>
      </div>
      <p className="form-footnote"><ShieldCheck size={14} /> Health details and consent can be added to the member profile later.</p>
      <footer className="form-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit" disabled={isSubmitting}><UserRoundPlus size={16} /> Add member</Button></footer>
    </form>
  );
}

function MemberDetails({ member, onBack }: { member: Member; onBack: () => void }) {
  const recordPayment = useGymStore((state) => state.recordPayment);
  return (
    <div className="product-page">
      <PageIntro title={member.name} description={`${member.id} / Member profile`} action={<Button variant="secondary" onClick={onBack}><ChevronLeft size={16} /> All members</Button>} />
      <section className="profile-hero panel">
        <Avatar name={member.name} color={member.color} size="large" />
        <div className="profile-hero-main"><h2>{member.name}</h2><p>{member.goal} <span>/</span> Joined June 12, 2025</p><div className="profile-hero-tags"><StatusPill status={member.status} /><span>{member.plan} plan</span></div></div>
        <div className="profile-contact"><span>{member.phone}</span><span>{member.email}</span></div>
        <div className="profile-actions"><Button variant="secondary" onClick={() => toast.message(`A reminder draft is ready for ${member.name}.`)}><MessageCircle size={15} /> Message</Button><Button variant="primary" onClick={() => { recordPayment(member.name, member.plan === "Quarterly" ? 13500 : 5000, "Cash"); toast.success("Payment added to the demo ledger."); }}><WalletCards size={15} /> Collect payment</Button></div>
      </section>
      <div className="profile-stats-grid">
        <div className="mini-stat"><span>Visits this month</span><b>{member.visits}</b><small>Last visit {member.lastVisit}</small></div>
        <div className="mini-stat"><span>Membership</span><b>{member.plan}</b><small>Renews {member.renewal}</small></div>
        <div className="mini-stat"><span>Attendance signal</span><b className="mini-stat-signal">{member.risk === "low" ? "On track" : "Needs a check-in"}</b><small>Based on recent visit pattern</small></div>
      </div>
      <section className="panel profile-history"><SectionHeading title="Recent activity" description="A quick look at the member's activity" /><div className="activity-list"><div><span className="activity-icon"><Check size={15} /></span><div><b>Membership active</b><small>{member.plan} membership renewed</small></div><time>Oct 18</time></div><div><span className="activity-icon"><Activity size={15} /></span><div><b>Gym visit</b><small>Checked in at Iron Peak Fitness</small></div><time>{member.lastVisit}</time></div><div><span className="activity-icon"><CreditCard size={15} /></span><div><b>Payment received</b><small>{money(member.plan === "Quarterly" ? 13500 : 5000)} membership payment</small></div><time>Oct 12</time></div></div></section>
    </div>
  );
}

export function MembersPage({ mode = "members" }: { mode?: "members" | "checkin" | "memberships" }) {
  const members = useGymStore((state) => state.members);
  const addMember = useGymStore((state) => state.addMember);
  const payments = useGymStore((state) => state.payments);
  const [searchParams] = useSearchParams();
  const { memberId } = useParams();
  const navigate = useNavigate();
  const [search, setSearch] = useState(searchParams.get("q") ?? "");
  const [filter, setFilter] = useState("All statuses");
  const modal = useModalState();
  const filtered = useMemo(() => members.filter((member) => {
    const matchesText = `${member.name} ${member.phone} ${member.id} ${member.plan}`.toLowerCase().includes(search.trim().toLowerCase());
    return matchesText && (filter === "All statuses" || member.status === filter.toLowerCase());
  }), [filter, members, search]);

  if (memberId) {
    const selected = members.find((member) => member.id === memberId);
    if (!selected) return <div className="product-page"><EmptyState title="Member not found" description="This profile is not in the current demo workspace." action={<Link className="button button-secondary" to="/app/members">Back to members</Link>} /></div>;
    return <MemberDetails member={selected} onBack={() => navigate("/app/members")} />;
  }

  if (mode === "checkin") {
    return <CheckInPage members={members} onCollect={(member) => { toast.success(`Payment recorded for ${member.name}.`); }} />;
  }
  if (mode === "memberships") return <MembershipPlansPage />;

  const handleAddMember = (values: MemberForm) => {
    addMember(values);
    toast.success(`${values.name} added to the demo member list.`);
  };
  const activeCount = members.filter((member) => member.status === "active").length;
  const dueCount = payments.filter((payment) => payment.status === "Due").length;

  return (
    <div className="product-page">
      <PageIntro title="Members" description="A clear picture of every person in your club." action={<Button variant="primary" onClick={modal.show}><Plus size={17} /> Add member</Button>} />
      <div className="member-overview-strip">
        <div><span>Showing members</span><b>{members.length + 110} <small>total</small></b></div><span className="overview-strip-divider" />
        <div><span>Active today</span><b className="number-green">{activeCount + 112}</b></div><span className="overview-strip-divider" />
        <div><span>Renewals soon</span><b>{members.filter((member) => member.status === "expiring").length + 8}</b></div><span className="overview-strip-divider" />
        <div><span>Payments due</span><b>{dueCount + 7}</b></div>
      </div>
      <div className="member-table-panel panel">
        <div className="table-toolbar">
          <div className="table-toolbar-left"><SearchInput value={search} onChange={setSearch} placeholder="Name, number or member ID" ariaLabel="Search members" /><button className="filter-button"><Filter size={15} /> Filter <ChevronDown size={13} /></button><select className="table-status-filter" value={filter} onChange={(event) => setFilter(event.target.value)} aria-label="Filter by status"><option>All statuses</option>{(["active", "expiring", "grace", "expired", "frozen", "stopped"] as const).map((status) => <option value={status} key={status}>{status[0].toUpperCase() + status.slice(1)}</option>)}</select></div>
          <Button variant="secondary" size="small" onClick={() => toast.message("Member export is a frontend demo action.")}><FileDown size={15} /> Export</Button>
        </div>
        {filtered.length ? (
          <div className="table-scroll"><table className="data-table member-table">
            <thead><tr><th>MEMBER</th><th>MEMBERSHIP</th><th>STATUS</th><th>VISITS</th><th>LAST VISIT</th><th>RENEWAL</th><th /></tr></thead>
            <tbody>{filtered.map((member) => <tr key={member.id}>
              <td><Link className="table-member" to={`/app/members/${member.id}`}><Avatar name={member.name} color={member.color} size="small" /><span><b>{member.name}</b><small>{member.id}</small></span></Link></td>
              <td>{member.plan}</td><td><StatusPill status={member.status} /></td><td>{member.visits}</td><td className="table-muted">{member.lastVisit}</td><td>{member.renewal}</td><td><Link className="icon-button row-more" aria-label={`View ${member.name}`} to={`/app/members/${member.id}`}><ChevronRight size={16} /></Link></td>
            </tr>)}</tbody>
          </table></div>
        ) : <EmptyState title="No members found" description="Try another name, phone number, or membership status." action={<Button variant="secondary" onClick={() => { setSearch(""); setFilter("All statuses"); }}>Clear filters</Button>} />}
        <div className="table-footer"><span>Showing {filtered.length} demo profiles <span>/</span> More members available in the full gym account</span><div><button className="icon-button" aria-label="Previous page" disabled><ChevronLeft size={16} /></button><span className="table-page-number">1</span><button className="icon-button" aria-label="Next page" onClick={() => toast.message("You're viewing all seeded demo members.")}><ChevronRight size={16} /></button></div></div>
      </div>
      <Modal title="Add a member" description="A few details to get their membership started." open={modal.open} onClose={modal.close}><MemberFormPanel onSave={handleAddMember} onClose={modal.close} /></Modal>
    </div>
  );
}

function CheckInPage({ members, onCollect }: { members: Member[]; onCollect: (member: Member) => void }) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Member | null>(null);
  const [checked, setChecked] = useState<"ok" | "blocked" | null>(null);
  const checkIn = useGymStore((state) => state.checkIn);
  const count = useGymStore((state) => state.checkedInIds.length);
  const findMember = () => {
    const value = query.trim().toLowerCase();
    const match = members.find((member) => `${member.name} ${member.phone} ${member.id}`.toLowerCase().includes(value));
    if (!value || !match) {
      setSelected(null);
      setChecked("blocked");
      toast.error(value ? "No member matches that search." : "Enter a member name, phone, or ID.");
      return;
    }
    setSelected(match);
    const result = checkIn(match.id);
    setChecked(result ? "ok" : "blocked");
    result ? toast.success(`${match.name} checked in.`) : toast.error(match.status !== "active" ? `${match.name}'s membership is ${match.status}.` : `${match.name} is already checked in.`);
  };
  return (
    <div className="product-page checkin-page">
      <PageIntro title="Quick check-in" description="A fast hello on the way in." action={<span className="online-pill"><span /> Online</span>} />
      <div className="checkin-layout">
        <section className="checkin-search-panel panel">
          <span className="checkin-large-icon"><ScanLine size={22} /></span>
          <h2>Ready when they are.</h2>
          <p>Look up a member by name, phone, or membership number.</p>
          <form className="checkin-form" onSubmit={(event) => { event.preventDefault(); findMember(); }}>
            <label htmlFor="checkin-search">Find a member</label>
            <div className="checkin-search-row"><Search size={18} /><input id="checkin-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Try Nimali or IPF-1048" autoFocus /><Button variant="primary" type="submit">Check in <ArrowRight size={15} /></Button></div>
          </form>
          <button className="scan-qr-button" onClick={() => toast.message("Camera scanning is a UI preview. Enter a member ID to check in.")}><QrCode size={18} /> Scan member QR <span>Camera preview</span></button>
          <div className="checkin-hint"><ShieldCheck size={15} /><span>Member access is checked against their active membership.</span></div>
        </section>
        <section className={`checkin-result panel ${checked === "ok" ? "checkin-result-ok" : checked === "blocked" ? "checkin-result-blocked" : ""}`} aria-live="polite">
          {!selected ? (
            <div className="checkin-idle"><div className="checkin-idle-mark"><QrCode size={24} /></div><h2>Ready to welcome</h2><p>The member result will appear here.</p><div className="checkin-live-count"><Users size={15} /><span><b>{38 + count}</b> members in the club now</span><span className="live-dot" /></div></div>
          ) : (
            <div className="checkin-result-content">
              <div className={`checkin-state-icon ${checked === "ok" ? "checkin-state-pass" : "checkin-state-stop"}`}>{checked === "ok" ? <Check size={22} /> : <X size={22} />}</div>
              <div className="checkin-result-message"><h2>{checked === "ok" ? "You&apos;re all set." : "Hold on a moment."}</h2><p>{checked === "ok" ? "Membership verified. Enjoy your session." : `${selected.name}'s membership needs attention before entry.`}</p></div>
              <div className="checkin-member-card"><Avatar name={selected.name} color={selected.color} size="large" /><div><h3>{selected.name}</h3><p>{selected.id} <span>/</span> {selected.plan}</p></div><StatusPill status={selected.status} /></div>
              <div className="checkin-result-detail"><span>Membership renews</span><b>{selected.renewal}</b><span>Visits this month</span><b>{selected.visits}</b></div>
              {checked === "blocked" && <Button variant="primary" className="checkin-renew-button" onClick={() => onCollect(selected)}><WalletCards size={16} /> Collect payment</Button>}
              {checked === "ok" && <button className="checkin-reset" onClick={() => { setSelected(null); setQuery(""); setChecked(null); }}>Ready for next member <ArrowRight size={14} /></button>}
            </div>
          )}
        </section>
      </div>
      <section className="checkin-last-visits"><SectionHeading title="Recent arrivals" description="The latest check-ins at your front desk" /><div className="recent-arrivals">{members.filter((member) => member.status === "active").slice(0, 4).map((member, index) => <div className="arrival-row" key={member.id}><Avatar name={member.name} color={member.color} size="small" /><span><b>{member.name}</b><small>{member.plan}</small></span><time>{index === 0 ? "09:42 AM" : index === 1 ? "09:28 AM" : index === 2 ? "09:16 AM" : "08:58 AM"}</time><StatusPill status="active" /></div>)}</div></section>
    </div>
  );
}

function MembershipPlansPage() {
  const plans = [
    { name: "Day Pass", price: 800, detail: "A single day on the floor", members: "Flexible access" },
    { name: "Monthly", price: 5000, detail: "A strong start, month by month", members: "Gym floor access" },
    { name: "Student", price: 4000, detail: "Training that fits the semester", members: "Student ID required" },
    { name: "Quarterly", price: 13500, detail: "A steady three-month rhythm", members: "Gym floor access" },
    { name: "Yearly", price: 48000, detail: "One year to build your routine", members: "Best annual value" },
    { name: "Couple Monthly", price: 8500, detail: "Make training a shared habit", members: "Two members" },
  ];
  const [active, setActive] = useState("Monthly");
  return (
    <div className="product-page">
      <PageIntro title="Memberships" description="Flexible plans for every kind of training routine." action={<Button variant="primary" onClick={() => toast.message("Plan editor is available in the full product.")}><Plus size={16} /> New plan</Button>} />
      <div className="plan-intro-banner"><div><div className="banner-label"><ShieldCheck size={14} /> YOUR MEMBERSHIP MENU</div><h2>Make it easy to<br /><em>keep showing up.</em></h2><p>Clear plans. Simple renewals. No surprises.</p></div><div className="banner-plan-highlight"><span>MOST POPULAR</span><b>Monthly</b><small>Renews every 30 days</small><strong>Rs 5,000<small> / month</small></strong></div></div>
      <SectionHeading title="Membership plans" description="All prices shown in Sri Lankan rupees" action={<span className="count-label">{plans.length} plans</span>} />
      <div className="membership-plan-grid">{plans.map((plan, index) => <article className={`membership-plan-card ${plan.name === active ? "membership-plan-active" : ""}`} key={plan.name}>
        <div className="membership-plan-card-head"><span className="membership-plan-badge">{index === 1 ? <Flame size={13} /> : <ShieldCheck size={13} />}{index === 1 ? "Popular" : plan.name === active ? "Current" : "Available"}</span><button className="icon-button" aria-label={`Plan options: ${plan.name}`} onClick={() => toast.message(`${plan.name} plan options are part of the full admin experience.`)}><MoreHorizontal size={17} /></button></div>
        <h3>{plan.name}</h3><p>{plan.detail}</p><strong>{money(plan.price)}<small>{plan.name === "Day Pass" ? " / day" : " / month"}</small></strong>
        <div className="membership-plan-inclusions"><span><Check size={14} /> {plan.members}</span><span><Check size={14} /> Check-in access</span><span><Check size={14} /> Member app access</span></div>
        <Button variant={plan.name === active ? "secondary" : "primary"} onClick={() => { setActive(plan.name); toast.success(`${plan.name} selected.`); }}>{plan.name === active ? "Selected plan" : "Select plan"}</Button>
      </article>)}</div>
      <div className="notice-box"><CircleAlert size={17} /><div><b>Member limits are built into your workspace.</b><span>Plans, freezes, grace periods, and discounts help you manage each membership with care.</span></div></div>
    </div>
  );
}

function RecordPaymentForm({
  onSave,
  onClose,
}: {
  onSave: (name: string, amount: number, method: Payment["method"]) => void;
  onClose: () => void;
}) {
  const members = useGymStore((state) => state.members);
  const [name, setName] = useState(members[0]?.name ?? "");
  const [amount, setAmount] = useState("5000");
  const [method, setMethod] = useState<Payment["method"]>("Cash");
  const [reference, setReference] = useState("");
  const [error, setError] = useState("");
  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const total = Number(amount);
    if (!Number.isFinite(total) || total <= 0) { setError("Enter a payment amount greater than zero."); return; }
    if (method === "Bank transfer" && !reference.trim()) { setError("Add a bank reference for this payment."); return; }
    onSave(name, total, method);
    onClose();
  };
  return (
    <form className="stacked-form" onSubmit={submit}>
      <label className="form-field"><span>Member</span><select value={name} onChange={(event) => setName(event.target.value)}>{members.map((member) => <option key={member.id}>{member.name}</option>)}</select></label>
      <label className="form-field"><span>Amount (LKR)</span><div className="money-input"><span>Rs</span><input type="number" min="1" step="1" value={amount} onChange={(event) => setAmount(event.target.value)} /></div></label>
      <fieldset className="payment-methods"><legend>Payment method</legend><div>{(["Cash", "Card", "Bank transfer", "Online"] as const).map((option) => <button className={`payment-method-option ${method === option ? "payment-method-selected" : ""}`} type="button" key={option} onClick={() => setMethod(option)}>{option}</button>)}</div></fieldset>
      {method === "Bank transfer" && <label className="form-field"><span>Bank reference</span><input value={reference} onChange={(event) => setReference(event.target.value)} placeholder="e.g. Bank slip number" /></label>}
      {error && <p className="field-error" role="alert">{error}</p>}
      <p className="form-footnote"><ShieldCheck size={14} /> No real payment is processed. Demo entries stay in this browser.</p>
      <footer className="form-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit"><Check size={16} /> Record payment</Button></footer>
    </form>
  );
}

export function PaymentsPage() {
  const payments = useGymStore((state) => state.payments);
  const recordPayment = useGymStore((state) => state.recordPayment);
  const markDuePaid = useGymStore((state) => state.markDuePaid);
  const modal = useModalState();
  const paidTotal = payments.filter((payment) => payment.status === "Paid").reduce((total, payment) => total + payment.amount, 0) + 178300;
  const openTotal = payments.filter((payment) => payment.status === "Due").reduce((total, payment) => total + payment.amount, 0) + 47200;
  return (
    <div className="product-page">
      <PageIntro title="Payments" description="Take payments, keep track of dues, and make renewals easier." action={<Button variant="primary" onClick={modal.show}><Plus size={16} /> Record payment</Button>} />
      <div className="payments-stats-grid"><div className="payments-stat-card"><span className="payments-stat-icon"><CircleDollarSign size={18} /></span><span>Collected today</span><b>{money(paidTotal)}</b><small className="stat-positive"><ArrowUpRight size={13} /> 8.2% vs last week</small></div><div className="payments-stat-card"><span className="payments-stat-icon stat-icon-soft-amber"><Clock3 size={18} /></span><span>Open dues</span><b>{money(openTotal)}</b><small>Across {payments.filter((payment) => payment.status === "Due").length + 7} members</small></div><div className="payments-stat-card"><span className="payments-stat-icon stat-icon-soft-blue"><CreditCard size={18} /></span><span>Transactions</span><b>{payments.length + 39}</b><small>Recorded this month</small></div></div>
      <section className="panel payment-list-panel"><SectionHeading title="Recent transactions" description="Payment records for your demo workspace" action={<Button variant="secondary" size="small" onClick={() => toast.message("CSV export is a frontend demo action.")}><FileDown size={14} /> Export</Button>} /><div className="table-scroll"><table className="data-table"><thead><tr><th>MEMBER</th><th>INVOICE</th><th>METHOD</th><th>DATE</th><th>AMOUNT</th><th>STATUS</th><th /></tr></thead><tbody>{payments.map((payment) => <tr key={payment.id}><td><span className="table-name-only">{payment.member}</span></td><td className="table-muted">{payment.id}</td><td><span className="payment-method-cell">{payment.method === "Cash" ? <WalletCards size={14} /> : payment.method === "Bank transfer" ? <ArrowDown size={14} /> : <CreditCard size={14} />}{payment.method}</span></td><td className="table-muted">{payment.date}</td><td className="payment-amount">{money(payment.amount)}</td><td><StatusPill status={payment.status.toLowerCase()} /></td><td>{payment.status === "Due" ? <button className="table-action-link" onClick={() => { markDuePaid(payment.id); toast.success(`${payment.member}'s due was marked paid.`); }}>Mark paid</button> : <button className="icon-button" aria-label={`View receipt ${payment.id}`} onClick={() => toast.message(`Receipt ${payment.id} is ready to print in the full product.`)}><ChevronRight size={16} /></button>}</td></tr>)}</tbody></table></div><div className="table-footer"><span>Recent payments <span>/</span> Demo ledger</span><div><span className="table-page-number">1</span></div></div></section>
      <div className="receipt-note"><ClipboardCheck size={17} /><div><b>Receipts are ready when you are.</b><span>Printed and mobile-friendly receipts are planned for the full frontend flow.</span></div><Button variant="ghost" size="small" onClick={() => toast.message("Sample receipt preview is not connected to a payment gateway.")}>Preview receipt <ArrowRight size={14} /></Button></div>
      <Modal title="Record a payment" description="Add a payment to your local demo ledger." open={modal.open} onClose={modal.close}><RecordPaymentForm onClose={modal.close} onSave={(name, amount, method) => { recordPayment(name, amount, method); toast.success(`${money(amount)} payment recorded for ${name}.`); }} /></Modal>
    </div>
  );
}

const weekdaySessions = [
  { name: "Monday", classes: ["HIIT Circuit", "Strength Lab", "Yoga Flow"] },
  { name: "Tuesday", classes: ["Boxing Basics", "Pilates", "Zumba"] },
  { name: "Wednesday", classes: ["Strength Lab", "Mobility & Core", "Spin Class"] },
  { name: "Thursday", classes: ["HIIT Circuit", "Morning Yoga", "Zumba"] },
  { name: "Friday", classes: ["Full Body Strength", "Boxing Basics", "Yoga Flow"] },
];

export function ClassesPage() {
  const classes = useGymStore((state) => state.classes);
  const bookClass = useGymStore((state) => state.bookClass);
  const [day, setDay] = useState("Today");
  const sessions = classes.map((session, index) => ({ ...session, time: day === "Tomorrow" ? ["06:30 AM", "09:00 AM", "05:30 PM", "06:30 PM", "07:30 PM"][index] : session.time }));
  const book = (sessionId: string, name: string) => {
    const session = classes.find((entry) => entry.id === sessionId);
    if (!session || session.booked >= session.capacity) { toast.error("This class is full. Join the waitlist instead."); return; }
    bookClass(sessionId);
    toast.success(`You've been booked for ${name}.`);
  };
  return (
    <div className="product-page">
      <PageIntro title="Classes" description="Plan a great session and make room for everyone." action={<Button variant="primary" onClick={() => toast.message("Class editing is shown as a demo UI.")}><Plus size={16} /> Add a class</Button>} />
      <div className="schedule-toolbar"><div className="day-picker"><button className="icon-button" aria-label="Previous day" onClick={() => setDay("Today")}><ChevronLeft size={16} /></button><span>{day === "Today" ? "Tuesday, October 27" : "Wednesday, October 28"}</span><button className="icon-button" aria-label="Next day" onClick={() => setDay("Tomorrow")}><ChevronRight size={16} /></button></div><div className="schedule-filters"><button className="select-compact">All instructors <ChevronDown size={14} /></button><button className="select-compact"><CalendarDays size={14} /> Week view <ChevronDown size={14} /></button></div></div>
      <div className="classes-day-list">{sessions.map((session, index) => {
        const full = session.booked >= session.capacity;
        return <article className="class-session-row panel" key={session.id}><div className="class-session-time"><b>{session.time}</b><span>{index === 0 ? "45 min" : "60 min"}</span></div><div className={`class-session-tone class-session-tone-${index % 4}`}><Dumbbell size={19} /></div><div className="class-session-info"><h3>{session.name}</h3><p><Avatar name={session.trainer} size="small" /> {session.trainer} <span>/</span> {session.room}</p></div><div className="class-session-capacity"><div><b>{session.booked}</b> <span>/ {session.capacity} spots</span></div><span className="capacity-indicator"><i style={{ width: `${(session.booked / session.capacity) * 100}%` }} /></span></div><div className="class-session-availability"><span className={`availability-pill ${full ? "availability-full" : session.capacity - session.booked <= 3 ? "availability-few" : ""}`}>{full ? "Full" : `${session.capacity - session.booked} spots left`}</span><Button variant={full ? "secondary" : "primary"} size="small" disabled={full} onClick={() => book(session.id, session.name)}>{full ? "Waitlist" : "Book"}</Button></div><button className="icon-button class-more" aria-label={`More ${session.name} options`} onClick={() => toast.message(`Session details for ${session.name}.`)}><MoreHorizontal size={18} /></button></article>;
      })}</div>
      <section className="weekly-strip panel"><SectionHeading title="Weekly timetable" description="A quick look at this week's classes" action={<Button variant="ghost" size="small" onClick={() => toast.message("Full timetable is part of the demo UI.")}>Full timetable <ArrowRight size={14} /></Button>} /><div className="week-days">{weekdaySessions.map((weekday) => <div className="week-day" key={weekday.name}><b>{weekday.name}</b>{weekday.classes.map((className, i) => <button className={`week-class week-class-${i}`} key={className} onClick={() => toast.message(`${className} is on the ${weekday.name} timetable.`)}>{className}</button>)}</div>)}</div></section>
    </div>
  );
}

export function TrainersPage() {
  const coaches = [
    { name: "Kasun Silva", specialty: "Strength & conditioning", clients: 16, sessions: 28, color: "#99b784" },
    { name: "Maya de Alwis", specialty: "Yoga & mobility", clients: 12, sessions: 24, color: "#c9a1b1" },
    { name: "Dinesh Herath", specialty: "Sports performance", clients: 11, sessions: 22, color: "#8cadd1" },
    { name: "Thilini Samarasinghe", specialty: "Nutrition & recovery", clients: 9, sessions: 18, color: "#d0a674" },
  ];
  return (
    <div className="product-page">
      <PageIntro title="Trainers" description="Good coaching builds good habits. Keep everyone connected." action={<Button variant="primary" onClick={() => toast.message("Add trainer is ready for the connected staff flow.")}><UserRoundPlus size={16} /> Add trainer</Button>} />
      <div className="trainer-highlight panel"><div className="trainer-highlight-icon"><Dumbbell size={20} /></div><div><p>THIS WEEK</p><h2>82 coaching sessions</h2><span>Your team has 9 sessions scheduled today.</span></div><Button variant="secondary" onClick={() => toast.message("Coach calendar is shown in the full app.")}>Open calendar <ArrowRight size={15} /></Button></div>
      <div className="trainer-grid">{coaches.map((coach, i) => <article className="trainer-card panel" key={coach.name}><div className="trainer-card-top"><Avatar name={coach.name} color={coach.color} size="large" /><button className="icon-button" aria-label={`Options for ${coach.name}`} onClick={() => toast.message(`Trainer profile for ${coach.name}.`)}><MoreHorizontal size={18} /></button></div><h3>{coach.name}</h3><p>{coach.specialty}</p><div className="trainer-metrics"><div><b>{coach.clients}</b><span>Clients</span></div><div><b>{coach.sessions}</b><span>Sessions</span></div><div><b>{["4.9", "4.8", "4.9", "4.7"][i]}</b><span>Rating</span></div></div><button className="trainer-card-link" onClick={() => toast.message(`${coach.name}'s client list is ready to review.`)}>View clients <ArrowRight size={15} /></button></article>)}</div>
      <section className="panel trainer-session-list"><SectionHeading title="Today's coaching" description="Your upcoming personal training sessions" /><div className="trainer-session-row"><span className="session-time-dot">10:30</span><Avatar name="Kavindu Fernando" color="#d38c68" size="small" /><span><b>Strength foundations</b><small>Kavindu Fernando <span>/</span> Kasun Silva</small></span><StatusPill status="active" /></div><div className="trainer-session-row"><span className="session-time-dot">12:00</span><Avatar name="Nimali Perera" color="#b5f24a" size="small" /><span><b>Personal training</b><small>Nimali Perera <span>/</span> Dinesh Herath</small></span><StatusPill status="expiring" /></div><div className="trainer-session-row"><span className="session-time-dot">04:30</span><Avatar name="Ayesha Wickramasinghe" color="#d897ad" size="small" /><span><b>Movement assessment</b><small>Ayesha Wickramasinghe <span>/</span> Thilini Samarasinghe</small></span><StatusPill status="active" /></div></section>
    </div>
  );
}

export function WorkoutsPage() {
  const members = useGymStore((state) => state.members);
  const [tab, setTab] = useState<"Plans" | "Exercises">("Plans");
  const approvePlan = useGymStore((state) => state.approvePlan);
  const pending = members.filter((member) => member.risk === "high");
  const exercises = ["Goblet squat", "Dumbbell row", "Romanian deadlift", "Incline press", "Lat pulldown", "Dead bug"];
  return (
    <div className="product-page">
      <PageIntro title="Workout plans" description="A good plan starts with a coach who knows the person." action={<Button variant="primary" onClick={() => toast.message("A blank workout plan has been opened in this demo.")}><Plus size={16} /> Create plan</Button>} />
      <div className="segmented-tabs"><button className={tab === "Plans" ? "segmented-active" : ""} onClick={() => setTab("Plans")}>Plans <span>18</span></button><button className={tab === "Exercises" ? "segmented-active" : ""} onClick={() => setTab("Exercises")}>Exercise library <span>{exercises.length + 34}</span></button><span className="segmented-spacer" /><button className="select-compact" onClick={() => toast.message("Showing all trainers.")}>All trainers <ChevronDown size={13} /></button></div>
      {tab === "Plans" ? <><div className="pending-approval-banner"><span className="pending-icon"><Sparkles size={16} /></span><div><b>{pending.length} plans ready for your review</b><span>AI-assisted plans stay private until a trainer approves them.</span></div><Button variant="secondary" size="small" onClick={() => toast.message("Review each plan before sharing it with a member.")}>Review all <ArrowRight size={14} /></Button></div><div className="workout-plan-list">{[
        ...pending.slice(0, 3).map((member, index) => ({ name: `${member.goal} plan`, member: member.name, status: "Needs review", date: index === 0 ? "Just now" : "Today", source: "AI draft", color: member.color })),
        { name: "Strength foundations", member: "Kavindu Fernando", status: "Approved", date: "Oct 25", source: "Trainer plan", color: "#d38c68" },
        { name: "3-day movement reset", member: "Nimali Perera", status: "Approved", date: "Oct 24", source: "Trainer plan", color: "#b5f24a" },
        { name: "Building a stronger base", member: "Ravindu de Silva", status: "Approved", date: "Oct 23", source: "Template", color: "#8aadd0" },
      ].map((plan, index) => <article className="workout-plan-row panel" key={`${plan.member}-${plan.name}`}><div className={`workout-plan-cover workout-cover-${index % 4}`}><Dumbbell size={22} /></div><div className="workout-plan-info"><h3>{plan.name}</h3><p><Avatar name={plan.member} color={plan.color} size="small" /> {plan.member} <span>/</span> {plan.source}</p></div><span className={`plan-approval-pill ${plan.status === "Needs review" ? "plan-needs-review" : ""}`}>{plan.status === "Needs review" ? <Sparkles size={13} /> : <Check size={13} />}{plan.status}</span><time>{plan.date}</time><button className="icon-button" aria-label={`View ${plan.name}`} onClick={() => toast.message(`Plan detail for ${plan.member}.`)}><ChevronRight size={16} /></button><Button variant={plan.status === "Needs review" ? "primary" : "ghost"} size="small" onClick={() => { if (plan.status === "Needs review") { const member = pending.find((entry) => entry.name === plan.member); if (member) approvePlan(member.id); toast.success(`${plan.member}'s plan approved in the demo.`); } else toast.message("This plan is already approved."); }}>{plan.status === "Needs review" ? "Approve" : "View"}</Button></article>)}</div></> : <div className="exercise-grid">{exercises.map((exercise, index) => <article className="exercise-card panel" key={exercise}><div className={`exercise-art exercise-art-${index % 4}`}><Dumbbell size={21} /><span>{["Legs", "Back", "Posterior chain", "Chest", "Back", "Core"][index]}</span></div><div><h3>{exercise}</h3><p>{["Dumbbell", "Dumbbells", "Barbell", "Dumbbells", "Cable machine", "Bodyweight"][index]} <span>/</span> {index < 2 ? "Beginner" : "Intermediate"}</p></div><button className="icon-button" aria-label={`Exercise details: ${exercise}`} onClick={() => toast.message(`${exercise} exercise details are available in the full app.`)}><ChevronRight size={16} /></button></article>)}</div>}
      <p className="medical-note"><ShieldCheck size={14} /> Fitness plans are general guidance. A trainer reviews each member's plan before it is shared.</p>
    </div>
  );
}

const seedLeads = [
  { name: "Sanduni Weerasinghe", source: "Instagram", detail: "Interested in strength training", initial: "S", stage: "New", score: "Likely fit", color: "#cda1b0" },
  { name: "Heshan Mendis", source: "Walk-in", detail: "Asked about a quarterly plan", initial: "H", stage: "New", score: "Follow up", color: "#8fb9a4" },
  { name: "Piumi Abeysekara", source: "Friend referral", detail: "Trial pass ends this week", initial: "P", stage: "Trial", score: "Trial active", color: "#c9b075" },
  { name: "Chamika Peiris", source: "Walk-in", detail: "Visited twice on a trial pass", initial: "C", stage: "Trial", score: "Likely fit", color: "#87a9cb" },
  { name: "Yasara Dissanayake", source: "Instagram", detail: "Joined on a monthly plan", initial: "Y", stage: "Joined", score: "Converted", color: "#a8b995" },
  { name: "Nadeesha Samarawickrama", source: "Website", detail: "Follow-up requested next month", initial: "N", stage: "Lost", score: "Revisit later", color: "#b29ac8" },
];

export function LeadsPage() {
  const [stage, setStage] = useState("All leads");
  const stages = ["All leads", "New", "Trial", "Joined", "Lost"];
  const leads = stage === "All leads" ? seedLeads : seedLeads.filter((lead) => lead.stage === stage);
  return (
    <div className="product-page">
      <PageIntro title="Leads" description="Every great membership starts with a conversation." action={<Button variant="primary" onClick={() => toast.message("Add a lead to the full customer follow-up flow.")}><Plus size={16} /> Add lead</Button>} />
      <div className="lead-summary-grid"><div><span>Active leads</span><b>30</b><small><ArrowUpRight size={13} /> 6 new this week</small></div><div><span>Trials to follow up</span><b>8</b><small>3 ending this week</small></div><div><span>Conversion this month</span><b>28.6%</b><small>2 more than last month</small></div><div><span>Next follow-up</span><b>Today</b><small>5 conversations due</small></div></div>
      <div className="segmented-tabs lead-tabs">{stages.map((item) => <button key={item} className={stage === item ? "segmented-active" : ""} onClick={() => setStage(item)}>{item}{item !== "All leads" && <span>{seedLeads.filter((lead) => lead.stage === item).length}</span>}</button>)}</div>
      <div className="lead-board">{["New", "Trial", "Joined", "Lost"].map((column) => {
        const columnLeads = leads.filter((lead) => lead.stage === column);
        return <section className={`lead-column lead-column-${column.toLowerCase()}`} key={column}><div className="lead-column-heading"><h2>{column}</h2><span>{columnLeads.length}</span><button className="icon-button" aria-label={`Add ${column.toLowerCase()} lead`} onClick={() => toast.message(`Add a lead to ${column.toLowerCase()}.`)}><Plus size={16} /></button></div>{columnLeads.length ? columnLeads.map((lead) => <article className="lead-card panel" key={lead.name}><div className="lead-card-header"><Avatar name={lead.name} color={lead.color} size="small" /><span>{lead.name}</span><button className="icon-button" aria-label={`${lead.name} options`} onClick={() => toast.message(`${lead.name} lead details.`)}><Ellipsis size={16} /></button></div><p>{lead.detail}</p><div className="lead-card-footer"><span>{lead.source}</span><span className={`lead-score ${lead.score === "Likely fit" ? "lead-score-positive" : ""}`}>{lead.score}</span></div>{lead.stage === "Trial" && <Button variant="secondary" size="small" onClick={() => toast.message(`Follow-up draft ready for ${lead.name}.`)}><MessageCircle size={14} /> Send follow-up</Button>}</article>) : <div className="lead-empty">No leads in this stage.</div>}</section>;
      })}</div>
    </div>
  );
}

export function MessagesPage() {
  const [tab, setTab] = useState<"Needs review" | "Outbox" | "Campaigns">("Needs review");
  const [messageText, setMessageText] = useState("Hi Tharushi, it's been a little while since your last session. Your strength goals are waiting when you're ready. Would you like a hand getting back into your routine?");
  const [sent, setSent] = useState(false);
  return (
    <div className="product-page">
      <PageIntro title="Messages" description="A thoughtful note can bring someone back to the club." action={<Button variant="primary" onClick={() => toast.message("Message campaign builder is a frontend preview.")}><Plus size={16} /> New message</Button>} />
      <div className="message-top-stats"><div><span>Awaiting approval</span><b>04</b></div><div><span>Queued this week</span><b>18</b></div><div><span>Delivery channel</span><b>WhatsApp <small>links</small></b></div></div>
      <div className="segmented-tabs">{(["Needs review", "Outbox", "Campaigns"] as const).map((item) => <button className={tab === item ? "segmented-active" : ""} key={item} onClick={() => setTab(item)}>{item}{item === "Needs review" && <span>4</span>}</button>)}</div>
      {tab === "Needs review" ? <div className="message-review-layout"><div className="message-inbox panel">{[
        { name: "Tharushi Jayasinghe", label: "Win-back draft", time: "12 min ago", excerpt: "A warm note about a recent change in attendance...", risk: "high" },
        { name: "Ayesha Wickramasinghe", label: "Renewal reminder", time: "1 hour ago", excerpt: "A helpful reminder before a membership renews...", risk: "medium" },
        { name: "Kavindu Fernando", label: "Class follow-up", time: "Yesterday", excerpt: "A quick check-in after the last strength session...", risk: "low" },
        { name: "Piumi Abeysekara", label: "Trial follow-up", time: "Yesterday", excerpt: "A welcome note following a first visit...", risk: "medium" },
      ].map((message, index) => <button className={`message-inbox-item ${index === 0 ? "message-inbox-item-active" : ""}`} key={message.name} onClick={() => { setSent(false); setMessageText(index === 0 ? "Hi Tharushi, it's been a little while since your last session. Your strength goals are waiting when you're ready. Would you like a hand getting back into your routine?" : `Hi ${message.name.split(" ")[0]}, we'd love to hear how your training is going. Reply if we can help you get your next session booked.`); }}><div><Avatar name={message.name} size="small" /><span><b>{message.name}</b><small>{message.label}</small></span><time>{message.time}</time></div><p>{message.excerpt}</p><StatusPill status={message.risk} /></button>)}</div><div className="message-composer panel"><div className="message-compose-header"><div><Sparkles size={16} /><span>AI-assisted draft</span></div><StatusPill status="pending" /><button className="icon-button" aria-label="More message options"><MoreHorizontal size={18} /></button></div><div className="message-recipient"><Avatar name="Tharushi Jayasinghe" color="#c8a8e9" size="small" /><div><b>Tharushi Jayasinghe</b><span>WhatsApp <span>/</span> Preferred language: English</span></div></div><label htmlFor="message-body" className="message-body-label">MESSAGE PREVIEW</label><textarea id="message-body" rows={6} value={messageText} onChange={(event) => setMessageText(event.target.value)} /><p className="ai-safety-note"><ShieldCheck size={14} /> Review and edit AI-drafted messages before sending. Nothing sends automatically.</p><div className="message-composer-actions"><Button variant="ghost" onClick={() => { setMessageText(""); toast.message("The draft was cleared."); }}>Discard draft</Button><Button variant="secondary" onClick={() => toast.success("Your edits have been saved to the demo outbox.")}><Check size={15} /> Save changes</Button><Button variant="primary" disabled={!messageText.trim()} onClick={() => { setSent(true); toast.success("Message link created for review."); }}><Send size={15} /> {sent ? "Link ready" : "Create send link"}</Button></div>{sent && <div className="message-sent-confirm"><CheckCheck size={15} /> The message is ready to open in WhatsApp. No message was sent.</div>}</div></div> : <div className="message-empty panel"><EmptyState title={tab === "Outbox" ? "Your outbox is quiet" : "No campaigns yet"} description={tab === "Outbox" ? "Approved message previews will be listed here." : "Create a campaign to send an update to your community."} action={<Button variant="secondary" onClick={() => toast.message("This view is ready for the connected campaign flow.")}>Explore {tab.toLowerCase()}</Button>} /></div>}
    </div>
  );
}

export function AiCenterPage() {
  const members = useGymStore((state) => state.members);
  const [activeTab, setActiveTab] = useState("Member signals");
  const [selected, setSelected] = useState<Member | null>(null);
  const highRisk = members.filter((member) => member.risk === "high");
  return (
    <div className="product-page">
      <PageIntro title="AI insights" description="Useful suggestions for your team. Every important action stays yours to confirm." action={<span className="ai-status-pill"><span /><Sparkles size={14} /> Demo assistant ready</span>} />
      <section className="ai-welcome-panel panel"><div className="ai-welcome-mark"><Sparkles size={21} /></div><div><span>YOUR WEEKLY CLUB SNAPSHOT</span><h2>A few small nudges can make a difference.</h2><p>{highRisk.length + 9} members have changed their visit routine. We've drafted a few ideas for your team to review.</p></div><Button variant="primary" onClick={() => toast.message("Weekly snapshot ready to review. No messages will be sent.")}>View summary <ArrowRight size={15} /></Button></section>
      <div className="ai-metric-grid"><article className="ai-metric panel"><div className="ai-metric-title"><span>Members to check in on</span><span className="ai-metric-icon ai-tint-amber"><Heart size={17} /></span></div><b>{highRisk.length + 9}</b><p><ArrowUpRight size={13} /> 3 more than last week</p><small>Based on recent visit patterns</small></article><article className="ai-metric panel"><div className="ai-metric-title"><span>Plans waiting for review</span><span className="ai-metric-icon ai-tint-green"><Dumbbell size={17} /></span></div><b>{highRisk.length}</b><p>Trainer approval required</p><small>Members won't see drafts yet</small></article><article className="ai-metric panel"><div className="ai-metric-title"><span>Class attendance</span><span className="ai-metric-icon ai-tint-blue"><CalendarDays size={17} /></span></div><b>78%</b><p><ArrowUpRight size={13} /> Up 4% this month</p><small>Based on session bookings</small></article><article className="ai-metric panel"><div className="ai-metric-title"><span>Actions taken by AI</span><span className="ai-metric-icon ai-tint-purple"><ShieldCheck size={17} /></span></div><b>0 <small>without your approval</small></b><p>Every action needs a human tap</p><small>Nothing runs automatically</small></article></div>
      <div className="segmented-tabs">{["Member signals", "Workout coach", "Ask your gym", "Weekly summary", "Activity log"].map((tab) => <button className={activeTab === tab ? "segmented-active" : ""} key={tab} onClick={() => setActiveTab(tab)}>{tab}</button>)}</div>
      <section className="panel ai-risk-list-panel"><SectionHeading title={activeTab} description={activeTab === "Member signals" ? "A simple list based on recent visits and upcoming renewals." : "This is a local AI interface preview. Suggested actions require a human confirmation."} action={<button className="select-compact"><Filter size={14} /> All trainers <ChevronDown size={13} /></button>} />
        {activeTab === "Member signals" ? highRisk.length ? highRisk.slice(0, 6).map((member) => <button className="ai-risk-row" key={member.id} onClick={() => setSelected(member)}><Avatar name={member.name} color={member.color} size="small" /><span><b>{member.name}</b><small>{member.visits} visits this month <span>/</span> last in {member.lastVisit.toLowerCase()}</small></span><span className="ai-risk-reason">{member.status === "expiring" ? "Membership ending soon" : "Visits below usual pattern"}</span><span className="risk-signal risk-signal-high">Check in</span><ChevronRight size={15} /></button>) : <EmptyState title="No members to review" description="Your member visit patterns are looking steady." /> : <div className="ai-empty-panel"><span className="ai-empty-icon"><MessageCircle size={20} /></span><h3>{activeTab === "Workout coach" ? "Built to support your coaches." : activeTab === "Ask your gym" ? "Your numbers, in plain language." : activeTab === "Weekly summary" ? "Your club's week, at a glance." : "Every AI suggestion, accounted for."}</h3><p>{activeTab === "Workout coach" ? "Draft a plan from the gym exercise library, then send it to a trainer for review." : activeTab === "Ask your gym" ? "Ask about revenue, renewals, dues, and class demand using demo gym data." : activeTab === "Weekly summary" ? "Compare visits and revenue with last week and review suggested next steps." : "See what was suggested, who reviewed it, and whether it was approved."}</p><Button variant="secondary" onClick={() => activeTab === "Workout coach" ? toast.message("Open Workout Plans to review the member draft queue.") : toast.success(`${activeTab} demo view loaded.`)}>{activeTab === "Workout coach" ? "Open workout plans" : "Explore this view"} <ArrowRight size={14} /></Button></div>}
      </section>
      <p className="ai-disclaimer"><ShieldCheck size={14} /> AI suggestions are not medical advice. A trainer reviews all workout plans. Demo insights use seeded visit and payment data.</p>
      <Modal title={`Follow up with ${selected?.name ?? "a member"}`} description="Edit the draft first. Nothing will be sent until you choose an action." open={Boolean(selected)} onClose={() => setSelected(null)}><FollowUpDraft name={selected?.name ?? "member"} onClose={() => setSelected(null)} /></Modal>
    </div>
  );
}

function FollowUpDraft({ name, onClose }: { name: string; onClose: () => void }) {
  const [value, setValue] = useState(`Hi ${name.split(" ")[0]}, we miss seeing you at Iron Peak. Your training plan is ready whenever you'd like to pick it back up. Can we help you find a time this week?`);
  return <form className="stacked-form" onSubmit={(event) => { event.preventDefault(); toast.success("Draft saved for staff review. No message was sent."); onClose(); }}><label className="form-field"><span>Message draft</span><textarea rows={5} value={value} onChange={(event) => setValue(event.target.value)} /></label><p className="form-footnote"><ShieldCheck size={14} /> AI drafts are only suggestions. Review and edit before creating a send link.</p><footer className="form-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit"><Check size={15} /> Save draft</Button></footer></form>;
}

export function ReportsPage() {
  const chartData = [
    { name: "Mon", revenue: 68400, joins: 8 },
    { name: "Tue", revenue: 79200, joins: 12 },
    { name: "Wed", revenue: 71800, joins: 7 },
    { name: "Thu", revenue: 86600, joins: 14 },
    { name: "Fri", revenue: 80500, joins: 11 },
    { name: "Sat", revenue: 112400, joins: 18 },
    { name: "Sun", revenue: 62400, joins: 5 },
  ];
  const [metric, setMetric] = useState<"revenue" | "joins">("revenue");
  return (
    <div className="product-page">
      <PageIntro title="Reports" description="The details behind a healthy gym, in one clear view." action={<Button variant="secondary" onClick={() => toast.success("Report export prepared for this demo workspace.")}><FileDown size={15} /> Export report</Button>} />
      <div className="report-filter-bar"><button className="select-compact"><CalendarDays size={14} /> Oct 20 - Oct 26, 2026 <ChevronDown size={13} /></button><button className="select-compact"><Users size={14} /> All locations <ChevronDown size={13} /></button><span className="report-updated">Demo data updated just now</span></div>
      <div className="reports-stat-grid"><div className="report-stat-panel panel"><span>Net revenue</span><b>{money(541300)}</b><small className="stat-positive"><ArrowUpRight size={13} /> 9.4% on last week</small></div><div className="report-stat-panel panel"><span>New memberships</span><b>75</b><small className="stat-positive"><ArrowUpRight size={13} /> 12.7% on last week</small></div><div className="report-stat-panel panel"><span>Attendance</span><b>1,614</b><small className="stat-positive"><ArrowUpRight size={13} /> 11.8% on last week</small></div><div className="report-stat-panel panel"><span>Renewal rate</span><b>73.6%</b><small><span className="report-neutral">Across 38 renewals</span></small></div></div>
      <section className="panel report-chart-panel"><SectionHeading title="Club performance" description="A simple weekly view of your club's activity" action={<div className="metric-switch"><button className={metric === "revenue" ? "metric-switch-active" : ""} onClick={() => setMetric("revenue")}>Revenue</button><button className={metric === "joins" ? "metric-switch-active" : ""} onClick={() => setMetric("joins")}>New members</button></div>} /><div className="reports-chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} margin={{ top: 14, right: 18, bottom: 0, left: -12 }}><CartesianGrid vertical={false} stroke="var(--line)" strokeDasharray="3 7" /><XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "var(--muted-2)", fontSize: 11 }} dy={11} /><YAxis tickFormatter={(value) => metric === "revenue" ? `${Math.round(value / 1000)}k` : String(value)} axisLine={false} tickLine={false} tick={{ fill: "var(--muted-2)", fontSize: 10 }} /><Tooltip contentStyle={{ background: "var(--panel-strong)", border: "1px solid var(--line)", borderRadius: 12, color: "var(--text)", fontSize: 12 }} formatter={(value) => [metric === "revenue" ? money(Number(value)) : `${value} members`, metric === "revenue" ? "Revenue" : "Joins"]} /><Bar dataKey={metric} radius={[5, 5, 0, 0]}>{chartData.map((item) => <Cell key={item.name} fill={item.name === "Sat" ? "#b5f24a" : "var(--chart-muted)"} />)}</Bar></BarChart></ResponsiveContainer></div></section>
      <div className="report-lower-grid"><section className="panel"><SectionHeading title="Membership mix" description="Active member plans" /><div className="mix-list">{[{ name: "Monthly", count: 84, percentage: 56, color: "green" }, { name: "Quarterly", count: 42, percentage: 28, color: "blue" }, { name: "Yearly", count: 18, percentage: 12, color: "purple" }, { name: "Other", count: 6, percentage: 4, color: "amber" }].map((item) => <div className="mix-row" key={item.name}><div><b>{item.name}</b><span>{item.count} members</span></div><div className="mix-track"><i className={`mix-fill-${item.color}`} style={{ width: `${item.percentage}%` }} /></div><strong>{item.percentage}%</strong></div>)}</div></section><section className="panel"><SectionHeading title="Popular classes" description="Based on this week's bookings" /><div className="popular-class-list">{[{ name: "Zumba", bookings: 42, attendance: "94%" }, { name: "Strength Lab", bookings: 38, attendance: "89%" }, { name: "HIIT Circuit", bookings: 36, attendance: "86%" }].map((item, index) => <div className="popular-class-row" key={item.name}><span className={`popular-number ${index === 0 ? "popular-number-top" : ""}`}>0{index + 1}</span><div><b>{item.name}</b><small>{item.bookings} bookings</small></div><span>{item.attendance}<small> show rate</small></span></div>)}</div></section></div>
      <p className="demo-disclaimer">All figures on this page are sample values from the Iron Peak demo workspace.</p>
    </div>
  );
}

export function SubscriptionPage() {
  const [selected, setSelected] = useState("Premium");
  const tiers = [
    { name: "Basic", price: 5900, members: "Up to 150 members", staff: "3 staff accounts", features: ["Member records and check-in", "Memberships and payments", "Basic club reports"] },
    { name: "Standard", price: 12900, members: "Up to 500 members", staff: "10 staff accounts", features: ["Everything in Basic", "Classes and bookings", "Member app and workouts", "Attendance insights"] },
    { name: "Premium", price: 24900, members: "Unlimited members", staff: "Unlimited staff", features: ["Everything in Standard", "AI coaching and club insights", "Multi-branch support", "Priority support"] },
  ];
  return (
    <div className="product-page">
      <PageIntro title="My plan" description="The tools behind your club, all in one workspace." action={<span className="subscription-status"><span /> Trial ends Nov 8, 2026</span>} />
      <section className="subscription-current panel"><div className="subscription-current-icon"><ShieldCheck size={19} /></div><div><span>YOUR CURRENT PLAN</span><h2>Premium <small>plan</small></h2><p>Everything your club needs to keep members moving.</p></div><div className="subscription-current-price"><b>Rs 24,900</b><span>per month</span></div><Button variant="secondary" onClick={() => toast.message("Billing settings are a demo preview.")}>Manage billing <ArrowRight size={14} /></Button></section>
      <SectionHeading title="Choose the right plan" description="Simple monthly billing. Upgrade or change your plan at any time." action={<span className="currency-label">Prices shown in LKR</span>} />
      <div className="subscription-tier-grid">{tiers.map((tier) => <article className={`subscription-tier panel ${tier.name === selected ? "subscription-tier-selected" : ""}`} key={tier.name}><div className="subscription-tier-header"><span className="subscription-tier-name">{tier.name}</span>{tier.name === "Premium" && <span className="subscription-recommended">CURRENT PLAN</span>}</div><div className="subscription-price">{money(tier.price)}<small> / month</small></div><span className="subscription-tier-members">{tier.members}</span><span className="subscription-tier-staff">{tier.staff}</span><div className="subscription-feature-list">{tier.features.map((feature) => <span key={feature}><Check size={14} /> {feature}</span>)}</div><Button variant={tier.name === selected ? "secondary" : "primary"} onClick={() => { setSelected(tier.name); toast.success(`${tier.name} plan selected for this preview. No charge was made.`); }}>{tier.name === "Premium" ? "Current plan" : tier.name === selected ? "Selected plan" : `Choose ${tier.name}`}</Button></article>)}</div>
      <section className="subscription-invoice panel"><SectionHeading title="Recent invoices" description="Billing history for your demo workspace" action={<button className="panel-link" onClick={() => toast.message("All invoices are sample data.")}>See all invoices <ArrowRight size={14} /></button>} /><div className="invoice-line"><span><span className="invoice-icon"><FileDown size={15} /></span><span><b>Premium plan</b><small>Oct 8, 2026 <span>/</span> INV-SUB-0041</small></span></span><span className="invoice-amount">{money(24900)}</span><StatusPill status="paid" /><button className="icon-button" aria-label="Download invoice" onClick={() => toast.message("Invoice download is not connected in this preview.")}><ArrowDown size={15} /></button></div><div className="invoice-line"><span><span className="invoice-icon"><FileDown size={15} /></span><span><b>Premium plan</b><small>Sep 8, 2026 <span>/</span> INV-SUB-0032</small></span></span><span className="invoice-amount">{money(24900)}</span><StatusPill status="paid" /><button className="icon-button" aria-label="Download previous invoice" onClick={() => toast.message("Invoice download is not connected in this preview.")}><ArrowDown size={15} /></button></div></section>
      <p className="demo-disclaimer">Plan changes in this preview do not create a subscription or process a payment.</p>
    </div>
  );
}

export function SettingsPage({ onReset }: { onReset: () => void }) {
  const theme = useGymStore((state) => state.theme);
  const setTheme = useGymStore((state) => state.setTheme);
  const locale = useGymStore((state) => state.locale);
  const setLocale = useGymStore((state) => state.setLocale);
  const [online, setOnline] = useState(true);
  const [reminders, setReminders] = useState(true);
  const [classReminder, setClassReminder] = useState(true);
  const [planName, setPlanName] = useState("Iron Peak Fitness");
  return (
    <div className="product-page">
      <PageIntro title="Settings" description="Make the workspace feel at home in your club." action={<Button variant="primary" onClick={() => toast.success("Settings saved in this browser.")}><Check size={16} /> Save changes</Button>} />
      <div className="settings-layout"><nav className="settings-nav" aria-label="Settings sections">{["Club profile", "Preferences", "Notifications", "Membership rules", "Demo workspace"].map((item, index) => <a href={`#settings-${index}`} key={item} onClick={(event) => { event.preventDefault(); document.getElementById(`settings-${index}`)?.scrollIntoView({ behavior: "smooth" }); }} className={index === 0 ? "settings-nav-active" : ""}>{item}<ChevronRight size={14} /></a>)}</nav><div className="settings-content">
        <section className="settings-section panel" id="settings-0"><SectionHeading title="Club profile" description="The details your members see" /><div className="settings-form-grid"><label className="form-field"><span>Gym name</span><input value={planName} onChange={(event) => setPlanName(event.target.value)} /></label><label className="form-field"><span>Phone number</span><input defaultValue="+94 11 285 6400" /></label><label className="form-field"><span>Time zone</span><select defaultValue="Asia/Colombo"><option value="Asia/Colombo">Asia / Colombo (GMT+5:30)</option><option value="Asia/Kolkata">Asia / Kolkata</option></select></label><label className="form-field"><span>Currency</span><select defaultValue="LKR"><option value="LKR">LKR - Sri Lankan rupee</option><option value="USD">USD - US dollar</option></select></label><label className="form-field form-field-wide"><span>Club address</span><input defaultValue="48 Station Road, Nugegoda, Sri Lanka" /></label></div></section>
        <section className="settings-section panel" id="settings-1"><SectionHeading title="Preferences" description="How your workspace looks and reads" /><div className="settings-row"><div><b>Appearance</b><span>Choose a look for your team</span></div><div className="settings-segmented"><button className={theme === "light" ? "selected" : ""} onClick={() => setTheme("light")}>Light</button><button className={theme === "dark" ? "selected" : ""} onClick={() => setTheme("dark")}>Dark</button></div></div><div className="settings-row"><div><b>Display language</b><span>Navigation and member messages</span></div><select className="settings-value-select" value={locale} onChange={(event) => { setLocale(event.target.value as typeof locale); toast.message("Language preferences are previewed in the page footer."); }}><option value="en">English</option><option value="si">Sinhala</option><option value="ta">Tamil</option></select></div><div className="settings-row"><div><b>Front-desk offline mode</b><span>Queue local check-ins when the network drops</span></div><Toggle checked={online} onChange={setOnline} label="Offline check-in mode" /></div><p className="settings-info"><ShieldCheck size={15} /> Offline sync is not connected to a server in this UI preview.</p></section>
        <section className="settings-section panel" id="settings-2"><SectionHeading title="Notifications" description="Stay in step with the club" /><div className="settings-row"><div><b>Membership reminders</b><span>Notify the team before a membership expires</span></div><Toggle checked={reminders} onChange={setReminders} label="Membership reminders" /></div><div className="settings-row"><div><b>Class booking updates</b><span>Updates when a member books or cancels a session</span></div><Toggle checked={classReminder} onChange={setClassReminder} label="Class booking updates" /></div></section>
        <section className="settings-section panel" id="settings-3"><SectionHeading title="Membership rules" description="Set everyday rules for memberships" /><div className="settings-form-grid"><label className="form-field"><span>Grace period</span><select defaultValue="7"><option value="0">No grace period</option><option value="3">3 days</option><option value="7">7 days</option><option value="14">14 days</option></select></label><label className="form-field"><span>Late class cancellation</span><select defaultValue="4"><option value="2">2 hours before</option><option value="4">4 hours before</option><option value="12">12 hours before</option></select></label></div></section>
        <section className="settings-section settings-reset-panel panel" id="settings-4"><div><b>Reset this demo workspace</b><span>Restore the original sample members, payments, and classes.</span></div><Button variant="secondary" onClick={() => { onReset(); toast.success("Demo workspace reset to the original sample data."); }}>Reset demo data</Button></section>
      </div></div>
    </div>
  );
}

const memberNav = [
  { path: "/m/home", label: "Home", icon: Activity },
  { path: "/m/workout", label: "Workout", icon: Dumbbell },
  { path: "/m/classes", label: "Classes", icon: CalendarDays },
  { path: "/m/progress", label: "Progress", icon: TrendingUp },
  { path: "/m/assistant", label: "Assistant", icon: MessageCircle },
];

function MemberHome({ onTabChange }: { onTabChange: (tab: string) => void }) {
  return <><section className="member-mobile-banner"><div className="member-mobile-gym-name"><span>IRON PEAK FITNESS</span><button onClick={() => onTabChange("profile")} aria-label="Member profile"><Avatar name="Nimali Perera" size="small" /></button></div><h1>Ready when<br />you are, <em>Nimali.</em></h1><p>A good session starts with showing up.</p><div className="member-qr-card"><div><span>MEMBER PASS</span><b>Active member</b><small>Monthly plan <span>/</span> renews Nov 18</small></div><QRCodeSVG value="IRON-PEAK-DEMO-IPF-1048" size={78} bgColor="#f2f5ee" fgColor="#11120f" level="M" includeMargin /></div></section><section className="member-workout-today"><div><div className="member-section-row"><h2>Today's workout</h2><button onClick={() => onTabChange("workout")}>See plan <ArrowRight size={14} /></button></div><p>Strength foundations <span>/</span> 45 min</p><div className="member-exercise-mini"><span className="member-exercise-count">01</span><div><b>Goblet squat</b><small>3 sets <span>/</span> 10 reps</small></div><span className="exercise-done"><Check size={15} /></span></div><div className="member-exercise-mini"><span className="member-exercise-count">02</span><div><b>Dumbbell row</b><small>3 sets <span>/</span> 12 reps</small></div><span className="exercise-pending"><Plus size={15} /></span></div><button className="member-start-button" onClick={() => onTabChange("workout")}>Start your workout <ArrowRight size={16} /></button></div></section><section className="member-busy-card"><div><span>YOUR BEST TIME TO TRAIN</span><h2>Quieter between<br /><b>2 and 4 PM.</b></h2><p>Find some room to move.</p></div><div className="mini-crowd-chart">{[22, 30, 46, 26, 19, 33, 75, 84, 56, 32, 22, 18].map((level, index) => <span className={index === 5 ? "mini-crowd-best" : ""} style={{ height: `${level}%` }} key={index} />)}</div></section><button className="member-dues-row" onClick={() => toast.message("Your member payment preview is not connected to a payment provider.")}><span className="member-dues-icon"><WalletCards size={17} /></span><span><b>Membership up to date</b><small>Your next renewal is Nov 18, 2026.</small></span><ChevronRight size={17} /></button></>;
}

function MemberAssistant() {
  const [message, setMessage] = useState("");
  const [suggestion, setSuggestion] = useState("");
  const [pendingAction, setPendingAction] = useState(false);
  const bookClass = useGymStore((state) => state.bookClass);
  const respond = (text: string) => {
    setMessage(text);
    const normalized = text.toLowerCase();
    if (normalized.includes("book") || normalized.includes("zumba")) {
      setSuggestion("There's space in Zumba tomorrow at 6:30 PM. Want me to book one spot?");
      setPendingAction(true);
    } else if (normalized.includes("workout")) {
      setSuggestion("Today is strength foundations: goblet squats, dumbbell rows, and a short core finisher.");
      setPendingAction(false);
    } else if (normalized.includes("dues") || normalized.includes("payment")) {
      setSuggestion("Your monthly membership is active and your next renewal is November 18. You're all set.");
      setPendingAction(false);
    } else {
      setSuggestion("I can help with today's workout, class bookings, gym hours, or membership renewals.");
      setPendingAction(false);
    }
  };
  return <div className="member-assistant-page"><div className="assistant-header-mark"><Sparkles size={20} /></div><h1>How can I<br />help today?</h1><p>Ask about a workout, class, or membership.</p><div className="assistant-suggestions">{["What's today's workout?", "Book Zumba tomorrow", "Check my dues"].map((item) => <button key={item} onClick={() => respond(item)}>{item}<ArrowRight size={13} /></button>)}</div><div className="assistant-conversation"><div className="assistant-answer"><Sparkles size={16} /><div><b>Hi Nimali. I'm here to help.</b><span>I can look up your plan, answer a question, or suggest a class.</span></div></div>{suggestion && <><div className="assistant-question">{message}</div><div className="assistant-answer"><Sparkles size={16} /><div><b>{suggestion}</b>{pendingAction && <ConfirmAction label="Confirm booking" onCancel={() => { setPendingAction(false); toast.message("Booking cancelled."); }} onConfirm={() => { bookClass("CLS-04"); setPendingAction(false); setSuggestion("You're booked for Zumba tomorrow at 6:30 PM. See you there!"); toast.success("Your class booking is confirmed in the demo."); }} />}</div></div></>}</div><form className="assistant-input-row" onSubmit={(event) => { event.preventDefault(); if (message.trim()) respond(message); }}><input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask me anything..." aria-label="Ask the member assistant" /><button type="button" className="assistant-mic" aria-label="Voice input" onClick={() => toast.message("Voice transcription depends on browser support and is not connected in this demo.")}><AudioLines size={18} /></button><button className="assistant-send" aria-label="Send message"><Send size={17} /></button></form><small className="assistant-medical-note"><ShieldCheck size={13} /> Fitness guidance only. Ask your trainer about health concerns.</small></div>;
}

function MemberWorkout() {
  const [logged, setLogged] = useState(0);
  const exercises = [{ name: "Goblet squat", detail: "3 sets · 10 reps", group: "LEGS", color: "green" }, { name: "Dumbbell row", detail: "3 sets · 12 reps", group: "BACK", color: "blue" }, { name: "Romanian deadlift", detail: "3 sets · 10 reps", group: "FULL BODY", color: "purple" }];
  return <div className="member-route-content"><PageIntro title="Your workout" description="Strength foundations · today · about 45 minutes" /><div className="member-day-progress"><div><span>Workout progress</span><b>{logged} of {exercises.length} exercises</b></div><span>{Math.round((logged / exercises.length) * 100)}%</span><div className="member-progress-track"><i style={{ width: `${(logged / exercises.length) * 100}%` }} /></div></div><div className="member-workout-list">{exercises.map((exercise, index) => <article className="member-workout-card panel" key={exercise.name}><span className={`member-exercise-number ${exercise.color}`}>0{index + 1}</span><div><span className="exercise-group">{exercise.group}</span><h2>{exercise.name}</h2><p>{exercise.detail}</p><div className="rep-controls"><button onClick={(event) => event.currentTarget.parentElement?.querySelector("b")?.textContent && Number(event.currentTarget.parentElement.querySelector("b")!.textContent) > 1 && (event.currentTarget.parentElement.querySelector("b")!.textContent = String(Number(event.currentTarget.parentElement.querySelector("b")!.textContent) - 1))} aria-label={`Decrease reps for ${exercise.name}`}><Minus size={14} /></button><b>10</b><button onClick={(event) => { const output = event.currentTarget.parentElement?.querySelector("b"); if (output) output.textContent = String(Number(output.textContent) + 1); }} aria-label={`Increase reps for ${exercise.name}`}><Plus size={14} /></button><span>reps</span></div></div><button className={logged > index ? "workout-exercise-done" : "workout-exercise-check"} aria-label={logged > index ? `${exercise.name} complete` : `Mark ${exercise.name} complete`} onClick={() => setLogged((current) => logged > index ? current : Math.min(current + 1, exercises.length))}>{logged > index ? <Check size={17} /> : <Check size={17} />}</button></article>)}</div><Button variant="primary" className="member-complete-workout" onClick={() => { setLogged(exercises.length); toast.success("Workout complete. Nice work, Nimali."); }}>Finish workout <Check size={16} /></Button></div>;
}

function MemberClasses() {
  const classes = useGymStore((state) => state.classes);
  const bookClass = useGymStore((state) => state.bookClass);
  const [bookedIds, setBookedIds] = useState<string[]>([]);
  return <div className="member-route-content"><PageIntro title="Find your class" description="Book a spot and make time for yourself." /><div className="member-day-switch"><button className="member-day-active">Today <small>Tue 27</small></button><button>Tomorrow <small>Wed 28</small></button><button>Thu <small>Oct 29</small></button></div><div className="member-class-list">{classes.map((session, index) => <article className="member-class-card panel" key={session.id}><div className={`member-class-swatch member-swatch-${index % 4}`}><Dumbbell size={19} /></div><div className="member-class-info"><span>{session.time} <span>/</span> {session.room}</span><h2>{session.name}</h2><p>Coach {session.trainer} <span>/</span> {session.booked} of {session.capacity} spots</p></div><button className={`member-book-button ${bookedIds.includes(session.id) ? "member-booked" : ""}`} disabled={session.booked >= session.capacity} onClick={() => { if (session.booked >= session.capacity) { toast.error("This class is full."); return; } bookClass(session.id); setBookedIds((ids) => [...ids, session.id]); toast.success(`You're booked for ${session.name}.`); }}>{bookedIds.includes(session.id) ? <><Check size={14} /> Booked</> : session.booked >= session.capacity ? "Full" : "Book"}</button></article>)}</div></div>;
}

function MemberProgress() {
  const days = ["M", "T", "W", "T", "F", "S", "S"];
  const [selected, setSelected] = useState(0);
  return <div className="member-route-content"><PageIntro title="Your progress" description="Small wins add up. See the work you've put in." /><div className="member-streak-panel"><div className="streak-flame"><Flame size={22} /></div><div><span>YOUR CURRENT STREAK</span><b>4 <small>weeks</small></b><p>You've trained regularly for four weeks.</p></div><div className="streak-days">{days.map((day, index) => <button key={`${day}-${index}`} className={selected === index || index < 4 ? "streak-day-done" : ""} onClick={() => setSelected(index)}><span>{day}</span>{selected === index || index < 4 ? <Check size={13} /> : <span />}</button>)}</div></div><div className="member-progress-cards"><section className="panel"><span>MONTHLY VISITS</span><b>17</b><p><ArrowUpRight size={13} /> 4 more than last month</p><div className="progress-sparkline">{[22, 38, 32, 48, 40, 72, 61, 88, 68, 82, 100, 76].map((level, i) => <i key={i} style={{ height: `${level}%` }} />)}</div></section><section className="panel"><span>PERSONAL TRAINING</span><b>6 <small>of 10 sessions</small></b><p>Your session pack is 60% complete.</p><div className="personal-training-progress"><i /></div></section></div><section className="panel member-goal-panel"><SectionHeading title="Your goal" description="One step closer, every week." action={<button className="panel-link" onClick={() => toast.message("Goal editing is available in the full app.")}>Edit goal <ArrowRight size={13} /></button>} /><div className="member-goal-card"><span><Target size={18} /></span><div><b>Build a regular training routine</b><small>12 of 16 weekly sessions complete</small></div><strong>75%</strong></div></section></div>;
}

function MemberProfile() {
  const setLocale = useGymStore((state) => state.setLocale);
  const locale = useGymStore((state) => state.locale);
  const [updates, setUpdates] = useState(true);
  return <div className="member-route-content"><PageIntro title="Your profile" description="Your membership and preferences." /><section className="member-profile-card panel"><Avatar name="Nimali Perera" color="#b5f24a" size="large" /><h2>Nimali Perera</h2><p>Member since June 2025</p><StatusPill status="active" /><div><span>Member number</span><b>IPF-1048</b></div><div><span>Phone</span><b>+94 71 284 6138</b></div><div><span>Membership</span><b>Monthly · renews Nov 18</b></div></section><section className="panel member-settings-panel"><SectionHeading title="Your preferences" /><div><span>App language</span><select value={locale} onChange={(event) => { setLocale(event.target.value as typeof locale); toast.message("Language preference saved for the member preview."); }}><option value="en">English</option><option value="si">Sinhala</option><option value="ta">Tamil</option></select></div><div><span>Class updates</span><Toggle checked={updates} onChange={setUpdates} label="Class updates" /></div><div className="member-support-row"><span><b>Questions about your health form?</b><small>Your trainer can help you update your details.</small></span><button onClick={() => toast.message("Your trainer has been notified in this demo.")}>Contact trainer <ArrowRight size={13} /></button></div></section><button className="member-logout" onClick={() => toast.message("Member app preview only.")}>Sign out of member app</button></div>;
}

export function MemberAppPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const activeTab = location.pathname.split("/").filter(Boolean)[1] ?? "home";
  const setTab = (value: string) => navigate(`/m/${value}`);
  const content = activeTab === "workout" ? <MemberWorkout /> : activeTab === "classes" ? <MemberClasses /> : activeTab === "progress" ? <MemberProgress /> : activeTab === "assistant" ? <MemberAssistant /> : activeTab === "profile" ? <MemberProfile /> : <MemberHome onTabChange={setTab} />;
  return <div className="member-app-wrap member-web-preview"><header className="member-preview-top"><Link to="/app/dashboard"><ChevronLeft size={16} /> Staff app</Link><span><span /> MEMBER APP PREVIEW</span><select aria-label="Member profile" defaultValue="Nimali Perera" onChange={(event) => toast.message(`${event.target.value}'s member app preview is not configured.`)}><option>Nimali Perera</option><option>Kavindu Fernando</option></select></header><div className="member-web-shell"><div className="member-phone-frame"><div className="member-phone-status"><span>9:41</span><span><span /> ◈ ▰</span></div><main className={`member-screen ${activeTab === "home" ? "member-screen-home" : ""}`}>{content}</main>{activeTab !== "assistant" && <nav className="member-bottom-nav">{memberNav.map(({ path, label, icon: Icon }) => { const isActive = activeTab === path.split("/")[2]; return <button className={isActive ? "member-tab-active" : ""} onClick={() => setTab(path.split("/")[2])} key={path}><Icon size={19} /><span>{label}</span></button>; })}</nav>}{activeTab === "assistant" && <button className="member-assistant-bottom-back" onClick={() => setTab("home")}><ArrowRight size={14} /> Back to your home</button>}</div><aside className="member-desktop-aside"><div className="member-preview-aside-icon"><Dumbbell size={20} /></div><h1>A better training day starts here.</h1><p>The member app is built around your everyday routine: check in, see a plan, find a class, and keep moving.</p><div className="member-aside-features"><span><QrCode size={16} /> Personal QR member pass</span><span><Dumbbell size={16} /> Trainer-approved workouts</span><span><CalendarDays size={16} /> Easy class bookings</span><span><MessageCircle size={16} /> A helpful gym assistant</span></div><button onClick={() => { setTab("assistant"); toast.message("Try: Book Zumba tomorrow."); }}>Try the member assistant <ArrowRight size={14} /></button><small>Demo preview, responsive browser experience</small></aside></div></div>;
}

export function NotFoundPage() {
  return <main className="not-found"><span className="not-found-mark"><Dumbbell size={23} /></span><h1>That page isn't here yet.</h1><p>Return to your club overview to keep things moving.</p><Link className="button button-primary" to="/app/dashboard">Back to overview <ArrowRight size={15} /></Link></main>;
}
