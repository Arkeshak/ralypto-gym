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

    expect(await screen.findByRole("heading", { name: "Good morning, Aru." })).toBeInTheDocument();
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
});
