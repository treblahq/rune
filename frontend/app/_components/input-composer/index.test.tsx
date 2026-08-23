import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { InputComposer } from ".";

describe("InputComposer", () => {
  it("adds several pasted links as one batch", async () => {
    const onAdd = vi.fn().mockResolvedValue(undefined);
    render(<InputComposer busy={false} onAdd={onAdd} />);

    await userEvent.type(
      screen.getByLabelText("Links de vídeo ou áudio"),
      "https://example.com/a{enter}https://example.com/b",
    );
    await userEvent.click(screen.getByRole("button", { name: "Adicionar à fila" }));

    expect(onAdd).toHaveBeenCalledWith(
      ["https://example.com/a", "https://example.com/b"],
      [],
    );
  });

  it("keeps the primary action disabled while there is no input", () => {
    render(<InputComposer busy={false} onAdd={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Adicionar à fila" })).toBeDisabled();
  });
});
