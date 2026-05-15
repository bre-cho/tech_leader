import type { ReactNode } from "react";

type PipelineShellProps = {
  children: ReactNode;
};

export function PipelineShell({ children }: PipelineShellProps) {
  return <div className="pipeline-shell">{children}</div>;
}
