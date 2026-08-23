export type InputComposerProps = {
  busy: boolean;
  onAdd: (links: string[], files: File[]) => Promise<void>;
};
