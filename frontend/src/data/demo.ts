export type MemberStatus = "active" | "expiring" | "grace" | "expired" | "frozen" | "stopped";

export type Member = {
  id: string;
  name: string;
  email: string;
  phone: string;
  goal: string;
  plan: string;
  status: MemberStatus;
  visits: number;
  lastVisit: string;
  renewal: string;
  risk: "high" | "medium" | "low";
  color: string;
};

export type Payment = {
  id: string;
  member: string;
  amount: number;
  method: "Cash" | "Card" | "Bank transfer" | "Online";
  date: string;
  status: "Paid" | "Due";
};

export type ClassSession = {
  id: string;
  name: string;
  trainer: string;
  time: string;
  capacity: number;
  booked: number;
  room: string;
};

export const initialMembers: Member[] = [
  { id: "IPF-1048", name: "Nimali Perera", email: "nimali.perera@mail.lk", phone: "+94 71 284 6138", goal: "Build strength", plan: "Monthly", status: "active", visits: 17, lastVisit: "Today, 7:12 AM", renewal: "Nov 18, 2026", risk: "low", color: "#b5f24a" },
  { id: "IPF-1032", name: "Kavindu Fernando", email: "kavindu.f@mail.lk", phone: "+94 77 395 2814", goal: "Lose weight", plan: "Quarterly", status: "active", visits: 12, lastVisit: "Yesterday, 6:04 PM", renewal: "Dec 03, 2026", risk: "low", color: "#d38c68" },
  { id: "IPF-1007", name: "Tharushi Jayasinghe", email: "tharushi.j@mail.lk", phone: "+94 76 417 2605", goal: "Get stronger", plan: "Yearly", status: "expiring", visits: 4, lastVisit: "5 days ago", renewal: "Oct 29, 2026", risk: "high", color: "#c8a8e9" },
  { id: "IPF-0986", name: "Ravindu de Silva", email: "ravindu.ds@mail.lk", phone: "+94 72 608 5713", goal: "General fitness", plan: "Monthly", status: "grace", visits: 8, lastVisit: "2 days ago", renewal: "Oct 17, 2026", risk: "medium", color: "#8aadd0" },
  { id: "IPF-0954", name: "Ayesha Wickramasinghe", email: "ayesha.w@mail.lk", phone: "+94 75 842 1930", goal: "Build muscle", plan: "Quarterly", status: "active", visits: 3, lastVisit: "8 days ago", renewal: "Jan 12, 2027", risk: "high", color: "#d897ad" },
  { id: "IPF-0918", name: "Isuru Bandara", email: "isuru.b@mail.lk", phone: "+94 70 356 9241", goal: "Endurance", plan: "Monthly", status: "active", visits: 14, lastVisit: "Today, 6:38 AM", renewal: "Nov 25, 2026", risk: "low", color: "#a5bd8c" },
  { id: "IPF-0841", name: "Sachini Gunawardena", email: "sachini.g@mail.lk", phone: "+94 78 254 7906", goal: "Tone up", plan: "Student", status: "active", visits: 2, lastVisit: "11 days ago", renewal: "Nov 02, 2026", risk: "high", color: "#dfba70" },
  { id: "IPF-0782", name: "Dilan Samaraweera", email: "dilan.s@mail.lk", phone: "+94 74 679 3821", goal: "General fitness", plan: "Monthly", status: "expired", visits: 6, lastVisit: "Sep 18, 2026", renewal: "Oct 01, 2026", risk: "medium", color: "#9eabbe" },
  { id: "IPF-0725", name: "Minoli Rodrigo", email: "minoli.r@mail.lk", phone: "+94 77 520 1468", goal: "Strength & mobility", plan: "Yearly", status: "frozen", visits: 5, lastVisit: "Oct 08, 2026", renewal: "Nov 22, 2026", risk: "low", color: "#a9b88f" },
  { id: "IPF-0673", name: "Ashen Jayawardene", email: "ashen.j@mail.lk", phone: "+94 71 748 3029", goal: "Fat loss", plan: "Monthly", status: "stopped", visits: 1, lastVisit: "Aug 04, 2026", renewal: "Sep 04, 2026", risk: "medium", color: "#d19a7c" },
];

export const initialPayments: Payment[] = [
  { id: "INV-0261", member: "Nimali Perera", amount: 5000, method: "Cash", date: "Today, 9:18 AM", status: "Paid" },
  { id: "INV-0260", member: "Kavindu Fernando", amount: 13500, method: "Card", date: "Today, 8:42 AM", status: "Paid" },
  { id: "INV-0259", member: "Ayesha Wickramasinghe", amount: 5000, method: "Bank transfer", date: "Yesterday", status: "Due" },
  { id: "INV-0258", member: "Isuru Bandara", amount: 800, method: "Cash", date: "Yesterday", status: "Paid" },
];

export const initialClasses: ClassSession[] = [
  { id: "CLS-01", name: "HIIT Circuit", trainer: "Kasun Silva", time: "06:30 AM", capacity: 18, booked: 14, room: "Studio A" },
  { id: "CLS-02", name: "Morning Yoga", trainer: "Maya de Alwis", time: "08:00 AM", capacity: 14, booked: 11, room: "Studio B" },
  { id: "CLS-03", name: "Strength Lab", trainer: "Dinesh Herath", time: "05:30 PM", capacity: 16, booked: 15, room: "Main floor" },
  { id: "CLS-04", name: "Zumba", trainer: "Maya de Alwis", time: "06:30 PM", capacity: 20, booked: 17, room: "Studio A" },
  { id: "CLS-05", name: "Boxing Basics", trainer: "Kasun Silva", time: "07:30 PM", capacity: 12, booked: 8, room: "Studio C" },
];

export const chartData = [
  { day: "Mon", visits: 208, revenue: 68400 },
  { day: "Tue", visits: 246, revenue: 79200 },
  { day: "Wed", visits: 193, revenue: 71800 },
  { day: "Thu", visits: 274, revenue: 86600 },
  { day: "Fri", visits: 232, revenue: 80500 },
  { day: "Sat", visits: 305, revenue: 112400 },
  { day: "Sun", visits: 156, revenue: 62400 },
];

export const memberFullName = (id: string) =>
  initialMembers.find((member) => member.id === id)?.name ?? "New member";

export const money = (amount: number) =>
  new Intl.NumberFormat("en-LK", {
    style: "currency",
    currency: "LKR",
    maximumFractionDigits: 0,
  }).format(amount);
