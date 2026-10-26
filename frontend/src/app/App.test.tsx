import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import App from "./App";
import { useGymStore } from "./use-gym-store";

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("Ralypto Gym frontend demo", () => {
  beforeEach(() => {
    window.localStorage.clear();
    useGymStore.getState().resetDemo();
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it("opens the owner dashboard with demo data", async () => {
    renderAt("/app/dashboard");

    expect(await screen.findByRole("heading", { name: "Good morning, Aru." }, { timeout: 8000 })).toBeInTheDocument();
    expect(screen.getByText("Active members")).toBeInTheDocument();
    expect(screen.getByText("Members to check in on")).toBeInTheDocument();
  });

  it("checks in an active member and blocks an expired member", async () => {
    const { unmount } = renderAt("/app/check-in");

    fireEvent.change(await screen.findByLabelText("Find a member"), { target: { value: "IPF-1048" } });
    fireEvent.click(screen.getByRole("button", { name: /check in/i }));
    expect(await screen.findByText("Membership verified. Enjoy your session.")).toBeInTheDocument();
    unmount();
    window.localStorage.clear();
    useGymStore.getState().resetDemo();

    renderAt("/app/check-in");
    fireEvent.change(await screen.findByLabelText("Find a member"), { target: { value: "IPF-0782" } });
    fireEvent.click(screen.getByRole("button", { name: /check in/i }));
    expect(await screen.findByText(/membership needs attention/i)).toBeInTheDocument();
    expect(useGymStore.getState().checkedInIds).toHaveLength(0);
  });

  it("adds a member after validating the required details", async () => {
    renderAt("/app/members");
    fireEvent.click(await screen.findByRole("button", { name: /add member/i }));
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Sanjaya Perera" } });
    fireEvent.change(screen.getByLabelText("Phone number"), { target: { value: "+94 77 111 2233" } });
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: /add member/i }));

    expect(await screen.findByText("Sanjaya Perera")).toBeInTheDocument();
    expect(useGymStore.getState().members).toHaveLength(11);
  });

  it("waits for the member to confirm an assistant booking", async () => {
    renderAt("/m/assistant");

    fireEvent.click(await screen.findByRole("button", { name: /book zumba tomorrow/i }));
    expect(screen.getByText(/want me to book one spot/i)).toBeInTheDocument();
    expect(useGymStore.getState().classes.find((session) => session.id === "CLS-04")?.booked).toBe(17);
    fireEvent.click(screen.getByRole("button", { name: /confirm booking/i }));
    await waitFor(() => expect(useGymStore.getState().classes.find((session) => session.id === "CLS-04")?.booked).toBe(18));
  });

  it("filters navigation when switched to Front desk role", async () => {
    useGymStore.getState().setRole("Front desk");
    renderAt("/app/dashboard");

    expect(await screen.findByRole("heading", { name: "Good morning, Aru." }, { timeout: 8000 })).toBeInTheDocument();
    expect(screen.getAllByText("Overview").length).toBeGreaterThan(0);
    expect(screen.getByText("Check-in")).toBeInTheDocument();
    expect(screen.queryByText("AI insights")).not.toBeInTheDocument();
    expect(screen.queryByText("My plan")).not.toBeInTheDocument();
  });

  it("filters navigation when switched to Trainer role", async () => {
    useGymStore.getState().setRole("Trainer");
    renderAt("/app/dashboard");

    expect(await screen.findByRole("heading", { name: "Good morning, Aru." }, { timeout: 8000 })).toBeInTheDocument();
    expect(screen.getByText("Classes")).toBeInTheDocument();
    expect(screen.getByText("Workouts")).toBeInTheDocument();
    expect(screen.queryByText("Payments")).not.toBeInTheDocument();
    expect(screen.queryByText("Check-in")).not.toBeInTheDocument();
  });

  it("displays UpgradeCard for classes when on Basic plan", async () => {
    useGymStore.getState().setPlan("Basic");
    renderAt("/app/classes");

    expect(await screen.findByText(/Upgrade to unlock Classes & Bookings/i)).toBeInTheDocument();
    expect(screen.getByText(/available on the Standard tier and above/i)).toBeInTheDocument();
  });

  it("displays UpgradeCard for workouts when on Basic plan", async () => {
    useGymStore.getState().setPlan("Basic");
    renderAt("/app/workouts");

    expect(await screen.findByText(/Upgrade to unlock Workouts & Plans/i)).toBeInTheDocument();
  });

  it("displays UpgradeCard for AI Center when on Standard plan", async () => {
    useGymStore.getState().setPlan("Standard");
    renderAt("/app/ai");

    expect(await screen.findByText(/Upgrade to unlock AI Insights & Coach/i)).toBeInTheDocument();
    expect(screen.getByText(/available on the Premium tier and above/i)).toBeInTheDocument();
  });

  it("displays UpgradeCard for Member Mobile App when on Basic plan", async () => {
    useGymStore.getState().setPlan("Basic");
    renderAt("/m/home");

    expect(await screen.findByText(/Upgrade to unlock Member Mobile App/i)).toBeInTheDocument();
  });

  it("records a payment and stores it in gym store", () => {
    const initialCount = useGymStore.getState().payments.length;
    useGymStore.getState().recordPayment("Kavindu Fernando", 7500, "Cash");

    const updated = useGymStore.getState().payments;
    expect(updated).toHaveLength(initialCount + 1);
    expect(updated[0].member).toBe("Kavindu Fernando");
    expect(updated[0].amount).toBe(7500);
    expect(updated[0].status).toBe("Paid");
  });

  it("marks an outstanding payment due as paid", () => {
    const duePayment = useGymStore.getState().payments.find((p) => p.status === "Due");
    expect(duePayment).toBeDefined();

    useGymStore.getState().markDuePaid(duePayment!.id);
    const updated = useGymStore.getState().payments.find((p) => p.id === duePayment!.id);
    expect(updated?.status).toBe("Paid");
  });

  it("toggles and persists theme in store", () => {
    expect(useGymStore.getState().theme).toBe("dark");
    useGymStore.getState().setTheme("light");
    expect(useGymStore.getState().theme).toBe("light");
    useGymStore.getState().setTheme("dark");
    expect(useGymStore.getState().theme).toBe("dark");
  });

  it("switches language locale in store", () => {
    expect(useGymStore.getState().locale).toBe("en");
    useGymStore.getState().setLocale("si");
    expect(useGymStore.getState().locale).toBe("si");
    useGymStore.getState().setLocale("ta");
    expect(useGymStore.getState().locale).toBe("ta");
  });

  it("approves a workout plan for high risk member", () => {
    const member = useGymStore.getState().members.find((m) => m.risk === "high");
    expect(member).toBeDefined();

    useGymStore.getState().approvePlan(member!.id);
    const updated = useGymStore.getState().members.find((m) => m.id === member!.id);
    expect(updated?.risk).toBe("low");
  });

  it("responds to workout inquiry in member assistant", async () => {
    renderAt("/m/assistant");

    fireEvent.click(await screen.findByRole("button", { name: /what's today's workout/i }));
    expect(screen.getByText(/Today is strength foundations/i)).toBeInTheDocument();
  });

  it("responds to dues inquiry in member assistant", async () => {
    renderAt("/m/assistant");

    fireEvent.click(await screen.findByRole("button", { name: /check my dues/i }));
    expect(screen.getByText(/Your monthly membership is active and your next renewal is November 18/i)).toBeInTheDocument();
  });

  it("renders demo personas on the login page", async () => {
    renderAt("/login");

    expect(await screen.findByText("IRON PEAK FITNESS · CLIENT DEMO")).toBeInTheDocument();
    expect(screen.getByText("Gym Owner")).toBeInTheDocument();
    expect(screen.getByText("Club Manager")).toBeInTheDocument();
    expect(screen.getByText("Front Desk Staff")).toBeInTheDocument();
    expect(screen.getByText("Personal Trainer")).toBeInTheDocument();
    expect(screen.getByText("Member Mobile App")).toBeInTheDocument();
  });

  it("switches plan dynamically in subscription page", async () => {
    renderAt("/app/subscription");

    expect(await screen.findByText("ACTIVE PLAN")).toBeInTheDocument();
    const chooseBasic = screen.getByRole("button", { name: /switch to basic/i });
    fireEvent.click(chooseBasic);
    expect(useGymStore.getState().plan).toBe("Basic");
  });

  it("performs simulated QR scan in check-in page", async () => {
    renderAt("/app/check-in");

    const scanBtn = await screen.findByRole("button", { name: /scan member qr/i });
    fireEvent.click(scanBtn);
    expect(await screen.findByText(/Membership verified. Enjoy your session./i)).toBeInTheDocument();
    expect(useGymStore.getState().checkedInIds).toContain("IPF-1048");
  });
});

