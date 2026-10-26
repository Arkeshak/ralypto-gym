import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  initialClasses,
  initialMembers,
  initialPayments,
  type ClassSession,
  type Member,
  type Payment,
} from "../data/demo";

type Role = "Owner" | "Manager" | "Front desk" | "Trainer";
type Theme = "dark" | "light";
export type GymPlan = "Basic" | "Standard" | "Premium";

type GymStore = {
  members: Member[];
  payments: Payment[];
  classes: ClassSession[];
  role: Role;
  theme: Theme;
  plan: GymPlan;
  locale: "en" | "si" | "ta";
  checkedInIds: string[];
  setRole: (role: Role) => void;
  setTheme: (theme: Theme) => void;
  setPlan: (plan: GymPlan) => void;
  setLocale: (locale: "en" | "si" | "ta") => void;
  addMember: (member: Pick<Member, "name" | "phone" | "email" | "goal" | "plan">) => void;
  checkIn: (memberId: string) => boolean;
  recordPayment: (memberName: string, amount: number, method: Payment["method"]) => void;
  markDuePaid: (paymentId: string) => void;
  bookClass: (sessionId: string) => void;
  approvePlan: (memberId: string) => void;
  resetDemo: () => void;
};

const startingState = {
  members: initialMembers,
  payments: initialPayments,
  classes: initialClasses,
  role: "Owner" as const,
  theme: "dark" as const,
  plan: "Premium" as GymPlan,
  locale: "en" as const,
  checkedInIds: [] as string[],
};

export const useGymStore = create<GymStore>()(
  persist(
    (set, get) => ({
      ...startingState,
      setRole: (role) => set({ role }),
      setTheme: (theme) => set({ theme }),
      setPlan: (plan) => set({ plan }),
      setLocale: (locale) => set({ locale }),
      addMember: (form) => {
        const nextNumber = 1100 + get().members.length;
        const member: Member = {
          ...form,
          id: `IPF-${nextNumber}`,
          status: "active",
          visits: 0,
          lastVisit: "Not checked in",
          renewal: "Nov 25, 2026",
          risk: "low",
          color: "#b5f24a",
        };
        set((state) => ({ members: [member, ...state.members] }));
      },
      checkIn: (memberId) => {
        const member = get().members.find((entry) => entry.id === memberId);
        if (!member || member.status !== "active" || get().checkedInIds.includes(memberId)) {
          return false;
        }
        set((state) => ({
          checkedInIds: [...state.checkedInIds, memberId],
          members: state.members.map((entry) =>
            entry.id === memberId
              ? { ...entry, visits: entry.visits + 1, lastVisit: "Just now" }
              : entry,
          ),
        }));
        return true;
      },
      recordPayment: (memberName, amount, method) =>
        set((state) => ({
          payments: [
            {
              id: `INV-${262 + state.payments.length}`,
              member: memberName,
              amount,
              method,
              date: "Just now",
              status: "Paid",
            },
            ...state.payments,
          ],
        })),
      markDuePaid: (paymentId) =>
        set((state) => ({
          payments: state.payments.map((payment) =>
            payment.id === paymentId ? { ...payment, status: "Paid" } : payment,
          ),
        })),
      bookClass: (sessionId) =>
        set((state) => ({
          classes: state.classes.map((session) =>
            session.id === sessionId && session.booked < session.capacity
              ? { ...session, booked: session.booked + 1 }
              : session,
          ),
        })),
      approvePlan: (memberId) =>
        set((state) => ({
          members: state.members.map((member) =>
            member.id === memberId ? { ...member, risk: "low" } : member,
          ),
        })),
      resetDemo: () => set(startingState),
    }),
    {
      name: "ralypto-gym-demo",
      partialize: (state) => ({
        members: state.members,
        payments: state.payments,
        classes: state.classes,
        role: state.role,
        theme: state.theme,
        plan: state.plan,
        locale: state.locale,
        checkedInIds: state.checkedInIds,
      }),
    },
  ),
);
