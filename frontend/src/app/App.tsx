import {
  Activity,
  ArrowUpRight,
  Bell,
  CalendarDays,
  ChevronDown,
  CircleDollarSign,
  Dumbbell,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquareText,
  Moon,
  PanelsTopLeft,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Sun,
  Users,
  WalletCards,
  X,
  type LucideIcon,
} from "lucide-react";
import { lazy, Suspense, useState } from "react";
import { Link, NavLink, Navigate, Outlet, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useGymStore } from "./use-gym-store";
import { Avatar } from "../components/ui";
const DashboardPage = lazy(() => import("../features/dashboard/DashboardPage"));
const AiCenterPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.AiCenterPage })));
const ClassesPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.ClassesPage })));
const LeadsPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.LeadsPage })));
const DemoLoginPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.LoginPage })));
const MembersPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.MembersPage })));
const MemberAppPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.MemberAppPage })));
const SubscriptionPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.SubscriptionPage })));
const MessagesPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.MessagesPage })));
const NotFoundPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.NotFoundPage })));
const PaymentsPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.PaymentsPage })));
const ReportsPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.ReportsPage })));
const SettingsPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.SettingsPage })));
const TrainersPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.TrainersPage })));
const WorkoutsPage = lazy(() => import("../features/product-pages").then((module) => ({ default: module.WorkoutsPage })));

type NavigationItem = { label: string; path: string; icon: LucideIcon; group: string };

const staffNavigation: NavigationItem[] = [
  { label: "Overview", path: "/app/dashboard", icon: LayoutDashboard, group: "WORKSPACE" },
  { label: "Check-in", path: "/app/check-in", icon: Activity, group: "WORKSPACE" },
  { label: "Members", path: "/app/members", icon: Users, group: "WORKSPACE" },
  { label: "Memberships", path: "/app/memberships", icon: ShieldCheck, group: "WORKSPACE" },
  { label: "Payments", path: "/app/payments", icon: WalletCards, group: "WORKSPACE" },
  { label: "Classes", path: "/app/classes", icon: CalendarDays, group: "TRAINING" },
  { label: "Trainers", path: "/app/trainers", icon: Dumbbell, group: "TRAINING" },
  { label: "Workouts", path: "/app/workouts", icon: Activity, group: "TRAINING" },
  { label: "Leads", path: "/app/leads", icon: ArrowUpRight, group: "GROWTH" },
  { label: "Messages", path: "/app/messages", icon: MessageSquareText, group: "GROWTH" },
  { label: "AI insights", path: "/app/ai", icon: Sparkles, group: "GROWTH" },
  { label: "Reports", path: "/app/reports", icon: PanelsTopLeft, group: "MANAGE" },
  { label: "My plan", path: "/app/subscription", icon: CircleDollarSign, group: "MANAGE" },
  { label: "Settings", path: "/app/settings", icon: Settings2, group: "MANAGE" },
];

const titles: Record<string, string> = {
  "/app/dashboard": "Overview",
  "/app/check-in": "Check-in",
  "/app/members": "Members",
  "/app/memberships": "Memberships",
  "/app/payments": "Payments",
  "/app/classes": "Classes",
  "/app/trainers": "Trainers",
  "/app/workouts": "Workouts",
  "/app/leads": "Leads",
  "/app/messages": "Messages",
  "/app/ai": "AI insights",
  "/app/reports": "Reports",
  "/app/subscription": "My plan",
  "/app/settings": "Settings",
};

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const location = useLocation();
  const activePath = location.pathname;
  const role = useGymStore((state) => state.role);
  const visibleNavigation = staffNavigation.filter(({ path }) => {
    if (role === "Front desk") return ["/app/dashboard", "/app/check-in", "/app/members", "/app/payments"].includes(path);
    if (role === "Trainer") return ["/app/dashboard", "/app/members", "/app/classes", "/app/trainers", "/app/workouts", "/app/ai"].includes(path);
    if (role === "Manager") return path !== "/app/subscription";
    return true;
  });
  const grouped = visibleNavigation.reduce<Record<string, NavigationItem[]>>((groups, item) => {
    groups[item.group] = [...(groups[item.group] ?? []), item];
    return groups;
  }, {});

  return (
    <aside className="sidebar">
      <Link className="brand-lockup" to="/app/dashboard" onClick={onNavigate}>
        <span className="brand-icon"><Dumbbell size={20} strokeWidth={2.2} /></span>
        <span className="brand-name">ralypto<span>GYM</span></span>
      </Link>
      <button className="workspace-switcher" onClick={() => toast.message("Iron Peak Fitness is the active demo workspace.")}>
        <span className="workspace-emblem">I</span>
        <span className="workspace-copy"><b>Iron Peak Fitness</b><small>Premium workspace</small></span>
        <ChevronDown size={15} />
      </button>

      <nav className="primary-nav" aria-label="Main navigation">
        {Object.entries(grouped).map(([group, items]) => (
          <div className="nav-group" key={group}>
            <p className="nav-group-label">{group}</p>
            {items.map(({ icon: Icon, label, path }) => {
              const isActive = activePath === path || (path === "/app/members" && activePath.startsWith("/app/members/"));
              return (
                <NavLink
                  key={path}
                  to={path}
                  onClick={onNavigate}
                  aria-current={isActive ? "page" : undefined}
                  className={`nav-link ${isActive ? "nav-link-active" : ""}`}
                >
                  <Icon size={17} strokeWidth={1.7} />
                  <span>{label}</span>
                  {label === "AI insights" && <span className="nav-count">5</span>}
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <Link className="member-preview-link" to="/m/home" onClick={onNavigate}>
          <div className="member-preview-phone"><span /><i /><span /><span /></div>
          <div><b>Member app</b><span>Preview the mobile app</span></div>
          <ArrowUpRight size={15} />
        </Link>
        <div className="sidebar-user">
          <Avatar name="Aru Wijesinghe" color="#a1bca0" size="small" />
          <span className="sidebar-user-copy"><b>Aru Wijesinghe</b><span>Gym owner</span></span>
          <button className="icon-button" aria-label="Account menu" onClick={() => toast.message("Signed in to the Iron Peak demo workspace.")}>
            <ChevronDown size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
}

function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const { role, setRole, plan, setPlan, theme, setTheme, locale, setLocale } = useGymStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);
  const pageTitle = titles[location.pathname] ?? (location.pathname.startsWith("/app/members/") ? "Members" : "Ralypto Gym");

  return (
    <div className={`app-shell ${theme === "light" ? "theme-light" : ""}`}>
      <aside className={`sidebar-container ${mobileMenuOpen ? "sidebar-container-open" : ""}`}>
        <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
        <button className="mobile-sidebar-close icon-button" aria-label="Close menu" onClick={() => setMobileMenuOpen(false)}>
          <X size={18} />
        </button>
      </aside>
      {mobileMenuOpen && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setMobileMenuOpen(false)} />}
      <div className="workspace">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu-button icon-button" aria-label="Open menu" onClick={() => setMobileMenuOpen(true)}>
              <Menu size={20} />
            </button>
            <span className="breadcrumb-root">Iron Peak</span>
            <span className="breadcrumb-slash">/</span>
            <span className="breadcrumb-current">{pageTitle}</span>
          </div>
          <div className="topbar-actions">
            <span className="demo-mode"><span /> DEMO WORKSPACE</span>
            {searchOpen ? (
              <form
                className="topbar-search"
                onSubmit={(event) => {
                  event.preventDefault();
                  navigate(`/app/members?q=${encodeURIComponent(searchValue)}`);
                  setSearchOpen(false);
                }}
              >
                <Search size={16} />
                <input aria-label="Search members" autoFocus placeholder="Find a member..." value={searchValue} onChange={(event) => setSearchValue(event.target.value)} />
                <button type="button" className="icon-button" onClick={() => setSearchOpen(false)} aria-label="Close search"><X size={14} /></button>
              </form>
            ) : (
              <button className="topbar-icon-button icon-button" aria-label="Search members" onClick={() => setSearchOpen(true)}><Search size={18} /></button>
            )}
            <div className="topbar-divider" />
            <button className="topbar-icon-button notification-button icon-button" aria-label="Notifications" onClick={() => toast.message("You're all caught up.")}>
              <Bell size={18} /><span />
            </button>
            {import.meta.env.VITE_DEV_TOOLS === "true" && (
              <label className="role-select-label dev-plan-switcher" aria-label="Dev gym plan">
                <select value={plan} onChange={(event) => setPlan(event.target.value as any)} aria-label="Dev switch gym plan">
                  <option value="Basic">Dev: Basic</option>
                  <option value="Standard">Dev: Standard</option>
                  <option value="Premium">Dev: Premium</option>
                </select>
                <ChevronDown size={13} />
              </label>
            )}
            <label className="role-select-label" aria-label="Demo user role">
              <select value={role} onChange={(event) => setRole(event.target.value as typeof role)} aria-label="Switch demo role">
                <option value="Owner">Owner</option>
                <option value="Manager">Manager</option>
                <option value="Front desk">Front desk</option>
                <option value="Trainer">Trainer</option>
              </select>
              <ChevronDown size={13} />
            </label>
            <div className="profile-menu-wrap">
              <button className="topbar-avatar-button" aria-label="Open user menu" onClick={() => setProfileOpen(!profileOpen)}>
                <Avatar name="Aru Wijesinghe" color="#a1bca0" size="small" />
              </button>
              {profileOpen && (
                <div className="profile-menu">
                  <div className="profile-menu-title"><b>Aru Wijesinghe</b><span>Owner account</span></div>
                  <button onClick={() => { navigate("/app/settings"); setProfileOpen(false); }}><Settings2 size={15} /> Account settings</button>
                  <button onClick={() => { navigate("/m/home"); setProfileOpen(false); }}><ArrowUpRight size={15} /> Member app preview</button>
                  <button onClick={() => { navigate("/login"); setProfileOpen(false); }}><LogOut size={15} /> Sign out</button>
                </div>
              )}
            </div>
          </div>
        </header>
        <main className="main-content">
          <Suspense fallback={<RouteLoading />}><Outlet /></Suspense>
        </main>
        <footer className="app-footer">
          <span><span className="footer-sparkle"><Dumbbell size={13} /></span> Ralypto Gym <span className="footer-separator">/</span> Iron Peak Fitness</span>
          <div className="footer-controls">
            <span>Demo data, local to this browser</span>
            <label className="footer-locale">
              <span className="sr-only">Language</span>
              <select value={locale} onChange={(event) => setLocale(event.target.value as typeof locale)}>
                <option value="en">EN</option><option value="si">SI</option><option value="ta">TA</option>
              </select>
            </label>
            <button className="footer-theme icon-button" aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`} onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
              {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default function App() {
  const resetDemo = useGymStore((state) => state.resetDemo);
  return (
    <Suspense fallback={<RouteLoading />}>
    <Routes>
      <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
      <Route path="/login" element={<DemoLoginPage onLogin={() => window.location.assign("/app/dashboard")} />} />
      <Route path="/app" element={<AppShell />}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="check-in" element={<CheckInRoute />} />
        <Route path="members" element={<MembersPage />} />
        <Route path="members/:memberId" element={<MembersPage />} />
        <Route path="memberships" element={<MembershipsRoute />} />
        <Route path="payments" element={<PaymentsPage />} />
        <Route path="classes" element={<ClassesPage />} />
        <Route path="trainers" element={<TrainersPage />} />
        <Route path="workouts" element={<WorkoutsPage />} />
        <Route path="leads" element={<LeadsPage />} />
        <Route path="messages" element={<MessagesPage />} />
        <Route path="ai" element={<AiCenterPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="subscription" element={<SubscriptionPage />} />
        <Route path="settings" element={<SettingsPage onReset={resetDemo} />} />
      </Route>
      <Route path="/m/*" element={<MemberAppPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
    </Suspense>
  );
}

function CheckInRoute() {
  return <MembersPage mode="checkin" />;
}

function MembershipsRoute() {
  return <MembersPage mode="memberships" />;
}

function RouteLoading() {
  return <div className="route-loading" role="status" aria-label="Loading page"><span /><span /><span /></div>;
}
